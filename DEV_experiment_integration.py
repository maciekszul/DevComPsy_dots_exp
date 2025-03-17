import stim
import dots_util
import numpy as np
import pandas as pd
import matplotlib.pylab as plt
from pathlib import Path
from psychopy import core
from psychopy import event
from psychopy import visual
from psychopy import monitors
from datetime import datetime
from exp_util import randomisation


timestamp = str(datetime.timestamp(datetime.now()))

def abort():
    win.close()
    core.quit()


# for future JSON settings
randomisation_bool = False
n_trials = 180
n_points = 250
radius = 12.5
dot_life = 7
trial_duration = 0.35



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

mouse = event.Mouse(visible=None, win=win)

framerate = win.getActualFrameRate(
    nIdentical=10,
    nMaxFrames=200,
    nWarmUpFrames=10,
    threshold=1
)
print(framerate)

n_frames = int(framerate * 0.35)

# scales positioning
offset = 3
width = 2
height = 13

scale = stim.scales_LR(win, width, height, offset)

# arrows
arrows_img = "img/arrow_white.png"
arrows_pos = [(-3, 8), (3, 8)]
arrows_ori = [180.0, 0.0]

arrows_stim = stim.arrows(
    win, arrows_img, arrows_pos, arrows_ori
)

# labels
label_str = ["0%", "100%"]
label_pos = [(0, -6.5), (0, 6.5)]
label_stim = stim.labels(
    win, label_str, label_pos
)

# scale_objs = list(scale) + list(arrows_stim) + list(label_stim)

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
directions = np.hstack([np.repeat(0.0, n_trials//2), np.repeat(180.0, n_trials//2)])

trial_types = np.hstack([np.repeat(0, n_trials//2), np.repeat(1, n_trials//2)])

scale_directions = np.hstack([np.repeat(0, n_trials//2), np.repeat(1, n_trials//2)])

if randomisation_bool:
    directions = randomisation(directions, 3)
    trial_types = randomisation(trial_types, 3)
    scale_directions = randomisation(scale_directions, 3)
else:
    np.random.shuffle(directions)
    np.random.shuffle(trial_types)
    np.random.shuffle(scale_directions)

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

tr_type_step_value = {
    i: np.where(signal_props[i] >= 0.6 + opposite_strengths[i])[0][-1] for i in opposite_strengths.keys()
}




for trial in range(n_trials):
    stim.draw(fix_parts)
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

    # dots
    for frame in positions:
        dots_stim.xys = frame
        dots_stim.draw()
        stim.draw(fix_parts)
        win.flip()
        if event.getKeys(["escape"]):
            abort()
    stim.draw(fix_parts)
    win.flip()

    # scale response delay
    post_stimulus_wait = core.StaticPeriod()
    post_stimulus_wait.start(0.25) # or randomised

    binary_mouse = []
    rt_list = []
    cursor_pos = []
    scale_direction = scale_directions[trial]
    if scale_direction == 1:
        label_pos_tr = label_pos[::-1]
        subtr = -(height/2)
    else:
        label_pos_tr = label_pos
        subtr = (height/2)
    
    rt = None

    post_stimulus_wait.complete()
    
    # scale
    mouse.setPos()
    mouse.clickReset()
    timer = core.CountdownTimer(3)
    while timer.getTime() > 0:
        m_pos = mouse.getPos()
        buttons, times = mouse.getPressed(getTime=True)
        if buttons[0]:
            q = -3
            scale[2].setOpacity(1.0)
            rt_list.append(times[0])
        elif buttons[2]:
            q = 3
            scale[2].setOpacity(1.0)
            rt_list.append(times[2])
        else:
            q = 0
            scale[2].setOpacity(0.0)
            mouse.setPos((0, -(height/2)))
        
        [p.setPos(label_pos_tr[ix]) for ix, p in enumerate(label_stim)]
        
        if m_pos[1] < -(height/2):
            scale[2].pos = [q, -(height/2)]
        elif m_pos[1] > (height/2):
            scale[2].pos = [q, (height/2)]
        else:
            scale[2].pos = [q, m_pos[1]]
        
        cursor_pos.append(scale[2].pos)
        
        stim.draw(label_stim)
        stim.draw(arrows_stim)
        stim.draw(scale)

        win.flip()

        if any(buttons):
            binary_mouse.append(any(buttons))
            press_resp = buttons
        
        elif (len(binary_mouse) > 5) and (any(buttons) == False):
            try:
                rt = np.unique(rt_list).min()
            except:
                rt = None

            break
        
        if event.getKeys(keyList=["escape"], timeStamped=False):
            abort()
    try:
        response = mouse_map[press_resp.index(1)]
        correct = direction == response_mapping[response]
    except:
        response = None
        correct = None
    scale_resp = np.round(np.abs(((scale[2].pos[1] + subtr)/ height) *100), 2)
    print(rt, response, correct, scale_resp)


abort()