import sys
import ac
import acsys
import time


appName = "Dynamic Ballast"
width, height = 400, 400 # width and height of the app's window

UPDATE_INTERVAL = 10.0 # Seconds

def acMain(ac_version):
    global appWindow, last_updated

    appWindow = ac.newApp(appName)
    ac.setTitle(appWindow, appName)
    ac.setSize(appWindow, width, height)

    last_updated = time.clock()
    
    return appName


def calculate_progress_metrics():
    ncars = ac.getCarsCount()
    d = {}
    for i in range(ncars):
        lap = ac.getCarState(i, acsys.CS.LapCount)
        spline = ac.getCarState(i, acsys.CS.NormalizedSplinePosition)
        prg = lap + spline
        d[i] = prg
    return d

def acUpdate(deltaT):
    global last_updated

    if (time.clock() - last_updated) > UPDATE_INTERVAL:
        metrics = calculate_progress_metrics()
        ac.console("Player progress: {}".format(metrics))

        last_updated = time.clock()