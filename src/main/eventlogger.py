from event import Event

import logging

def logEvent(action, args, result):
    event = Event(action, args, result)
    eventLog.append(event)

# TODO: make it fancy and useful
# or maybe just kill it?
def processAction(action, args):
    actionList.append(action)
    text = action.name
    textLog.append(text)
    logging.debug(text)

actionList = []
textLog = []
eventLog = []
