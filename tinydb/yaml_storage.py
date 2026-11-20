"""YAML storage. Imports PyYAML only when a database is read or written."""

from tinydb.storages import Storage


class YAMLStorage(Storage):
    def __init__(self, path: str, *args, **kwargs):
        self.path = path

    def read(self):
        import yaml
        with open(self.path, encoding="utf-8") as handle:
            text = handle.read()
        if not text.strip():
            return None
        return yaml.safe_load(text)

    def write(self, data) -> None:
        import yaml
        with open(self.path, "w", encoding="utf-8") as handle:
            yaml.safe_dump(data, handle)
