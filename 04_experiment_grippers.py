import u3
import stim
import dots_util
import numpy as np
import pandas as pd
import matplotlib.pylab as plt
from os import sep
from pathlib import Path
from datetime import datetime
from itertools import cycle, product
from psychopy import gui
from psychopy import core
from psychopy import event
from psychopy import visual
from psychopy import monitors
from exp_util import randomisation, save_dict_as_json, update_json_file, plot_staircase_results, load_json, get_directories, get_files, get_max, get_median, get_last_file

timestamp = str(datetime.timestamp(datetime.now()))

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

try:
    previous_block = get_last_file(subject_path, string="block")
    previous_block += 1
except:
    previous_block = 0

calibration_file = get_last_file(subject_path, ext="*.json", string="calibration", ret_path=True)

calibration = load_json(calibration_file)

# prompt
exp_settings = {
    "exp_name": calibration["exp_name"],
    "subject": subject,
    "gender (m/f/o)": calibration["gender (m/f/o)"],
    "age": calibration["age"],
    "block": previous_block,
    "monitor": calibration["monitor"],
    "settings": "main_exp_settings.json"
}


prompt = gui.DlgFromDict(
    dictionary=exp_settings, 
    title="DATA"
)

# LabJack Setup
d = u3.U3()
d.configU3()
d.getCalibrationData()
d.configIO(FIOAnalog=3)



trial_settings = load_json(
    Path(current_path, exp_settings["settings"])
)

randomisation_bool = trial_settings["randomisation_bool"]
n_trials = trial_settings["n_trials"]
n_points = trial_settings["n_points"]
radius = trial_settings["radius"]
dot_life_s = trial_settings["dot_life_s"]
trial_duration = trial_settings["trial_duration"]
corr_n_stair = trial_settings["corr_n_stair"]
small_steps = trial_settings["small_steps"]
starting_point = trial_settings["starting_point"]
dot_speed = trial_settings["dot_speed"]

step_mode = 2

resp_dur = trial_settings["resp_dur"]

exp_name = exp_settings["exp_name"]
subject = exp_settings["subject"]
block = exp_settings["block"]



# setting up the monitor
monitors_ = {
    "office": [2560, 1440, 59.67, 33.56, 56],
    "lab": [1920, 1080, 59.67, 33.56, 56],
    "meg": [1920, 1080, 52.70, 29.64, 56]
}

mon_choice = exp_settings["monitor"]

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

n_frames = int(framerate * trial_duration)
dot_life = int(dot_life_s * framerate)

dot_frame_displacement = dot_speed / framerate

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

scale_boundaries = calibration["scale_boundaries"]

scale_boundaries = {int(i): scale_boundaries[i] for i in scale_boundaries.keys()}


# scales positioning
offset = 3
width = 2
height = 13

scale = stim.scales_LR(win, width, height, offset)

# arrows
arrows_img = "img/arrow_white.png"
arrows_pos = [(-6, 0), (6, 0)]
arrows_ori = [180.0, 0.0]

arrows_stim = stim.arrows(
    win, arrows_img, arrows_pos, arrows_ori
)

[i.setOpacity(0.75) for i in arrows_stim]

# labels
label_colours = ["#800000", "#008000"]
label_str = ["0%", "100%"]
label_pos = [(0, -6.5), (0, 6.5)]
label_stim = stim.labels(
    win, label_str, label_pos
)
[label_stim[i].setColor(c) for i, c in enumerate(label_colours)]

# fixation point
fix_size = 0.3
fix_parts = stim.fixation_point(win, fix_size)

# info
info_text = stim.text(win, "RANDOMISATION IS WORKING")
info_text.draw()
win.flip()

# dots
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

conds = {i: v for i, v in enumerate(list(product([0.0, 180.0],[0,1])))}
trial_order = []
for i in range(int(n_trials/4)):
    trial_order.append(randomisation(np.arange(4), N=2))
trial_order = np.array(trial_order).flatten()
trial_settings = np.array([conds[i] for i in trial_order])
directions = trial_settings[:,0]
trial_types = trial_settings[:,1].astype(int)
scale_directions = np.tile(np.arange(2), int(n_trials/2))

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

gripper_mapping = {
    0: "left",
    1: "right"
}

directions_pos = np.array([0.0, 180.0])

# containers
tr_type_step_list = {
    i: [] for i in opposite_strengths.keys()
}

tr_type_correct_list = {
    i: [] for i in opposite_strengths.keys()
}

tr_type_corr_stair = {
    i: 0 for i in opposite_strengths.keys()
}

# where the staircase starts

tr_type_step_value = {
    i: int(np.min(np.where(signal_props[i] < 0.5 + opposite_strengths[i])[0])) for i in opposite_strengths.keys()
}

# output dictionaries

exp_data = {
    "subject": [],
    "gender (m/f/o)": [],
    "age": [],
    "block" : [],
    "trial_number": [],
    "dots_direction": [],
    "scale_direction": [],
    "response_key": [],
    "response_correct": [],
    "opposite_strenght": [],
    "opposite_label": [],
    "step": [],
    "signal_prop": [],
    "scale_response": [],
    "rt" : [],
    "exp_timing_trial_prep_start": [],
    "exp_timing_stim_start": [],
    "exp_timing_stim_stop": [],
    "exp_timing_scale_start": [],
    "exp_timing_scale_stop": []
}

response_data = {
    "raw_r": [],
    "raw_l": [],
    "prc_max_r": [],
    "prc_max_l": [],
    "time": [],
    "scale_response": [],
    "scale_response_time": []
}

continuous_output = {}

jsonpath = Path(subject_path, f"{exp_name}_{subject}_block-{str(block).zfill(3)}_{timestamp}.json")

save_dict_as_json(jsonpath, continuous_output)

plotpath = Path(subject_path, f"{exp_name}_{subject}_block-{str(block).zfill(3)}_{timestamp}.png")

info_text = stim.text(win, "PRESS SPACE TO CONTINUE")
info_text.draw()
win.flip()
event.waitKeys(keyList=["space"])

core.wait(2)

for trial in range(n_trials):

    stim.draw(fix_parts)
    trial_prep_start = win.flip()

    trial_prep_wait = core.StaticPeriod()
    trial_prep_wait.start(0.25 + np.random.uniform(0, 0.25))

    if trial > small_steps:
        mod = 1

    trial_type = list(opposite_strengths.keys())[trial_types[trial]]

    step = tr_type_step_value[trial_type]
    signal_prop = signal_props[trial_type][step]
    direction = directions[trial]

    settings = {
        "signal": [signal_prop, direction, dot_frame_displacement],
        "counterfactual": [opposite_strengths[trial_type], directions_pos[~(directions_pos == direction)][0], dot_frame_displacement],
        "noise": [1 - signal_prop, 0.0, dot_frame_displacement]
    }

    positions = dots_util.generate_trial(
        n_points, radius, dot_life, n_frames, 
        settings
    )

    trial_prep_wait.complete()

    # dots
    stim_start = core.getTime()
    for frame_ix, frame in enumerate(positions):
        dots_stim.xys = frame
        dots_stim.draw()
        stim.draw(fix_parts)
        if frame_ix == 0:
            stim_start = win.flip()
        else:
            win.flip()
        if event.getKeys(["escape"]):
            abort()
    stim.draw(fix_parts)
    
    stim_stop = win.flip()

    # scale response delay
    post_stimulus_wait = core.StaticPeriod()
    post_stimulus_wait.start(0.25) # or randomised

    scale_direction = scale_directions[trial]
    scale_direction = np.random.choice([0, 1])
    if scale_direction == 1:
        label_pos_tr = label_pos[::-1]
    else:
        label_pos_tr = label_pos
    
    post_stimulus_wait.complete()
    # response

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
            0: (prc_max[0] - hold_threshold[0] * scale_boundaries[0][0])  / (scale_boundaries[0][1] * max_grip_100[0]),
            1: (prc_max[1] - hold_threshold[1] * scale_boundaries[1][0])  / (scale_boundaries[1][1] * max_grip_100[1])
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
        

        thr_bool = [prc_max[c] > hold_threshold[c] * scale_boundaries[c][0] for c in [0, 1]]

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
        
        [p.setPos(label_pos_tr[ix]) for ix, p in enumerate(label_stim)]

        stim.draw(label_stim)
        stim.draw(arrows_stim)
        stim.draw(scale)
        win.flip()

        time_check = [len(scale_val[c]) >= int(resp_dur * framerate) for c in [0, 1]]
        if any(time_check):
            scale_stop = core.getTime()
            break

        if event.getKeys(keyList=["="], timeStamped=False):
            break
        elif event.getKeys(keyList=["escape"], timeStamped=False):
            abort()
    try:
        response = gripper_mapping[side[0]]
        correct = direction == response_mapping[response]
    except:
        response = None
        correct = None
    
    try:
        RT = scale_response_time[0]
    except:
        RT = 999.0

    try:
        if scale_direction == 1:
            scale_response = (1 - np.array(scale_response)).tolist()
            scale_value = np.mean(scale_response[-5])
        else:
            scale_value = np.mean(scale_response[-5])
    except:
        scale_value = None

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
            info_text.text = text_text
            info_text.pos = (0,0)
            info_text.height = 2
            stim.draw([info_text])
            win.flip()
            
        else:
            win.flip()
            post_response_wait = core.StaticPeriod()
            post_response_wait.start(2)

            if correct == True:
                tr_type_corr_stair[trial_type] += 1

                if tr_type_corr_stair[trial_type] > corr_n_stair - 1:
                    tr_type_corr_stair[trial_type] = 0
                    if signal_prop > 0.3:
                        tr_type_step_value[trial_type] += 2 * step_mode
                    else:
                        tr_type_step_value[trial_type] += 1 * step_mode

                    if tr_type_step_value[trial_type] >= len(signal_props[trial_type]):
                        tr_type_step_value[trial_type] = len(signal_props[trial_type]) - 1
            
            elif correct == False:
                tr_type_corr_stair[trial_type] = 0
                tr_type_step_value[trial_type] -= 1 * step_mode
                if tr_type_step_value[trial_type] < 0:
                    tr_type_step_value[trial_type] = 0

            exp_data["subject"].append(exp_settings["subject"])
            exp_data["age"].append(exp_settings["age"])
            exp_data["gender (m/f/o)"].append(exp_settings["gender (m/f/o)"])
            exp_data["block"].append(exp_settings["block"])
            exp_data["trial_number"].append(trial)
            exp_data["dots_direction"].append(direction)
            exp_data["response_key"].append(response)
            exp_data["response_correct"].append(correct)
            exp_data["step"].append(step)
            exp_data["signal_prop"].append(round(signal_prop, 4))
            exp_data["opposite_strenght"].append(opposite_strengths[trial_type])
            exp_data["opposite_label"].append(trial_type)
            exp_data["scale_response"].append(scale_value)
            exp_data["rt"].append(RT)
            exp_data["scale_direction"].append(scale_direction)
            exp_data["exp_timing_trial_prep_start"].append(trial_prep_start)
            exp_data["exp_timing_stim_start"].append(stim_start)
            exp_data["exp_timing_stim_stop"].append(stim_stop)
            exp_data["exp_timing_scale_start"].append(time[0])
            exp_data["exp_timing_scale_stop"].append(scale_stop)

            print(step, round(signal_prop, 4), trial_type, correct, tr_type_corr_stair[trial_type])
            # file saving
            filepath = Path(subject_path, f"{exp_name}_{subject}_block-{str(block).zfill(3)}_{timestamp}.csv")
            output_df = pd.DataFrame.from_dict(exp_data)
            output_df.to_csv(filepath, index=False)

            try:
                if scale_direction == 1:
                    scr = (100 - np.array(scale_response)).tolist()
                else:
                    scr = scale_response
            except:
                scr = []

            trial_output = {
                "-".join([str(trial), "L", "raw_data"]): voltage[0],
                "-".join([str(trial), "R", "raw_data"]): voltage[1],
                "-".join([str(trial), "L", "prc_max"]): data[0],
                "-".join([str(trial), "R", "prc_max"]): data[1],
                "-".join([str(trial), "L", "scale_response"]): scale_val[0],
                "-".join([str(trial), "R", "scale_response"]): scale_val[1],
                "-".join([str(trial), "confidence"]): scr,
                "-".join([str(trial), "confidence_time"]): scale_response_time,
                "-".join([str(trial), "time"]): time
            }
            update_json_file(jsonpath, trial_output)

            post_response_wait.complete()
            break
        
        if event.getKeys(keyList=["="], timeStamped=False):
            break
        elif event.getKeys(keyList=["escape"], timeStamped=False):
            plot_staircase_results(output_df, plotpath)
            abort()

plot_staircase_results(output_df, plotpath)
abort()