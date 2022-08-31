from odb.modules import Module

class Servo(Module):

    name = 'Servo'
    state = 'Not deployed'

    def during_bootup(self, *args, **kwargs):
        self.ready = True

    def before_handle(self, data=None):
        if self.name in data:
            if data[self.name] == "deploy":
                self.state = "deployed"
        return []


    def handle(self, data=None):
        # {'Servo': [{'data': []}], 'nrf24': [{'data': {'received': {'Servo': 'deploy'}}}], 'mpu': [{'data': 1577839151}]}
        if self.name in data['nrf24']['received']:
            if data['nrf24']['received']['Servo'] == 'deploy':
                self.state = 'deploy'
        return {'state' : self.state}
