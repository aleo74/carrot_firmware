class InvalidExtensionEnvironment(Exception):
    pass


class Extension:
    _enabled = True

    def enable(self, keyboard):
        self._enabled = True

        self.on_runtime_enable(keyboard)

    def disable(self, keyboard):
        self._enabled = False

        self.on_runtime_disable(keyboard)

    def before_handle(self, data=None):
        if data is None:
            data = []
        return data

    def handle(self, data=None):
        if data is None:
            data = []
        return data

    def after_handle(self, data=None):
        return None

    def during_bootup(self, keyboard):
        raise NotImplementedError

    def on_powersave_enable(self, keyboard):
        raise NotImplementedError

    def on_powersave_disable(self, keyboard):
        raise NotImplementedError