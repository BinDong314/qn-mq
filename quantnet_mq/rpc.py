class RPCHandler:
    def __init__(self, cmd: str, cb, classpath):
        self._cmd = cmd
        self._cb = cb
        self._classpath = classpath

    @property
    def cmd(self):
        return self._cmd

    @property
    def cb(self):
        return self._cb

    @property
    def classpath(self):
        return self._classpath

    def handle(self, instance):
        return self._cb(instance)
