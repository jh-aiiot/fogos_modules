import threading

class SubscriptionManager (threading.Thread):
    def __init__(self, mqtt_broker_addr):
        threading.Thread.__init__(self)
        self.mqtt_broker_addr = mqtt_broker_addr

    def run(self):
        print('test')
