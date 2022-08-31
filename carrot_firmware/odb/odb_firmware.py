

class Odb:

    modules = []
    extensions = []
    start = False
    data_from_module = ''


    def _init(self):
        i = 0
        while not self.start:
            for x in self.modules:
                try:
                    if not x.ready:
                        x.during_bootup()
                        if x.ready:
                            i = i + 1 # this is a quick fix
                        else:
                            i = 0
                        if i == len(self.modules):
                            self.start = True
                except Exception as err:
                    print('fail to load module', err, x)


    def go(self):
        self._init()
        while True:
            self._main_loop()

    def _main_loop(self):
        data = self.before_handle(self.data_from_module)
        data = self.handle(data)
        self.after_handle(data)

    def before_handle(self, data_from_module):
        data = {}
        for x in self.modules:
            dico = x.before_handle(data_from_module)
            data[x.name] = dico
        return data


    def handle(self, data_received):
        data = {}
        for x in self.modules:
            dico = x.handle(data_received)
            data[x.name] = dico
        return data


    def after_handle(self, data_received):
        self.data_from_module = {}
        for x in self.modules:
            dico = x.after_handle(data_received)
            if dico:
                self.data_from_module = dico

