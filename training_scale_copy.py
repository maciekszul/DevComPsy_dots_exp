import stim
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

win.mouseVisible = False

mouse = event.Mouse(visible=None, win=win)

framerate = win.getActualFrameRate(
    nIdentical=10,
    nMaxFrames=200,
    nWarmUpFrames=10,
    threshold=1
)
print(framerate)


# scales positioning
offset = 3
width = 2
height = 13

scale = stim.scales_LR(win, width, height, offset)

arrows_img = "img/arrow_white.png"
arrows_pos = [(-6, 0), (6, 0)]
arrows_ori = [180.0, 0.0]
arrows_stim = stim.arrows(
    win, arrows_img, arrows_pos, arrows_ori
)
[i.setOpacity(0.5) for i in arrows_stim]


# labels
label_colours = ["#800000", "#008000"]
label_str = ["0%", "100%"]
label_pos = [(0, -6.5), (0, 6.5)]
label_stim = stim.labels(
    win, label_str, label_pos
)
[label_stim[i].setColor(c) for i, c in enumerate(label_colours)]


win.flip()

for i in range(100):
    win.flip()
    core.wait(0.75)
    scale_direction = np.random.choice([0, 1])

    binary_mouse = []
    rt_list = []

    mouse.setPos()
    mouse.clickReset()
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
        win.flip()
        if event.getKeys(keyList=["escape"], timeStamped=False):
            abort()
        
        if any(buttons):
            binary_mouse.append(any(buttons))
            press_resp = buttons
        
        elif (len(binary_mouse) > 3) and (any(buttons) == False):
            break

abort()