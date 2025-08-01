

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
                    # FIXME : Si le module GPS est pas renseigné en dernier, cette partie du code devient non fonctionnel
                    if not x.ready:
                        x.during_bootup()
                        if x.ready:
                            i = i + 1
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
            if dico is None:  # ← on ignore None
                continue
            data[x.name] = dico
        return data


    def handle(self, data_received):
        data = dict(data_received)
        module_names = {m.name for m in self.modules}

        for x in self.modules:
            dico = x.handle(data)
            if dico is None or dico is data:
                continue
            data[x.name] = dico
            if isinstance(dico, dict):
                safe = {k: v for k, v in dico.items() if k not in module_names}
                data.update(safe)
        return data


    def after_handle(self, data_received):
        self.data_from_module = {}
        for x in self.modules:
            dico = x.after_handle(data_received)
            if dico:
                self.data_from_module = dico

