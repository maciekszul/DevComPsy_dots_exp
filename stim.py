from psychopy import visual


def scales_LR(win, width, height, offset):

    L_scale = visual.Rect(
        win, width=width, height=height,
        color="#FFFFFF", units="deg",
        pos=[-offset, 0]
    )

    R_scale = visual.Rect(
        win, width=width, height=height,
        color="#FFFFFF", units="deg",
        pos=[offset, 0]
    )

    marker = visual.Line(
        win, start=[0 - width/2, 0], end=[0 + width/2, 0],
        lineColor="red", lineWidth=15
        )
    
    box = visual.Rect(
        win, width=width, height=height,
        color="red", units="deg", anchor="bottom",
        pos=[0,0]
    )

    return L_scale, R_scale, marker, box


arrows_img = "img/arrow_white.png"
arrows_pos = [(-3, 8), (3, 8)]
arrows_ori = [180.0, 0.0]

def arrows(win, arrows_img, arrows_pos, arrows_ori):
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
    return arrows_stim


def labels(win, label_str, label_pos):
    text_stims = []
    for i, text in enumerate(label_str):
        text_stims.append(
            visual.TextStim(
                win,
                text=text,
                height=1.2,
                color="#FFFFFF",
                pos=label_pos[i],
                anchorHoriz="center", 
                anchorVert="center"
            )
        )
    return text_stims


def fixation_point(win, size, mp=1.05, th_div=5, background_color="#000000"):
    th = size / th_div # thiccness

    circle = visual.Circle(
        win,
        radius=size,
        edges=40,
        units="deg",
        fillColor="white",
        lineColor="white"
    )

    line1 = visual.ShapeStim(
        win,
        vertices=[
            [size*mp, 0 + th],
            [-size*mp, 0 + th],
            [-size*mp, 0 - th],
            [size*mp, 0 - th]
        ],
        units='deg',
        fillColor=background_color,
        lineColor=background_color
    )

    line2 = visual.ShapeStim(
        win,
        vertices=[
            [0 - th, size*mp],
            [0 + th, size*mp],
            [0 + th, -size*mp],
            [0 - th, -size*mp]
        ],
        units='deg',
        fillColor=background_color,
        lineColor=background_color
    )

    circle1 = visual.Circle(
        win,
        radius=th,
        edges=40,
        units='deg',
        fillColor='white',
        lineColor='white'
    )

    return circle, line1, line2, circle1


def draw(list):
    [i.draw() for i in list]

def text(win, text):
    text_stim = visual.TextStim(
        win,
        text=text,
        height=0.35,
        color="#FFFFFF",
        pos=(-17, 13),
        anchorHoriz="center", 
        anchorVert="center"
    )
    return text_stim


def plot_image(win, image_path):
    img = visual.ImageStim(
        win, image=image_path
    )
    return img