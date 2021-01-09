import sys
import ac
import acsys
import time

appName = "Dynamic Ballast"
width, height = 400, 400 # width and height of the app's window

UPDATE_INTERVAL = 5.0 # Seconds
MAX_PENALTY_PROGRESS_DELTA = 0.5
PENALTY_BALLAST_MAX = 500
PENALTY_RESTRICTOR_MAX = 100


def acMain(ac_version):
    global appWindow, last_updated

    appWindow = ac.newApp(appName)
    ac.setTitle(appWindow, appName)
    ac.setSize(appWindow, width, height)

    last_updated = time.clock()
    
    return appName


def calculate_progresses():
    ncars = ac.getCarsCount()
    d = []
    for i in range(ncars):
        lap = ac.getCarState(i, acsys.CS.LapCount)
        spline = ac.getCarState(i, acsys.CS.NormalizedSplinePosition)
        prg = lap + spline
        d.append(prg)
    return d


def calculate_penalties(progresses):
    prog_min = min(progresses)
    prog_max = max(progresses)

    advantages = [p - prog_min for p in progresses]
    scale = max(0.001, prog_max - prog_min)
    dampen = min(1.0, (prog_max - prog_min) / MAX_PENALTY_PROGRESS_DELTA)

    penalties = [dampen * (a/scale) for a in advantages]
    return penalties


def acUpdate(deltaT):
    global last_updated

    if (time.clock() - last_updated) > UPDATE_INTERVAL:
        progresses = calculate_progresses()
        penalties = calculate_penalties(progresses)

        ac.concole("")
        ac.console("Player progresses: {}".format(progresses))
        ac.console("Player penalties: {}".format(penalties))

        last_updated = time.clock()