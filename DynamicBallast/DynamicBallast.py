import sys
import ac
import acsys
import time

appName = "Dynamic Ballast"
width, height = 400, 400 # width and height of the app's window

UPDATE_INTERVAL = 5.0 # Seconds

def acMain(ac_version):
    global appWindow, last_updated

    appWindow = ac.newApp(appName)
    ac.setTitle(appWindow, appName)
    ac.setSize(appWindow, width, height)

    ac.console("Dynamic Ballast running")

    last_updated = time.clock()

    return appName


def acUpdate(deltaT):
    global last_updated

    if (time.clock() - last_updated) > UPDATE_INTERVAL:
        msg = "last updated {} seconds ago".format(last_updated)
        ac.sendChatMessage(msg)
        ac.console(msg)

        last_updated = time.clock()