from modelforge import merge_strings, Model, register_model, split_strings
from sourced.ml.core.models.license import DEFAULT_LICENSE


@register_model
class StandardLibraries(Model):
    """
    List of standard library contents for each Babelfish language.
    """

    NAME = "stdlib"
    VENDOR = "source{d}"
    DESCRIPTION = (
        "The list of standard library names for C++, C#, Go, Java, JavaSript, PHP, "
        "Python and Ruby. The language versions and other metadata are stored when "
        "found. The data is collected as exhaustively as possible."
    )
    LICENSE = DEFAULT_LICENSE

    def construct(self, library_names, library_metadata):
        self._library_names = library_names
        self._library_metadata = library_metadata
        self._langs = [l for l in sorted(library_names)]
        return self

    def _load_tree(self, tree):
        library_names = {}
        library_metadata = {lang: {} for lang in tree["langs"]}
        for lang in tree["langs"]:
            library_names[lang] = set(split_strings(tree[lang]["library_names"]))
            for meta, libs in tree[lang]["library_metadata"].items():
                library_metadata[lang][meta] = set(split_strings(libs))
        self.construct(library_names, library_metadata)

    def _generate_tree(self):
        tree = {"langs": self._langs}
        for lang, library_names in self._library_names.items():
            tree[lang] = {"library_names": merge_strings(sorted(library_names))}
            tree[lang]["library_metadata"] = {}
            for meta, libs in self._library_metadata[lang].items():
                tree[lang]["library_metadata"][meta] = merge_strings(sorted(libs))
        return tree

    def dump(self):
        msg = []
        for lang in self._langs:
            msg.append("%s:" % lang)
            msg.append("\t%d distinct library names" % len(self._library_names[lang]))
            msg.append("\t%d distinct categories" % len(self._library_metadata[lang]))
        return "\n".join(msg)

    @property
    def langs(self):
        return self._langs

    def get_library_names(self, lang):
        return self._library_names.get(lang, [])

    def get_library_metadata(self, lang):
        return self._library_metadata.get(lang, {})

    def get_library(self, lang, library):
        return [
            meta
            for meta, libs in self.get_library_metadata(lang).items()
            if library in libs
        ]
