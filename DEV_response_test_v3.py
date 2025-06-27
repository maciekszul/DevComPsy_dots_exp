import u3
import stim
import dots_util
import numpy as np
from os import sep
from pathlib import Path
from exp_util import load_json, save_dict_as_json, update_json_file
from datetime import datetime
from itertools import cycle
from psychopy import gui
from psychopy import core
from psychopy import event
from psychopy import visual
from psychopy import monitors


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

mon_choice = "lab"

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

framerate = win.getActualFrameRate(
    nIdentical=10,
    nMaxFrames=200,
    nWarmUpFrames=10,
    threshold=1
)
print("framerate:", framerate)

def abort():
    win.close()
    core.quit()



# calibration
calibration = load_json("data/counterfactual_staircase-test-calibration-1750663281.498953.json")

def get_max(max_data, max_bool, no_block=999):
    blocks = np.unique(max_bool)
    blocks = blocks[blocks != no_block]
    block_maps = [max_bool == i for i in blocks]
    block_data = [max_data[i] for i in block_maps]
    max_0_100 = np.mean(np.sort([np.max(i) for i in block_data])[-3:])
    return max_0_100

def get_median(max_data, max_bool, no_block=999):
    blocks = np.unique(max_bool)
    blocks = blocks[blocks != no_block]
    block_maps = [max_bool == i for i in blocks]
    block_data = [max_data[i] for i in block_maps]
    max_0_100 = np.mean(np.sort([np.median(i) for i in block_data])[-3:])
    return max_0_100

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

# settings

hold_mpl = 0.85
max_mpl = 0.25
resp_dur = 2.0

# scales positioning
offset = 3
width = 2
height = 13

scale = stim.scales_LR(win, width, height, offset)

# text
text = stim.text(win, "")
count = stim.text(win, "")
count.color = "#000000"
count.pos = [17, 10]
count.height = 3

circle = visual.Circle(
    win,
    radius=3,
    edges=40,
    units="deg",
    fillColor="white",
    lineColor="white",
    pos=[17, 10]
)

counter = 0

response_data = {
    "raw_r": [],
    "raw_l": [],
    "prc_max_r": [],
    "prc_max_l": [],
    "time": [],
    "scale_response": [],
    "scale_response_time": []
}

for i in range(100):
    data = {
        0: [],
        1: []
    }
    time = []
    scale_val = {
        0: [],
        1: []
    }
    scale_response = []
    scale_response_time = []
    voltage = {
        0: [],
        1: []
    }
    side = []
    trial_start = core.getTime()
    while True:
        raw_data = {
            0: d.getAIN(0),
            1: d.getAIN(2)
        }
        prc_max = {
            0: (raw_data[0] - baseline[0]) / max_grip_100[0],
            1: (raw_data[1] - baseline[1]) / max_grip_100[1]
        }

        scale_multiplier = {
            0: (prc_max[0] - hold_mpl * hold_threshold[0]) / (max_mpl * max_grip_100[0]),
            1: (prc_max[1] - hold_mpl * hold_threshold[1]) / (max_mpl * max_grip_100[1])
        }

        for c in [0,1]: # controller

            if scale_multiplier[c] >= 1.0:
                scale_multiplier[c] = 1.0
            elif scale_multiplier[c] <= 0.0:
                scale_multiplier[c] = 0.0
        
            voltage[c].append(raw_data[c])
            data[c].append(prc_max[c])
            scale_val[c].append(scale_multiplier[c])
        time.append(core.getTime() - trial_start)
        

        thr_bool = [prc_max[c] > hold_threshold[c] for c in [0, 1]]

        if any(thr_bool):
            side.append(thr_bool.index(True))

        if len(side) > 0:

            sign_ = np.array([-1, 1])[side[0]]
            scale_mpl = scale_multiplier[side[0]]
            scale_response.append(scale_mpl)
            scale_response_time.append(time[-1])
            
            bar_height = scale_mpl * height

            scale[2].setOpacity(1.0)
            scale[2].pos = [sign_ * offset, -height/2]

            scale[3].setOpacity(1.0)
            scale[3].pos = [sign_ * offset, -height/2]
            scale[3].size = [2.0, bar_height]
                
        else:
            scale[2].setOpacity(0.0)
            scale[3].setOpacity(0.0)

        time_check = [len(scale_val[c]) >= int(resp_dur * framerate) for c in [0, 1]]

        if any(time_check):
            break

        try:
            RT = scale_response_time[0]
        except:
            RT = 0.0

        text_text = f"mV_0:{prc_max[0]} mV_1:{prc_max[1]}\n" \
        f"%max_0:{prc_max[0]} %max_1:{prc_max[1]}\n" \
        f"scale: {scale_multiplier}\n" \
        f"RT {RT}\n" \
        f"trial {i}\n" \
        
        text.text = text_text
        stim.draw(list(scale) + [text])
        win.flip()
        if event.getKeys(keyList=["space"], timeStamped=False):
            break
        elif event.getKeys(keyList=["escape"], timeStamped=False):
            abort()

    print([len(scale_val[c]) for c in [0, 1]], RT, sign_, np.mean(scale_response[-5]))

    while True:
        raw_data = {
            0: d.getAIN(0),
            1: d.getAIN(2)
        }
        prc_max = {
            0: (raw_data[0] - baseline[0]) / max_grip_100[0],
            1: (raw_data[1] - baseline[1]) / max_grip_100[1]
        }
        thr_bool = [prc_max[c] > hold_threshold[c] for c in [0,1]]

        if any(thr_bool):
            text_text = "Release the grip"
            text.text = text_text
            stim.draw([text])
            win.flip()
            
        else:
            win.flip()
            core.wait(2)
            break
    

abort()