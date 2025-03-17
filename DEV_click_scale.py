import numpy as np
import pandas as pd
import matplotlib.pylab as plt
from pathlib import Path
from psychopy import core
from psychopy import event
from psychopy import visual
from psychopy import monitors
from datetime import datetime
from exp_util import scales_LR, arrows


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


# scales positioning
offset = 3
width = 2
height = 13

scale = scales_LR(win, width, height, offset)



arrows_img = "img/arrow_white.png"
arrows_pos = [(-3, 8), (3, 8)]
arrows_ori = [180.0, 0.0]
arrows_stim = arrows(
    win, arrows_img, arrows_pos, arrows_ori
)


text_str = ["0%", "100%"]
text_pos = [(0, -6.5), (0, 6.5)]

text_stims = []
for i, text in enumerate(text_str):
    text_stims.append(
        visual.TextStim(
            win,
            text=text,
            height=1.2,
            color="#FFFFFF",
            pos=text_pos[i],
            anchorHoriz="center", 
            anchorVert="center"
        )
    )


for i in range(10):
    start_trial = core.getTime()
    binary_mouse = []
    rt_list = []
    cursor_pos = []
    if i%2 == 1:
        text_pos_tr = text_pos[::-1]
        subtr = -(height/2)
    else:
        text_pos_tr = text_pos
        subtr = (height/2)

    mouse.setPos()
    mouse.clickReset()
    while True:
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
        [i.draw() for i in arrows_stim]
        [p.setPos(text_pos_tr[ix]) for ix, p in enumerate(text_stims)]
        [i.draw() for i in text_stims]

        if m_pos[1] < -(height/2):
            scale[2].pos = [q, -(height/2)]
        elif m_pos[1] > (height/2):
            scale[2].pos = [q, (height/2)]
        else:
            scale[2].pos = [q, m_pos[1]]
        
        cursor_pos.append(scale[2].pos)
        [i.draw() for i in scale]

        win.flip()

        if any(buttons):
            binary_mouse.append(any(buttons))
        elif (len(binary_mouse) > 5) and (any(buttons) == False):
            break

        if event.getKeys(keyList=["escape"], timeStamped=False):
            abort()


    print(np.unique(rt_list).min(), np.abs(np.round((scale[2].pos[1] + subtr)/ height, 2)*100), "%")

abort()

