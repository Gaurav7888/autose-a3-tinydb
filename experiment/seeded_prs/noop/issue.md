# A JSON file that only contains a newline crashes on open

If the database file is empty, TinyDB opens it as an empty database. If an editor saved a single newline into that file, TinyDB raises JSONDecodeError instead.

A file whose contents are empty or only whitespace should open as an empty database, the same as a zero-byte file. A file with a real JSON error, such as a single `{`, should still raise.

Inserting a document after opening a whitespace-only file should work.
