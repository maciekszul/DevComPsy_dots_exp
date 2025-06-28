import u3
import stim
import dots_util
import numpy as np
from os import sep
from pathlib import Path
from exp_util import load_json, save_dict_as_json, make_directory
from datetime import datetime
from itertools import cycle
from psychopy import gui
from psychopy import core
from psychopy import event
from psychopy import visual
from psychopy import monitors


current_path = Path.cwd()
data_path = current_path.joinpath("data")

timestamp = str(datetime.timestamp(datetime.now()))

exp_settings = {
    "exp_name": "counterfactual_staircase",
    "subject": "sub-666",
    "gender (m/f/o)": "o",
    "age": 0,
    "monitor": "office",
    "settings": "main_exp_settings.json",
    "save": True
}

prompt = gui.DlgFromDict(
    dictionary=exp_settings, 
    title="SUBJECT"
)

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

# stimuli

circle_0 = visual.Circle(
    win,
    radius=0.4,
    edges=40,
    units="deg",
    fillColor="red",
    lineColor="red"
)

circle_2 = visual.Circle(
    win,
    radius=0.4,
    edges=40,
    units="deg",
    fillColor="blue",
    lineColor="blue"
)

continue_text = "press space to continue"
wait_text = "wait"

signal_baseline_text = "Baseline readout. Lay grippers flat on the surface."
hold_baseline_text = "Holding baseline readout. Hold the grippers without squeezing them."
max_effort_text = "When the cursor overlaps the rectangle\n perform a single grip as hard as you can and release."
max_3s_effort_text = "When the cursor overlaps the rectangle\nmaintain the maximum consistent effort for 3 seconds."

hand = stim.text(win, "")
hand.pos = [0.0, -8.0]
hand.height = 2

text = stim.text(win, "")
text.pos = [0.0, 0.0]
text.height = 1

space_text = stim.text(win, "")
space_text.pos = [0.0, -5]
space_text.height = 0.5

# max effort stimuli

circle = visual.Circle(
    win,
    radius=0.1,
    edges=40,
    units="deg",
    fillColor="white",
    lineColor="white"
)

trange = [-6, 6]
range_size = [-30, 30]
distance = [[range_size[0], -5], [range_size[1], -5]]
time_ticks = np.linspace(trange[0], trange[1], num=int(np.sum(np.abs(trange)))+1).astype(int)
time_ticks_pos = np.linspace(range_size[0], range_size[1], num=int(np.sum(np.abs(trange)))+1)
time_ticks_pos = [[i, -6] for i in time_ticks_pos]
ticks = stim.labels(win, time_ticks, time_ticks_pos)

line = visual.Line(
    win, start=distance[0], end=distance[1],
    lineColor="#FFFFFF", lineWidth=2
)

data_size = int(framerate * np.abs(trange[0]))
data_pos = np.linspace(range_size[0], 0, num=data_size)

step_frame = np.abs(range_size[0]) / data_size

data_0 = np.zeros(data_size).tolist()
vertices = np.vstack([data_pos, np.array(data_0)]).transpose()
trace_0 = visual.ShapeStim(
    win, vertices=vertices, closeShape=False, 
    lineWidth=2, lineColor="red"
)

data_1 = np.zeros(data_size).tolist()
vertices = np.vstack([data_pos, np.array(data_1)]).transpose()
trace_1 = visual.ShapeStim(
    win, vertices=vertices, closeShape=False, 
    lineWidth=2, lineColor="blue"
)

width = 3 * int(framerate) * step_frame


positions = [12, 6, 6, 6, 6, 6]
positions = [i * int(framerate) * step_frame for i in positions]
positions = np.cumsum(positions)

boxes = stim.make_boxes(
    win, width, positions, "#daa520"
)


# data

calibration = {
    "calib_baseline_data_0_1": [],
    "calib_baseline_data_2_9": [],
    "calib_hold_data_0_1": [],
    "calib_hold_data_2_9": [],
    "calib_max_data_0_1": [],
    "calib_max_data_2_9": [],
    "calib_max_data_0_1_bool": [],
    "calib_max_data_2_9_bool": [],
}

# calibration

text.text = signal_baseline_text
space_text.text = continue_text

stim.draw([text, space_text])
win.flip()

event.waitKeys(keyList=["space"])

text.text = signal_baseline_text
space_text.text = wait_text
stim.draw([text, space_text])
win.flip()

wait = core.StaticPeriod()
wait.start(5)

for i in range(4000):
    calibration["calib_baseline_data_0_1"].append(d.getAIN(0))
    calibration["calib_baseline_data_2_9"].append(d.getAIN(2))

baseline_0 = np.mean(calibration["calib_baseline_data_0_1"])
baseline_1 = np.mean(calibration["calib_baseline_data_2_9"])

wait.complete()

text.text = hold_baseline_text
space_text.text = continue_text
stim.draw([text, space_text])
win.flip()

event.waitKeys(keyList=["space"])

text.text = hold_baseline_text
space_text.text = "Hold the grippers without squeezing"
stim.draw([text, space_text])
win.flip()

wait = core.StaticPeriod()
wait.start(5)

for i in range(4000):
    calibration["calib_hold_data_0_1"].append(d.getAIN(0))
    calibration["calib_hold_data_2_9"].append(d.getAIN(2))

wait.complete()


text.text = max_effort_text
space_text.text = continue_text

stim.draw([text, space_text])
win.flip()

event.waitKeys(keyList=["space"])

while True:
    hand.text = "LEFT"
    
    raw_data_in_0 = d.getAIN(0)
    calibration["calib_max_data_0_1"].append(raw_data_in_0)

    data_in_0 = raw_data_in_0 - baseline_0

    data_0.append(data_in_0 - 4.5)
    data_0 = data_0[1:]

    circle.pos = [0, data_in_0 - 4.5]

    overlap = [circle.overlaps(i) for i in boxes]

    overlap_bool = any(overlap)

    if overlap_bool:
        which_box = overlap.index(True)
    elif not overlap_bool:
        which_box = 999

    calibration["calib_max_data_0_1_bool"].append(which_box)

    trace_0.vertices = np.vstack([data_pos, np.array(data_0)]).transpose()
    stim.move_boxes(boxes, step_frame)
    line.draw()
    stim.draw(boxes)
    stim.draw([trace_0, line, circle] + ticks + [hand])
    win.flip()


    if event.getKeys(keyList=["escape"], timeStamped=False):
        break
    

boxes = stim.make_boxes(
    win, width, positions, "#daa520"
)

while True:
    hand.text = "RIGHT"
    
    raw_data_in_1 = d.getAIN(2)
    calibration["calib_max_data_2_9"].append(raw_data_in_1)

    data_in_1 = raw_data_in_1 - baseline_1

    data_1.append(data_in_1 - 4.5)
    data_1 = data_1[1:]

    circle.pos = [0, data_in_1 - 4.5]

    overlap = [circle.overlaps(i) for i in boxes]

    overlap_bool = any(overlap)

    if overlap_bool:
        which_box = overlap.index(True)
    elif not overlap_bool:
        which_box = 999
    
    calibration["calib_max_data_2_9_bool"].append(which_box)

    trace_1.vertices = np.vstack([data_pos, np.array(data_1)]).transpose()
    stim.move_boxes(boxes, step_frame)
    line.draw()
    stim.draw(boxes)
    stim.draw([trace_1, line, circle] + ticks + [hand])
    win.flip()


    if event.getKeys(keyList=["escape"], timeStamped=False):
        break


text.text = "End of calibration."
space_text.text = continue_text

stim.draw([text, space_text])
win.flip()

if exp_settings["save"]:
    output_dict = {**exp_settings, **calibration}
    output_dict["framerate"] = float(framerate)
    exp_name = exp_settings["exp_name"]
    subject = exp_settings["subject"]

    output_file = f"{exp_name}-{subject}-calibration-{timestamp}.json"

    output_dir = make_directory(data_path, subject)

    out = output_dir.joinpath(output_file)

    save_dict_as_json(out, output_dict)

abort()

