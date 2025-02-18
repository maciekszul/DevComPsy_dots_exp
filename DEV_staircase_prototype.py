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


win = visual.Window(
    [w_px, h_px],
    monitor=mon,
    units="deg",
    color="#000000",
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

text_stim = visual.TextStim(
    win,
    text="",
    height=0.5,
    color="white",
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

radius = 12.5
dot_life = 5
n_frames = int(framerate * 2)


n_trials = 90
directions = np.hstack([np.repeat(0.0, n_trials//2), np.repeat(180.0, n_trials//2)])
np.random.shuffle(directions)

counterfact = 0.15

signal_props_big = np.arange(0.05, 1.0 - counterfact, 0.05)[::-1]
signal_props_small = np.arange(0.025, 1.0 - counterfact, 0.025)[::-1]

response_mapping = {
    "left": 180.0,
    "right": 0.0
}

core.wait(1)

step = 0

exp_data = {
    "block" : [],
    "trial_number": [],
    "dots_direction": [],
    "response_key": [],
    "response_correct": [],
    "step": [],
    "signal_prop": []
}

Path("data").mkdir(parents=True, exist_ok=True)
Path("img").mkdir(parents=True, exist_ok=True)

steps_mode = {
    "coarse": signal_props_big,
    "fine": signal_props_small
}

directions_pos = np.array([0.0, 180.0])

mode = "fine"

for trial in range(n_trials):
    pre_trial_wait = core.StaticPeriod()
    pre_trial_wait.start(0.5)

    signal_props = steps_mode[mode]
    direction = directions[trial]
    signal_prop = signal_props[step]
    settings = {
        "signal": [signal_prop, direction, 0.075],
        "counterfactual": [counterfact, directions_pos[~(directions_pos == direction)][0], 0.075],
        "noise": [1 - (signal_prop), 0.0, 0.075]
    }

    positions = dots_util.generate_trial(
        n_points, radius, dot_life, n_frames, 
        settings
    )

    pre_trial_wait.complete()

    response_correct = False
    response = None
    frame = 0
    while True:
        dots_stim.xys = positions[frame]
        dots_stim.draw()
        key = event.getKeys(["left", "right"], timeStamped=True)
        text_stim.text = f"mode: {mode}, step: {step}/{len(signal_props)}, coh: {np.round(signal_prop, 3)}"
        text_stim.draw()
        win.flip()
        frame += 1

        if len(key) > 0:
            response, response_time = key[0]
            response_correct = direction == response_mapping[response]
            break

        elif frame >= n_frames:
            break

        elif event.getKeys(["q"]):
            abort()
    event.clearEvents()
    print(direction, response, response_correct)
    win.flip()

    post_trial_wait = core.StaticPeriod()
    post_trial_wait.start(0.25)

    exp_data["block"].append(0)
    exp_data["trial_number"].append(trial)
    exp_data["dots_direction"].append(direction)
    exp_data["response_key"].append(response)
    exp_data["response_correct"].append(response_correct)
    exp_data["step"].append(step)
    exp_data["signal_prop"].append(signal_prop)

    if sum(exp_data["response_correct"][-2:]) == 2:
        if signal_prop > 0.3:
            step += 2
        else:
            step += 1

        if step >= len(signal_props):
            step = len(signal_props) - 1

    
    if response_correct == False:
        step -= 1
        if step < 0:
            step = 0

    filepath = Path("data", f"staircase_output_{timestamp}.csv")
    pd.DataFrame.from_dict(exp_data).to_csv(filepath, index=False)

    post_trial_wait.complete()





abort()
    



