import sys
import ac
import acsys
import time

from config import GRID_IDS, ADMIN_PW
from itertools import cycle

appName = "Dynamic Ballast"
WIDTH, HEIGHT = 400, 700 # width and height of the app's window
USE_GRID_ID_CONVERSION = True # Lookup table needed in config.py if True

NCARS = ac.getCarsCount()
DRIVER_NAMES = [ac.getDriverName(i) for i in range(NCARS)]


def msg_turn_generator(n_players):
    for a in cycle(["ballast", "restrictor"]):
        for b in range(n_players):
            yield (a, b)


def acMain(ac_version):
    global appWindow, last_calculated, last_posted, turn_gen

    appWindow = ac.newApp(appName)
    ac.setTitle(appWindow, appName)
    ac.setSize(appWindow, WIDTH, HEIGHT)

    last_calculated = time.clock()
    last_posted = time.clock()

    create_ui_components()

    ac.sendChatMessage("/admin {}".format(ADMIN_PW))

    turn_gen = msg_turn_generator(NCARS)

    return appName


def create_ui_components():
    global appWindow
    global spinner_ballast, spinner_restrictor, spinner_smoothing, spinner_nonlinearity, spinner_calculation_interval, spinner_posting_interval
    global label_names, label_track_progress, label_penalties, label_last_message

    x_margin = 10
    y_margin = 80
    spacing = 16

    # Spinners
    spinner_ballast = ac.addSpinner(appWindow, "Max. ballast penalty (kg)")
    ac.setRange(spinner_ballast, 0, 5000)
    ac.setStep(spinner_ballast, 500)
    ac.setValue(spinner_ballast, 600)

    spinner_restrictor = ac.addSpinner(appWindow, "Max. restrictor penalty (pct.)")
    ac.setRange(spinner_restrictor, 0, 100)
    ac.setStep(spinner_restrictor, 10)
    ac.setValue(spinner_restrictor, 100)

    spinner_smoothing = ac.addSpinner(appWindow, "Smoothing (pct. of track)")
    ac.setRange(spinner_smoothing, 0, 100)
    ac.setStep(spinner_smoothing, 5)
    ac.setValue(spinner_smoothing, 10)

    spinner_nonlinearity = ac.addSpinner(appWindow, "Non-linearity")
    ac.setRange(spinner_nonlinearity, 1, 5)
    ac.setStep(spinner_nonlinearity, 1)
    ac.setValue(spinner_nonlinearity, 3)
    
    spinner_calculation_interval = ac.addSpinner(appWindow, "Calculation interval (ms)")
    ac.setRange(spinner_calculation_interval, 500, 5000)
    ac.setStep(spinner_calculation_interval, 500)
    ac.setValue(spinner_calculation_interval, 1000)

    spinner_posting_interval = ac.addSpinner(appWindow, "Posting interval (ms)")
    ac.setRange(spinner_posting_interval, 1000, 20000)
    ac.setStep(spinner_posting_interval, 100)
    ac.setValue(spinner_posting_interval, 1500)


    # Text output
    label_names = ac.addLabel(appWindow, "Driver names: {}".format(DRIVER_NAMES))
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
    ac.setPosition(spinner_nonlinearity, x_margin, y_margin + (spacing * 15))
    ac.setPosition(spinner_calculation_interval, x_margin, y_margin + (spacing * 20))
    ac.setPosition(spinner_posting_interval, x_margin, y_margin + (spacing * 25))
    ac.setPosition(label_names, x_margin, y_margin + (spacing * 30))
    ac.setPosition(label_track_progress, x_margin, y_margin + (spacing * 31))
    ac.setPosition(label_penalties, x_margin, y_margin + (spacing * 32))
    ac.setPosition(label_last_message, x_margin, y_margin + (spacing * 33))


def get_progresses():
    progs = []
    for i in range(NCARS):
        if ac.isConnected(i):
            lap = ac.getCarState(i, acsys.CS.LapCount)
            spline = ac.getCarState(i, acsys.CS.NormalizedSplinePosition)
            prg = lap + spline
            progs.append(prg)
    return progs


def calculate_penalties(progresses):
    global spinner_smoothing, spinner_nonlinearity

    SMOOTHING = ac.getValue(spinner_smoothing)/100
    NONLINEARITY = ac.getValue(spinner_nonlinearity)

    prog_min = min(progresses)
    prog_max = max(progresses)

    advantages = [p - prog_min for p in progresses]
    scale = max(0.001, prog_max - prog_min)
    dampen = min(1.0, (prog_max - prog_min) / SMOOTHING)

    raw_penalties = [dampen * (a/scale) for a in advantages]
    nonlinear_penalties = [p**NONLINEARITY for p in raw_penalties]

    return nonlinear_penalties


def acUpdate(delta_t):
    global last_calculated, last_posted
    global spinner_calculation_interval, spinner_posting_interval
    global label_names, label_track_progress, label_penalties, label_last_message
    global turn_gen, penalties

    CALCULATION_INTERVAL = ac.getValue(spinner_calculation_interval)/1000
    POSTING_INTERVAL = ac.getValue(spinner_posting_interval)/1000

    
    if (time.clock() - last_calculated) > CALCULATION_INTERVAL:
        last_calculated = time.clock()

        progresses = get_progresses()
        penalties = calculate_penalties(progresses)

        ac.setText(label_track_progress, "Track progresses: {}".format([round(float(i), 2) for i in progresses]))
        ac.setText(label_penalties, "Penalty percentages: {}".format([round(float(i), 2) for i in penalties]))


    if (time.clock() - last_posted) > POSTING_INTERVAL:
        p_type, target = next(turn_gen)

        if ac.isConnected(target):
            last_posted = time.clock()
            msg = create_msg(p_type, target, penalties)

            ac.sendChatMessage(msg)
            ac.setText(label_last_message, "Last message posted: {}".format(msg))


def create_msg(p_type, target, penalties):
        global spinner_ballast
        global spinner_restrictor

        MAX_BST = ac.getValue(spinner_ballast)
        MAX_RST = ac.getValue(spinner_restrictor)

        p_pct = penalties[target]

        if p_type == 'ballast':
            value = int(p_pct*MAX_BST)
        elif p_type == 'restrictor':
            value = int(p_pct*MAX_RST)

        if USE_GRID_ID_CONVERSION:
            driver_name = DRIVER_NAMES[target]
            target = GRID_IDS.get(driver_name, "NA")

        msg = "/{} {} {}".format(p_type, target, value)

        return msg
