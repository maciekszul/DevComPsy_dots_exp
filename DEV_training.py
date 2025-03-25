import stim
import dots_util
import numpy as np
import pandas as pd
import matplotlib.pylab as plt
from pathlib import Path
from psychopy import gui
from psychopy import core
from psychopy import event
from psychopy import visual
from psychopy import monitors
from datetime import datetime
from itertools import product
from exp_util import randomisation, save_dict_as_json, update_json_file, plot_staircase_results, load_json


timestamp = str(datetime.timestamp(datetime.now()))

def abort(filename, plot=True, show=False):
    if plot:
        plot_staircase_results(output_df, filename)
    if show:
        img = stim.plot_image(win, filename)
        img.draw()
        win.flip()
        event.waitKeys(keyList=["escape"])

    win.close()
    core.quit()



current_path = Path.cwd()

exp_settings = {
    "exp_name": "counterfactual_staircase_training",
    "subject": "test",
    "gender (m/f/o)": "o",
    "age": 69,
    "block": 0,
    "monitor": "lab",
    "show_stair": False,
    "settings": "training_settings.json"
}

prompt = gui.DlgFromDict(
    dictionary=exp_settings, 
    title="SUBJECT"
)

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

exp_name = exp_settings["exp_name"]
subject = exp_settings["subject"]

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

win.mouseVisible = False

mouse = event.Mouse(visible=None, win=win)

framerate = win.getActualFrameRate(
    nIdentical=10,
    nMaxFrames=200,
    nWarmUpFrames=10,
    threshold=1
)
print(framerate)

n_frames = int(framerate * trial_duration)
dot_life = int(dot_life_s * framerate)

# output paths
Path("data").mkdir(parents=True, exist_ok=True)
Path("img").mkdir(parents=True, exist_ok=True)

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
label_str = ["WRONG", "CORRECT"]
label_pos = [(0, 0.0), (0, 0.0)]
label_stim = stim.labels(
    win, label_str, label_pos
)
[label_stim[i].setColor(c) for i, c in enumerate(label_colours)]

# fixation point
fix_size = 0.3
fix_parts = stim.fixation_point(win, fix_size)

# info
info_text = stim.text(win, "RANDOM IS WORKING")
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

# exp prep
# directions = np.hstack([np.repeat(0.0, n_trials//2), np.repeat(180.0, n_trials//2)])

# trial_types = np.hstack([np.repeat(0, n_trials//2), np.repeat(1, n_trials//2)])

# scale_directions = np.hstack([np.repeat(0, n_trials//2), np.repeat(1, n_trials//2)])

# if randomisation_bool:
#     directions = randomisation(directions, 3)
#     trial_types = randomisation(trial_types, 3)
#     scale_directions = randomisation(scale_directions, 3)
# else:
#     np.random.shuffle(directions)
#     np.random.shuffle(trial_types)
#     np.random.shuffle(scale_directions)

conds = {i: v for i, v in enumerate(list(product([0.0, 180.0],[0,1], [0,1])))}
trial_conds = np.tile(np.arange(8), int(n_trials/8))
trial_order = randomisation(trial_conds, N=3)
trial_settings = np.array([conds[i] for i in trial_order])
directions = trial_settings[:,0]
trial_types = trial_settings[:,1].astype(int)
scale_directions = trial_settings[:,2].astype(int)

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

mouse_map = ["left", "middle", "right"]


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

exp_data = {
    "subject": [],
    "gender (m/f/o)": [],
    "age": [],
    "block" : [],
    "trial_number": [],
    "dots_direction": [],
    "response_key": [],
    "response_correct": [],
    "opposite_strenght": [],
    "opposite_label": [],
    "step": [],
    "signal_prop": [],
    "rt" : [],
    "exp_timing_trial_prep_start": [],
    "exp_timing_stim_start": [],
    "exp_timing_stim_stop": [],
    "exp_timing_scale_start": [],
    "exp_timing_scale_stop": []
}

continuous_output = {}

mod = 2

jsonpath = Path(current_path, "data", f"{exp_name}_{subject}_{timestamp}.json")
plotpath = Path(current_path, "data", f"{exp_name}_{subject}_{timestamp}.png")

save_dict_as_json(jsonpath, continuous_output)

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
        "signal": [signal_prop, direction, 0.075],
        "counterfactual": [opposite_strengths[trial_type], directions_pos[~(directions_pos == direction)][0], 0.075],
        "noise": [1 - signal_prop, 0.0, 0.075]
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
            abort(plotpath, show=exp_settings["show_stair"])
    stim.draw(fix_parts)
    
    stim_stop = win.flip()

    # scale response delay
    post_stimulus_wait = core.StaticPeriod()
    post_stimulus_wait.start(0.25) # or randomised

    binary_mouse = []
    rt_list = []
    
    rt = None

    post_stimulus_wait.complete()
    
    # scale
    mouse.setPos()
    mouse.clickReset()
    q = 0
    ever_pressed = False
    scale_start = core.getTime()
    while True:
        m_pos = mouse.getPos()
        buttons, times = mouse.getPressed(getTime=True)
        if buttons[0]:
            q = -3
            scale[2].setOpacity(1.0)
            scale[3].setOpacity(1.0)
            rt_list.append(times[0])
            scale[2].pos = [q, -(height/2)]
            scale[3].pos = [q, 0 - height/2]

        elif buttons[2]:
            q = 3
            scale[2].setOpacity(1.0)
            scale[3].setOpacity(1.0)
            rt_list.append(times[2])
            scale[2].pos = [q, m_pos[1]]
            scale[3].pos = [q, 0 - height/2]

        else:
            q = 0
            scale[2].setOpacity(0.0)
            scale[3].setOpacity(0.0)
            mouse.setPos((0, -(height/2))) # start point of the scale
        
        stim.draw(arrows_stim)
        stim.draw(scale)
        stim.draw(fix_parts)

        frame_time = win.flip()

        if any(buttons):
            binary_mouse.append(any(buttons))
            press_resp = buttons
        
        elif (len(binary_mouse) > 10) and (any(buttons) == False):
            try:
                rt = np.unique(rt_list).min()
            except:
                rt = None

            break
        
        if event.getKeys(keyList=["escape"], timeStamped=False):
            abort(plotpath, show=exp_settings["show_stair"])
    try:
        response = mouse_map[press_resp.index(1)]
        correct = direction == response_mapping[response]
    except:
        response = None
        correct = None
    
    if response == True:
        stim.draw([label_stim[0]])
    elif response == False:
        stim.draw([label_stim[1]])

    scale_stop = win.flip()

    stim.draw(fix_parts)
    win.flip()

    post_trial_wait = core.StaticPeriod()
    post_trial_wait.start(np.random.uniform(low=2, high=3))
    
    exp_data["subject"].append(exp_settings["subject"])
    exp_data["age"].append(exp_settings["age"])
    exp_data["gender (m/f/o)"].append(exp_settings["gender (m/f/o)"])
    exp_data["block"].append(exp_settings["block"])
    exp_data["trial_number"].append(trial)
    exp_data["dots_direction"].append(direction)
    exp_data["response_key"].append(response)
    exp_data["response_correct"].append(correct)
    exp_data["step"].append(step)
    exp_data["signal_prop"].append(signal_prop)
    exp_data["opposite_strenght"].append(opposite_strengths[trial_type])
    exp_data["opposite_label"].append(trial_type)
    exp_data["rt"].append(rt)
    exp_data["exp_timing_trial_prep_start"].append(trial_prep_start)
    exp_data["exp_timing_stim_start"].append(stim_start)
    exp_data["exp_timing_stim_stop"].append(stim_stop)
    exp_data["exp_timing_scale_start"].append(scale_start)
    exp_data["exp_timing_scale_stop"].append(scale_stop)
    

    # staircase settings 2 in a row independently
    if correct == True:
        tr_type_corr_stair[trial_type] += 1

        if tr_type_corr_stair[trial_type] > corr_n_stair - 1:
            tr_type_corr_stair[trial_type] = 0
            if signal_prop > 0.3:
                tr_type_step_value[trial_type] += 2 * mod
            else:
                tr_type_step_value[trial_type] += 1 * mod

            if tr_type_step_value[trial_type] >= len(signal_props[trial_type]):
                tr_type_step_value[trial_type] = len(signal_props[trial_type]) - 1
    
    elif correct == False:
        tr_type_corr_stair[trial_type] = 0
        tr_type_step_value[trial_type] -= 1 * mod
        if tr_type_step_value[trial_type] < 0:
            tr_type_step_value[trial_type] = 0


    print(step, round(signal_prop, 4), trial_type, correct, tr_type_corr_stair[trial_type])
    # file saving
    filepath = Path(current_path, "data", f"{exp_name}_{subject}_{timestamp}.csv")
    output_df = pd.DataFrame.from_dict(exp_data)
    output_df.to_csv(filepath, index=False)

    post_trial_wait.complete()


abort(plotpath, show=exp_settings["show_stair"])

