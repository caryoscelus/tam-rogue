import time

class Sleeping:
    SLEEP_TIME = 1.0/64
    
    def sleep(self, amount = 1):
        time.sleep(self.SLEEP_TIME*amount)
