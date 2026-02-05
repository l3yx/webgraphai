from typing import Any


class GlobalCache:
    _instance = None
    _max_size = 30

    def __new__(cls) -> 'GlobalCache':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._cache = {}
            cls._instance._order = []
        return cls._instance

    def set(self, key: str, value: Any) -> None:
        if key in self._cache:
            self._order.remove(key)
        else:
            if len(self._cache) >= self._max_size:
                oldest = self._order.pop(0)
                del self._cache[oldest]

        self._cache[key] = value
        self._order.append(key)

    def get(self, key: str) -> Any:
        if key not in self._cache:
            raise KeyError(f"Key '{key}' not found in cache.")
        return self._cache.get(key)

    def delete(self, key: str) -> None:
        if key in self._cache:
            del self._cache[key]
            self._order.remove(key)

    def clear(self) -> None:
        self._cache.clear()
        self._order.clear()


cache = GlobalCache()

if __name__ == "__main__":
    cache.set("a", 1)
    print(cache.get("a"))

    print(cache.get("b"))
