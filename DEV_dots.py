from psychopy import core
from psychopy import event
from psychopy import visual
from psychopy import monitors


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

dots = visual.DotStim(
    win,
    nDots=300,
    fieldShape="circle",
    dotSize=10,
    dotLife=5,
    signalDots="different",
    noiseDots="position",
    fieldSize=(25,25),
    coherence=0.25,
    speed=0.25
)


text_stim.text = "ZOINKS"
text_stim.draw()
win.flip()

core.wait(2)

while not event.getKeys():
    dots.draw()
    text_stim.draw()
    win.flip()

win.close()
core.quit()