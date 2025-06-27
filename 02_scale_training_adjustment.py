import u3
import stim
import dots_util
import numpy as np
from copy import copy
from os import sep
from pathlib import Path
from exp_util import load_json, save_dict_as_json, update_json_file, get_last_file, get_max
from datetime import datetime
from itertools import cycle
from psychopy import gui
from psychopy import core
from psychopy import event
from psychopy import visual
from psychopy import monitors

current_path = Path.cwd()

# subject prompt
sub_prompt = {
    "subject": "sub-666"
}

prompt = gui.DlgFromDict(
    dictionary=sub_prompt, 
    title="SUBJECT"
)

subject = sub_prompt["subject"]

data_path = current_path.joinpath("data")
subject_path = data_path.joinpath(subject)

calibration_file = get_last_file(subject_path, ext="*.json", string="calibration", ret_path=True)

calibration = load_json(calibration_file)

d = u3.U3()
d.configU3()
d.getCalibrationData()
d.configIO(FIOAnalog=3)

# setting up the monitor
monitors_ = {
    "office": [2560, 1440, 59.67, 33.56, 56],
    "lab": [1920, 1080, 59.67, 33.56, 56],
    "meg": [1920, 1080, 52.70, 29.64, 56]
}

mon_choice = calibration["monitor"]

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

def abort():
    win.close()
    core.quit()

framerate = win.getActualFrameRate(
    nIdentical=10,
    nMaxFrames=200,
    nWarmUpFrames=10,
    threshold=1
)
print("framerate:", framerate)

# getting the calibration

baseline = {
    0: np.mean(calibration["calib_baseline_data_0_1"]),
    1: np.mean(calibration["calib_baseline_data_2_9"])
}
hold = {
    0: np.mean(calibration["calib_hold_data_0_1"]),
    1: np.mean(calibration["calib_hold_data_2_9"]),
}

max_grip_data = {
    0: np.array(calibration["calib_max_data_0_1"]),
    1: np.array(calibration["calib_max_data_2_9"]),
    "0_bool": np.array(calibration["calib_max_data_0_1_bool"]),
    "1_bool": np.array(calibration["calib_max_data_2_9_bool"])
}

max_grip_100 = {
    0: get_max(max_grip_data[0] - baseline[0], max_grip_data["0_bool"]),
    1: get_max(max_grip_data[1] - baseline[1], max_grip_data["1_bool"])
}

hold_threshold = {
    0: (hold[0] - baseline[0]) / max_grip_100[0],
    1: (hold[1] - baseline[1]) / max_grip_100[1]
}

# scales positioning
offset = 3
width = 2
height = 13

scale = stim.scales_LR(win, width, height, offset)

target_bar = copy(scale[2])
target_bar.color = "red"

trial_settings = load_json(
    Path(current_path, "main_exp_settings.json")
)

resp_dur = trial_settings["resp_dur"]

thr_adj = "W + top\n" \
"A + bottom          D - bottom\n" \
"S - top"

adj = stim.text(win, thr_adj)
thr = stim.text(win, "")
thr.pos = (17, 13)

side_text = "L"
side_label = 0
side = stim.text(win, side_text)
side.pos = (0, 10)
side.height = 2

info = stim.text(win, "")
info.pos = (0, -10)


scale_boundaries = { # hold, max
    0: [1.2, 0.5],  # left
    1: [1.2, 0.5]   # right
}

target_positions = [0.10, 0.20, 0.30, 0.40, 0.60, 0.70, 0.80, 0.90]

counter = 0
target_pos = np.random.choice(target_positions)
target_on = False

while True:
    counter += 1

    raw_data = {
        0: d.getAIN(0),
        1: d.getAIN(2)
    }
    prc_max = {
        0: (raw_data[0] - baseline[0]) / max_grip_100[0],
        1: (raw_data[1] - baseline[1]) / max_grip_100[1]
    }

    scale_multiplier = {
        0: (prc_max[0] - hold_threshold[0] * scale_boundaries[0][0])  / (scale_boundaries[0][1] * max_grip_100[0]),
        1: (prc_max[1] - hold_threshold[1] * scale_boundaries[1][0])  / (scale_boundaries[1][1] * max_grip_100[1])
    }

    for c in [0,1]: # controller
        if scale_multiplier[c] >= 1.0:
            scale_multiplier[c] = 1.0
        elif scale_multiplier[c] <= 0.0:
            scale_multiplier[c] = 0.0
    
    thr_bool = [prc_max[c] > hold_threshold[c] * scale_boundaries[c][0] for c in [0, 1]]

    if thr_bool[side_label]:
        sign_ = np.array([-1, 1])[side_label]
        scale_mpl = scale_multiplier[side_label]
        
        bar_height = scale_mpl * height

        scale[2].setOpacity(1.0)
        scale[2].pos = [sign_ * offset, -height/2]

        scale[3].setOpacity(1.0)
        scale[3].pos = [sign_ * offset, -height/2]
        scale[3].size = [2.0, bar_height]
            
    else:
        scale[2].setOpacity(0.0)
        scale[3].setOpacity(0.0)

    


    thr_levels = f"hold_mpl: {round(scale_boundaries[side_label][0], 3)}\nmax_mpl: {round(scale_boundaries[side_label][1], 3)}"
    thr.text = thr_levels
    side.text = side_text
    info.text = f"mV_0:{round(raw_data[0], 4)} mV_1:{round(raw_data[1], 4)}\n" \
    f"%max_0:{round(prc_max[0], 4)} %max_1:{round(prc_max[1], 4)}\n" \
    f"scale: {scale_multiplier[side_label]}"
    stim.draw([adj, thr, side, info])
    stim.draw(scale)

    if target_on:
        if counter < int(resp_dur * framerate):
            sign_t = np.array([-1, 1])[side_label]
            target_bar.pos = [sign_t * offset, height * target_pos - height/2]
            stim.draw([target_bar])
        elif counter == int(resp_dur * framerate):
            target_pos = np.random.choice(target_positions)
        
        elif counter > 2 * int(resp_dur * framerate):
            counter = 0

    win.flip()

    if event.getKeys(keyList=["w"], timeStamped=False):
        scale_boundaries[side_label][1] += 0.01
    elif event.getKeys(keyList=["s"], timeStamped=False):
        scale_boundaries[side_label][1] -= 0.01
    elif event.getKeys(keyList=["a"], timeStamped=False):
        scale_boundaries[side_label][0] += 0.05
    elif event.getKeys(keyList=["d"], timeStamped=False):
        scale_boundaries[side_label][0] -= 0.05
    elif event.getKeys(keyList=["l"], timeStamped=False):
        side_label = 0
        side_text = "L"
    elif event.getKeys(keyList=["r"], timeStamped=False):
        side_label = 1
        side_text = "R"
    elif event.getKeys(keyList=["t"], timeStamped=False):
        target_on = not target_on
    elif event.getKeys(keyList=["escape"], timeStamped=False):
        break


update_json_file(
    calibration_file,
    {"scale_boundaries": scale_boundaries}
)

abort()