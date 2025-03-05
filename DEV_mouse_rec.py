import numpy as np
import pandas as pd
import matplotlib.pylab as plt
from pathlib import Path
from psychopy import core
from psychopy import event
from psychopy import visual
from psychopy import monitors
from datetime import datetime


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

mouse = event.Mouse(visible=None, win=win)

framerate = win.getActualFrameRate(
    nIdentical=10,
    nMaxFrames=200,
    nWarmUpFrames=10,
    threshold=1
)
print(framerate)


line = visual.Line(
    win,
    start=[-15, 0], end=[15, 0],
    units="deg", lineColor="#FFFFFF",
    lineWidth=15
)

middle_line = visual.Line(
    win,
    start=[-2, 0], end=[2, 0],
    units="deg", lineColor="#000000",
    lineWidth=15
)

cursor = visual.Line(
    win,
    start=[0, -1], end=[0, 1],
    units="deg", lineColor="#ff0000",
    lineWidth=15
)

text_str = ["100%", "0%", "100%", "0%"]
text_pos = [(-15, -0.5), (-2, -0.5), (15, -0.5), (2, -0.5)]

text_stims = []
for i, text in enumerate(text_str):
    text_stims.append(
        visual.TextStim(
            win,
            text=text,
            height=0.5,
            color="#FFFFFF",
            pos=text_pos[i],
            anchorHoriz="center", 
            anchorVert="center"
        )
    )

arrows_img = "img/arrow_white.png"
arrows_pos = [(-8.5, 3), (8.5, 3)]
arrows_ori = [180.0, 0.0]
arrows_stim = []
for i in range(len(arrows_pos)):
    arrows_stim.append(
        visual.ImageStim(
            win,
            image=arrows_img,
            size=(3,3),
            pos=arrows_pos[i],
            ori=arrows_ori[i],
            anchor="center"
        )
    )


for i in range(10):
    mouse.setPos()
    while True:
        pos = mouse.getPos()
        line.draw()
        middle_line.draw()
        [i.draw() for i in arrows_stim]

        if pos[0] > 15:
            cursor.pos = (15, 0)
        elif pos[0] < -15:
            cursor.pos = (-15, 0)
        else: 
            cursor.pos = [pos[0], 0]
        
        if np.abs(pos[0]) < 2:
            cursor.color = "#000000"
        else:
            cursor.color = "#ff0000"

        cursor.draw()
        [i.draw() for i in text_stims]
        win.flip()

        if event.getKeys(keyList=["escape"], timeStamped=False):
            abort()
        
        elif event.getKeys(keyList=["r"], timeStamped=False):
            mouse.setPos()

        elif event.getKeys(keyList=["space"], timeStamped=False):
            break

