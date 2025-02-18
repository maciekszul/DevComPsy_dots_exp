import numpy as np
from psychopy import core
from psychopy import event
from psychopy import visual
from psychopy import monitors
from psychopy.tools.coordinatetools import cart2pol
import dots_util

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


text_stim.text = "ZOINKS"
text_stim.draw()
win.flip()


settings = {
    "right": [0.5, 0.0, 0.075],
    "left": [0.0, 180.0, 0.075],
    "noise": [0.5, 0.0, 0.075]
}



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
n_frames = int(framerate * 1)
# dot_lifes = np.repeat(0, n_points)


init_wait = core.StaticPeriod()
init_wait.start(2)

# positions = dots_util.generate_trial(
#     n_points, radius, dot_life, n_frames, 
#     settings, dot_lifes=dot_lifes
# )

positions = dots_util.generate_trial(
    n_points, radius, dot_life, n_frames, 
    settings
)

init_wait.complete()


for frame in range(n_frames):
    dots_stim.xys = positions[frame]
    dots_stim.draw()
    win.flip()
    

win.flip()
core.wait(2)

win.close()
core.quit()