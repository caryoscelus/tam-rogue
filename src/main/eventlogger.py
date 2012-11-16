import logging

def processAction(action, args):
    actionList.append(action)
    text = action.name
    textLog.append(text)
    logging.debug(text)

actionList = []
textLog = []
