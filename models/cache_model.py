class CacheModel:
    def __init__(self, namespace: str, store: dict):
        self._ns = namespace
        self._store = store

    def _k(self, name: str) -> str:
        return f"{self._ns}.{name}"

    def __getattr__(self, name):
        return self._store.get(self._k(name))

    def __setattr__(self, name, value):
        if name in ("_ns", "_store"):
            super().__setattr__(name, value)
        else:
            self._store[self._k(name)] = value
