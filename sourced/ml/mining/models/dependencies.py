from modelforge import (
    assemble_sparse_matrix,
    disassemble_sparse_matrix,
    merge_strings,
    Model,
    register_model,
    split_strings,
)
from sourced.ml.core.models.license import DEFAULT_LICENSE


@register_model
class Dependencies(Model):
    """
    Occurence matrix between files and dependencies.
    """

    NAME = "deps"
    VENDOR = "source{d}"
    DESCRIPTION = (
        "Binary cooccurrence matrix between dependencies and files,"
        "as well as the mapping from file names to languages."
    )
    LICENSE = DEFAULT_LICENSE

    def construct(self, matrix, files, deps, ind_to_langs, ind_to_repos):
        self._matrix = matrix
        self._files = files
        self._deps = deps
        self._ind_to_langs = ind_to_langs
        self._ind_to_repos = ind_to_repos
        return self

    def _load_tree(self, tree):
        matrix = assemble_sparse_matrix(tree["matrix"])
        files = split_strings(tree["files"])
        deps = split_strings(tree["deps"])
        ind_to_langs = {
            ind: lang for ind, lang in enumerate(split_strings(tree["ind_to_langs"]))
        }
        ind_to_repos = {
            ind: repo for ind, repo in enumerate(split_strings(tree["ind_to_repos"]))
        }
        self.construct(matrix, files, deps, ind_to_langs, ind_to_repos)

    def _generate_tree(self):
        return {
            "matrix": disassemble_sparse_matrix(self._matrix),
            "files": merge_strings(self._files),
            "deps": merge_strings(self._deps),
            "ind_to_langs": merge_strings(
                [self._ind_to_langs[ind] for ind in range(len(self._files))]
            ),
            "ind_to_repos": merge_strings(
                [self._ind_to_repos[ind] for ind in range(len(self._files))]
            ),
        }

    def dump(self):
        msg = "Total number of files: %d\n" % len(self._files)
        msg += "Total number of repos: %d\n" % len(set(self._ind_to_repos.values()))
        msg += "Total number of dependencies: %d\n" % len(self._deps)
        msg += "Total number of non-zero entries: %d\n" % len(self._matrix.getnnz())
        return msg

    @property
    def files(self, lang):
        """
        Returns the files in the order which corresponds to the matrix's rows.
        """
        return self._files

    @property
    def deps(self):
        """
        Returns the dependencies in the order which corresponds to the matrix's cols.
        """
        return self._deps

    @property
    def matrix(self, lang):
        """
        Returns the sparse co-occurrence matrix.
        """
        return self._matrix

    @property
    def inds_to_lang(self):
        """
        Returns the mapping from file index to language.
        """
        return self._ind_to_langs

    @property
    def inds_to_repo(self):
        """
        Returns the mapping from file index to repo.
        """
        return self._ind_to_repos
