import sys
import ac
import acsys
import time

from config import GRID_IDS, ADMIN_PW

appName = "Dynamic Ballast"
width, height = 400, 600 # width and height of the app's window


def acMain(ac_version):
    global appWindow, last_calculated, last_posted

    appWindow = ac.newApp(appName)
    ac.setTitle(appWindow, appName)
    ac.setSize(appWindow, width, height)

    last_calculated = time.clock()
    last_posted = time.clock()

    create_ui_components()

    ac.sendChatMessage("/admin {}".format(ADMIN_PW))

    return appName


def create_ui_components():
    global appWindow
    global spinner_ballast, spinner_restrictor, spinner_smoothing, spinner_calculation_interval, spinner_posting_interval
    global label_names, label_track_progress, label_penalties, label_last_message

    x_margin = 10
    y_margin = 80
    spacing = 16

    # Spinners
    spinner_ballast = ac.addSpinner(appWindow, "Max. ballast penalty (kg)")
    ac.setRange(spinner_ballast, 0, 2000)
    ac.setStep(spinner_ballast, 100)
    ac.setValue(spinner_ballast, 1000)

    spinner_restrictor = ac.addSpinner(appWindow, "Max. restrictor penalty (pct.)")
    ac.setRange(spinner_restrictor, 0, 100)
    ac.setStep(spinner_restrictor, 5)
    ac.setValue(spinner_restrictor, 90)

    spinner_smoothing = ac.addSpinner(appWindow, "Smoothing (pct. of track)")
    ac.setRange(spinner_smoothing, 0, 100)
    ac.setStep(spinner_smoothing, 5)
    ac.setValue(spinner_smoothing, 20)
    
    spinner_calculation_interval = ac.addSpinner(appWindow, "Calculation interval (ms)")
    ac.setRange(spinner_calculation_interval, 500, 20000)
    ac.setStep(spinner_calculation_interval, 10000)
    ac.setValue(spinner_calculation_interval, 5000)

    spinner_posting_interval = ac.addSpinner(appWindow, "Posting interval (ms)")
    ac.setRange(spinner_posting_interval, 200, 2000)
    ac.setStep(spinner_posting_interval, 100)
    ac.setValue(spinner_posting_interval, 1000)


    # Text output
    label_names = ac.addLabel(appWindow, "Driver names:")
    ac.setFontSize(label_names, 10)

    label_track_progress = ac.addLabel(appWindow, "Track progresses:")
    ac.setFontSize(label_track_progress, 10)

    label_penalties = ac.addLabel(appWindow, "Penalty percentages:")
    ac.setFontSize(label_penalties, 10)

    label_last_message = ac.addLabel(appWindow, "Last message posted:")
    ac.setFontSize(label_last_message, 10)


    # Component positions
    ac.setPosition(spinner_ballast, x_margin, y_margin + (spacing * 0))
    ac.setPosition(spinner_restrictor, x_margin, y_margin + (spacing * 5))
    ac.setPosition(spinner_smoothing, x_margin, y_margin + (spacing * 10))
    ac.setPosition(spinner_calculation_interval, x_margin, y_margin + (spacing * 15))
    ac.setPosition(spinner_posting_interval, x_margin, y_margin + (spacing * 20))
    ac.setPosition(label_names, x_margin, y_margin + (spacing * 25))
    ac.setPosition(label_track_progress, x_margin, y_margin + (spacing * 26))
    ac.setPosition(label_penalties, x_margin, y_margin + (spacing * 27))
    ac.setPosition(label_last_message, x_margin, y_margin + (spacing * 29))


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
    global spinner_smoothing

    SMOOTHING = ac.getValue(spinner_smoothing)/100

    prog_min = min(progresses)
    prog_max = max(progresses)

    advantages = [p - prog_min for p in progresses]
    scale = max(0.001, prog_max - prog_min)
    dampen = min(1.0, (prog_max - prog_min) / SMOOTHING)

    penalties = [dampen * (a/scale) for a in advantages]
    return penalties


def acUpdate(deltaT):
    global last_calculated, last_posted, msg_queue
    global spinner_calculation_interval, spinner_posting_interval
    global label_names, label_track_progress, label_penalties, label_last_message

    CALCULATION_INTERVAL = ac.getValue(spinner_calculation_interval)/1000
    POSTING_INTERVAL = ac.getValue(spinner_posting_interval)/1000
    PENALTY_BALLAST_MAX = ac.getValue(spinner_ballast)
    PENALTY_RESTRICTOR_MAX = ac.getValue(spinner_restrictor)
    
    if (time.clock() - last_calculated) > CALCULATION_INTERVAL:
        last_calculated = time.clock()
        progresses, names = get_progresses_and_names()
        penalties = calculate_penalties(progresses)

        # ac.console("Player progresses: {}".format(progresses))
        # ac.console("Player penalties: {}".format(penalties))
        ac.setText(label_names, "Driver names: {}".format(names))
        ac.setText(label_track_progress, "Track progresses: {}".format([round(float(i), 2) for i in progresses]))
        ac.setText(label_penalties, "Penalty percentages: {}".format([round(float(i), 2) for i in penalties]))

        msg_queue = []
        for i, p in enumerate(penalties):
            bst = int(p*PENALTY_BALLAST_MAX)
            rst = int(p*PENALTY_RESTRICTOR_MAX)

            car_name = names[i]
            grid_id = GRID_IDS.get(car_name, "NA")

            msg_queue.append("/ballast {} {}".format(grid_id, bst))
            msg_queue.append("/restrictor {} {}".format(grid_id, rst))


    if (time.clock() - last_posted) > POSTING_INTERVAL:
        last_posted = time.clock()
        msg = msg_queue.pop()
        ac.setText(label_last_message, "Last message posted: {}".format(msg))
        ac.console(msg)
        ac.sendChatMessage(msg)
