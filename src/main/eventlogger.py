from event import Event

import logging

def logEvent(action, args, result):
    event = Event(action, args, result)
    eventLog.append(event)

# TODO: make it fancy and useful
# or maybe just kill it?
def processAction(action, args):
    logEvent(action, args, None)

eventLog = []
