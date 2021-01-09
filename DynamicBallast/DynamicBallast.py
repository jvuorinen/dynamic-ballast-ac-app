import sys
import ac
import acsys
import time

appName = "Dynamic Ballast"
width, height = 400, 400 # width and height of the app's window

UPDATE_INTERVAL = 1.0 # Seconds
MAX_PENALTY_PROGRESS_DELTA = 0.5
PENALTY_BALLAST_MAX = 500
PENALTY_RESTRICTOR_MAX = 100

NAME_TO_GRID_ID = {
    'jesse': 0,
    'niko': 1,
    'jne': 2,
    'ym': 3
}


def acMain(ac_version):
    global appWindow, last_updated

    appWindow = ac.newApp(appName)
    ac.setTitle(appWindow, appName)
    ac.setSize(appWindow, width, height)

    last_updated = time.clock()
    
    return appName


def get_progresses_and_names():
    ncars = ac.getCarsCount()
    progs = []
    names = []
    for i in range(ncars):
        if ac.isConnected(i):
            lap = ac.getCarState(i, acsys.CS.LapCount)
            spline = ac.getCarState(i, acsys.CS.NormalizedSplinePosition)
            prg = lap + spline
            progs.append(prg)
            names.append(ac.getDriverName(i))
    return progs, names


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
        progresses, names = get_progresses_and_names()
        penalties = calculate_penalties(progresses)

        ac.console("")
        ac.console("Player progresses: {}".format(progresses))
        ac.console("Player penalties: {}".format(penalties))

        for i, p in enumerate(penalties):
            bst = int(p*PENALTY_BALLAST_MAX)
            rst = int(p*PENALTY_RESTRICTOR_MAX)

            car_name = names[i]
            grid_id = NAME_TO_GRID_ID[car_name]

            msg_bst = "/ballast {} {}".format(grid_id, bst)
            msg_rst = "/restrictor {} {}".format(grid_id, rst)

            ac.console(msg_bst)
            ac.console(msg_rst)
            ac.sendChatMessage(msg_bst)
            ac.sendChatMessage(msg_rst)
            
        last_updated = time.clock()