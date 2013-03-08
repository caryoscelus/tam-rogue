from event import Event

import logging

def info(s):
    logging.info(s)
    logString(s)

def logString(s):
    eventLog.append(s)

def logEvent(action, args, result):
    event = Event(action, args, result)
    # TODO: use events again?
    #eventLog.append(event)

# TODO: make it fancy and useful
# or maybe just kill it?
def processAction(action, args):
    logEvent(action, args, None)

eventLog = []
