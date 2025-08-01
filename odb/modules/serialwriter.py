from odb.modules import Module
import json

class SerialWriter(Module):

    name = 'SerialWriter'

    def during_bootup(self, *args, **kwargs):
        self.ready = True


    def before_handle(self, data=None):
        return None

    def handle(self, data=None):
        return None


    def after_handle(self, data=None):
        print(json.dumps(data))
        return None

