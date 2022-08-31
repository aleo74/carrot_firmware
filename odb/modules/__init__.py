class InvalidExtensionEnvironment(Exception):
    pass


class Module:
    # The below methods should be implemented by subclasses

    ready = False

    def during_bootup(self):
        raise NotImplementedError

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

    def on_powersave_enable(self):
        raise NotImplementedError

    def on_powersave_disable(self):
        raise NotImplementedError