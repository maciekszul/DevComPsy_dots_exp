import stim
import dots_util
import numpy as np
from itertools import cycle
from psychopy import core
from psychopy import event
from psychopy import visual
from psychopy import monitors


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

mapping = {
    "left": 180.0,
    "right": 0.0
}

n_points = 250
radius = 12.5
dot_life = int(0.1 * framerate)
trial_duration = 2
n_frames = int(framerate * trial_duration)

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

# fixation point
fix_size = 0.3
fix_parts = stim.fixation_point(win, fix_size)


coherence_levels = np.linspace(0, 0.5, num=10)

text_str = ["caca"]
text_pos = [(-22, 14)]
text_stim = stim.labels(
    win, text_str, text_pos
)
text_stim[0].height = 0.4
text_stim[0].color = "#343434"

# precompute directions
precomputed_positions = {}
step = 0
for ix, coherence in enumerate(coherence_levels):
    for direction in ["left", "right"]:
        settings = {
            "signal": [coherence, mapping[direction], 0.075],
            "noise": [1 - coherence, 0.0, 0.075]
        }
        positions = dots_util.generate_trial(
            n_points, radius, dot_life, n_frames, 
            settings
        )

        precomputed_positions[(ix, direction)] = positions



level = 0
dir_mot = "left"

win.flip()
core.wait(0.5)

while True:
    win.flip()
    # core.wait(0.5)
    dots = cycle(precomputed_positions[(level, dir_mot)])
    text_stim[0].text = f"{np.round(coherence_levels[level], 2)} {dir_mot}"
    while True:
        frame = next(dots)
        dots_stim.xys = frame
        dots_stim.draw()
        stim.draw(text_stim)
        stim.draw(fix_parts)
        win.flip()
        if event.getKeys(["escape"]):
            abort()
            break
        elif event.getKeys(["up"]):
            level += 1
            if level > len(coherence_levels) -1:
                level = len(coherence_levels) -1
            break

        elif event.getKeys(["down"]):
            level -= 1
            if level < 0:
                level = 0
            break
        elif event.getKeys(["left"]):
            dir_mot = "left"
            break

        elif event.getKeys(["right"]):
            dir_mot = "right"
            break
