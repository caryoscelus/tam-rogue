import logging

# TODO: make it fancy and useful
def processAction(action, args):
    actionList.append(action)
    text = action.name
    textLog.append(text)
    logging.debug(text)

actionList = []
textLog = []
