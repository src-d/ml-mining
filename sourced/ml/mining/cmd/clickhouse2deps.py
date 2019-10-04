import logging
from pathlib import Path

from clickhouse_driver import Client
import jinja2
from scipy.sparse import coo_matrix
import yaml

from sourced.ml.mining.models import Dependencies


QUERY_TEMPLATE = "clickhouse2deps.sql.jinja2"
QUERY_ARGS = "clickhouse2deps.yaml"
CLICKHOUSE_LANGS = [
    "cpp",
    "csharp",
    "go",
    "java",
    "javascript",
    "php",
    "python",
]  # TODO(r0mainK): add ruby
MAX_BLOCK_SIZE = 1000000


def clickhouse2deps(args):
    """
    Extract dependencies from UASTs in a Clickhouse DB.
    """
    log = logging.getLogger("clickhouse2deps")
    if not args.output_path.suffix == ".asdf":
        args.output_path = args.output_path.with_suffix(".asdf")
    if args.output_path.exists():
        if not args.force:
            log.error(
                "%s already exists, aborting (use -f/--force to overwrite)",
                args.output_path,
            )
            raise FileExistsError
        log.warn("%s already exists, overwritten", args.output_path)
        args.output_path.unlink()
    log.info("Loading the query template ...")
    root = Path(__file__).parent
    template_loader = jinja2.FileSystemLoader(str(root))
    env = jinja2.Environment(keep_trailing_newline=False)
    template = template_loader.load(env, name=QUERY_TEMPLATE)
    log.info("Loading the query args ...")
    with (root / QUERY_ARGS).open() as fin:
        query_args = yaml.load(fin, Loader=yaml.BaseLoader)
    client = Client(
        user=args.user,
        password=args.password,
        host=args.host,
        port=args.port,
        database=args.database,
    )
    files, deps, ind_files, ind_deps = [], [], [], []
    ind_to_langs, ind_to_repos, file_to_inds, dep_to_inds = {}, {}, {}, {}
    for lang in args.langs:
        log.info("Extracting %s dependencies...", lang)
        rows = client.execute_iter(
            template.render(lang=lang, table=args.table, query_args=query_args[lang]),
            settings={"max_block_size": MAX_BLOCK_SIZE},
        )
        num_rows, num_files, num_deps = 0, 0, 0
        for row in rows:
            row = [
                e.decode("utf-8", errors="ignore") if not isinstance(e, str) else e
                for e in row
            ]
            num_rows += 1
            repo, file_path, dep = row
            lang_file = ":".join([lang, repo, file_path])
            lang_dep = ":".join([lang, dep])
            if lang_file not in file_to_inds:
                num_files += 1
                file_to_inds[lang_file] = len(file_to_inds)
                files.append(file_path)
            ind_file = file_to_inds[lang_file]
            ind_to_langs[ind_file] = lang
            ind_to_repos[ind_file] = repo
            ind_files.append(ind_file)
            if lang_dep not in dep_to_inds:
                num_deps += 1
                dep_to_inds[lang_dep] = len(dep_to_inds)
                deps.append(dep)
            ind_deps.append(dep_to_inds[lang_dep])
        log.info(
            "Finished with %s, retrieved %d rows with %d distinct dependencies in %d files",
            lang,
            num_rows,
            num_deps,
            num_files,
        )
    log.info(
        "Done, retrieved %d rows with %d distinct dependencies in %d files and %d repos",
        len(ind_files),
        len(deps),
        len(files),
        len(set(ind_to_repos.values())),
    )
    log.info("Creating the sparse matrix ...")
    matrix = coo_matrix(([True] * len(ind_files), (ind_files, ind_deps)), dtype=bool)
    log.info("Creating the dependencies model ...")
    model = Dependencies(log_level=args.log_level).construct(
        matrix, files, deps, ind_to_langs, ind_to_repos
    )
    model.save(args.output_path, series="deps")
    log.info("Saved model to %s" % args.output_path)
