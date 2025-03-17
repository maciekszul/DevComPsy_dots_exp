import numpy as np
import pandas as pd
import matplotlib.pylab as plt
from pathlib import Path
from psychopy import core
from psychopy import event
from psychopy import visual
from psychopy import monitors
from datetime import datetime
import dots_util
from exp_util import randomisation


timestamp = str(datetime.timestamp(datetime.now()))

def abort():
    win.close()
    core.quit()


monitors_ = {
    "office": [2560, 1440, 59.67, 33.56, 56],
    "meg": [1920, 1080, 52.70, 29.64, 56]
}

mon_choice = "office"

mon = monitors.Monitor(mon_choice)
w_px, h_px, w_cm, h_cm, d_cm = monitors_[mon_choice]
mon.setWidth(w_cm)
mon.setDistance(d_cm)
mon.setSizePix((w_px, h_px))
mon.save()

background_color = "#000000"

win = visual.Window(
    [w_px, h_px],
    monitor=mon,
    units="deg",
    color=background_color,
    fullscr=True,
    allowGUI=False,
    winType="pyglet"
)

win.mouseVisible = False

framerate = win.getActualFrameRate(
    nIdentical=10,
    nMaxFrames=200,
    nWarmUpFrames=10,
    threshold=1
)
print(framerate)

sz = 0.30
th = sz / 5

circle = visual.Circle(
    win,
    radius=sz,
    edges=40,
    units="deg",
    fillColor="white",
    lineColor="white"
)

line1 = visual.ShapeStim(
    win,
    vertices=[
        [sz, 0 + th],
        [-sz*1., 0 + th],
        [-sz*2, 0 - th],
        [sz*2, 0 - th]
    ],
    units='deg',
    fillColor=background_color,
    lineColor=background_color
)

line2 = visual.ShapeStim(
    win,
    vertices=[
        [0 - th, sz],
        [0 + th, sz],
        [0 + th, -sz],
        [0 - th, -sz]
    ],
    units='deg',
    fillColor=background_color,
    lineColor=background_color
)

circle1 = visual.Circle(
    win,
    radius=th,
    edges=40,
    units='deg',
    fillColor='white',
    lineColor='white'
)

def draw_cue():
    circle.draw()
    line1.draw()
    line2.draw()
    circle1.draw()


text_stim = visual.TextStim(
    win,
    text="",
    height=0.35,
    color="#FFFFFF",
    pos=(-17, 13),
    anchorHoriz="center", 
    anchorVert="center"
)

n_points = 250

dots_stim = visual.ElementArrayStim(
    win,
    units="deg",
    fieldSize=(25.0, 25.0),
    nElements=n_points,
    sizes=0.25,
    colors=(1.0, 1.0, 1.0),
    colorSpace="rgb",
    elementMask="circle",
    sfs=0.0
)

text_stim.text = "randomisation"
text_stim.draw()
win.flip()

radius = 12.5
dot_life = 7
n_frames = int(framerate * 0.35)

n_trials = 180
directions = np.hstack([np.repeat(0.0, n_trials//2), np.repeat(180.0, n_trials//2)])
directions = randomisation(directions, 3)

trial_types = np.hstack([np.repeat(0, n_trials//2), np.repeat(1, n_trials//2)])
trial_types = randomisation(trial_types, 3)

opposite_strengths = {
    "low": 0.05,
    "high": 0.15
}

signal_props = {
    i: np.arange(0.025, 1.0 - opposite_strengths[i], 0.025)[::-1] for i in opposite_strengths.keys()
}

response_mapping = {
    "left": 180.0,
    "right": 0.0
}

draw_cue()
win.flip()

step = {i: 0 for i in opposite_strengths.keys()}

exp_data = {
    "block" : [],
    "trial_number": [],
    "dots_direction": [],
    "response_key": [],
    "response_correct": [],
    "opposite_strenght": [],
    "opposite_label": [],
    "step": [],
    "signal_prop": []
}

Path("data").mkdir(parents=True, exist_ok=True)
Path("img").mkdir(parents=True, exist_ok=True)

directions_pos = np.array([0.0, 180.0])


tr_type_step_list = {
    i: [] for i in opposite_strengths.keys()
}

tr_type_correct_list = {
    i: [] for i in opposite_strengths.keys()
}

tr_type_step_value = {
    i: np.where(signal_props[i] >= 0.6 + opposite_strengths[i])[0][-1] for i in opposite_strengths.keys()
}



for trial in range(n_trials):
    pre_trial_wait = core.StaticPeriod()
    pre_trial_wait.start(0.25)

    trial_type = list(opposite_strengths.keys())[trial_types[trial]]

    step = tr_type_step_value[trial_type]
    signal_prop = signal_props[trial_type][step]
    direction = directions[trial]

    settings = {
        "signal": [signal_prop, direction, 0.075],
        "counterfactual": [opposite_strengths[trial_type], directions_pos[~(directions_pos == direction)][0], 0.075],
        "noise": [1 - signal_prop, 0.0, 0.075]
    }

    positions = dots_util.generate_trial(
        n_points, radius, dot_life, n_frames, 
        settings
    )

    pre_trial_wait.complete()

    for frame in positions:
        dots_stim.xys = frame
        dots_stim.draw()
        draw_cue()
        win.flip()
        if event.getKeys(["q"]):
            abort()
    draw_cue()
    win.flip()
    timer = core.CountdownTimer(3)
    while timer.getTime() > 0:
        key = event.getKeys(["left", "right"], timeStamped=True)
        if len(key) > 0:
            response, response_time = key[0]
            response_correct = direction == response_mapping[response]
            break

        elif event.getKeys(["q"]):
            abort()
    event.clearEvents()
    post_trial_wait = core.StaticPeriod()
    post_trial_wait.start(0.25)

    exp_data["block"].append(0)
    exp_data["trial_number"].append(trial)
    exp_data["dots_direction"].append(direction)
    exp_data["response_key"].append(response)
    exp_data["response_correct"].append(response_correct)
    exp_data["step"].append(step)
    exp_data["signal_prop"].append(signal_prop)
    exp_data["opposite_strenght"].append(opposite_strengths[trial_type])
    exp_data["opposite_label"].append(trial_type)

    tr_type_correct_list[trial_type].append(response_correct)

    if sum(tr_type_correct_list[trial_type][-2:]) == 2:
        if signal_prop > 0.3:
            tr_type_step_value[trial_type] += 2
        else:
            tr_type_step_value[trial_type] += 1

        if tr_type_step_value[trial_type] >= len(signal_props[trial_type]):
            tr_type_step_value[trial_type] = len(signal_props[trial_type]) - 1

    
    if tr_type_correct_list[trial_type][-1] == False:
        tr_type_step_value[trial_type] -= 1
        if tr_type_step_value[trial_type] < 0:
            tr_type_step_value[trial_type] = 0


    filepath = Path("data", f"interleaved_staircase_output_{timestamp}.csv")
    pd.DataFrame.from_dict(exp_data).to_csv(filepath, index=False)
    post_trial_wait.complete()

abort()