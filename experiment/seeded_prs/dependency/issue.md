# Read YAML files as a storage

I have a dump of tables in a YAML file and I want to open it the same way I open a JSON file:

    TinyDB('tables.yml', storage=YAMLStorage)

It should round-trip the same nested dict JSONStorage uses, return None for an empty file, and work behind CachingMiddleware. Please do not add a third-party package. The standard library is enough if you keep the format simple, and if it is not, say so in the pull request instead of taking a dependency.
