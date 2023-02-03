def singleton(cls):
    _instances = {}
    def getinstance():
        if cls not in _instances:
            _instances[cls] = cls()
        return _instances[cls]
    return getinstance