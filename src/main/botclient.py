import logging

from baseclient import BaseClient

class BotClient(BaseClient):
    def requestAction(self):
        logging.warning('bot should move, but don\'t know how')
