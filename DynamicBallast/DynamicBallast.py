import sys
import ac
import acsys
import time

appName = "Dynamic Ballast"
width, height = 400, 400 # width and height of the app's window

CALCULATION_INTERVAL = 10.0 # Seconds
POSTING_INTERVAL = 2.0 # Seconds

MAX_PENALTY_PROGRESS_DELTA = 0.05
PENALTY_BALLAST_MAX = 2000
PENALTY_RESTRICTOR_MAX = 100

NAME_TO_GRID_ID = {
    'Jesse': 0,
    'nikoj0': 1,
    'squeakymousetoy': 2,
    'bupu7': 
}

def acMain(ac_version):
    global appWindow, last_calculated, last_posted

    appWindow = ac.newApp(appName)
    ac.setTitle(appWindow, appName)
    ac.setSize(appWindow, width, height)

    last_calculated = time.clock()
    last_posted = time.clock()

    ac.sendChatMessage("/admin xxxxxxxx")

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
    global last_calculated, last_posted, msg_queue

    if (time.clock() - last_calculated) > CALCULATION_INTERVAL:
        last_calculated = time.clock()
        progresses, names = get_progresses_and_names()
        penalties = calculate_penalties(progresses)

        ac.console("Player progresses: {}".format(progresses))
        ac.console("Player penalties: {}".format(penalties))

        msg_queue = []
        for i, p in enumerate(penalties):
            bst = int(p*PENALTY_BALLAST_MAX)
            rst = int(p*PENALTY_RESTRICTOR_MAX)

            car_name = names[i]
            grid_id = NAME_TO_GRID_ID.get(car_name, "NA")

            msg_queue.append("/ballast {} {}".format(grid_id, bst))
            msg_queue.append("/restrictor {} {}".format(grid_id, rst))

    if (time.clock() - last_posted) > POSTING_INTERVAL:
        last_posted = time.clock()
        msg = msg_queue.pop()
        ac.console(msg)
        ac.sendChatMessage(msg)
