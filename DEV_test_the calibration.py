import u3
import stim
import dots_util
import numpy as np
from os import sep
from pathlib import Path
from exp_util import load_json, save_dict_as_json, get_files
from datetime import datetime
from itertools import cycle
from psychopy import gui
from psychopy import core
from psychopy import event
from psychopy import visual
from psychopy import monitors


exp_settings = {
    "exp_name": "counterfactual_staircase",
    "subject": "test",
    "gender (m/f/o)": "o",
    "age": 0,
    "monitor": "office",
    "timestamp": "latest",
    "settings": "main_exp_settings.json",
    "save": True,
}

prompt = gui.DlgFromDict(
    dictionary=exp_settings, 
    title="SUBJECT"
)

timestamp = exp_settings["timestamp"]

if exp_settings["timestamp"] == "latest":
    calib_files = get_files("data", "*.json", strings=[exp_settings["exp_name"], exp_settings["subject"], "calibration"])
    calib_files.sort()
    for i in calib_files:
        print(i.stem)

    print("Using:", calib_files[-1])
    calib_file = calib_files[-1]

else:
    
    calib_files = get_files("data", "*.json", strings=[exp_settings["exp_name"], exp_settings["subject"], "calibration", timestamp])
    try:
        print("Using:", calib_files[0])
        calib_file = calib_files[0]
    except:
        raise ValueError(f"No file with timestamp {timestamp}")

calibration = load_json(calib_file)

baseline_0 = np.mean(calibration["calib_baseline_data_0_1"])
baseline_1 = np.mean(calibration["calib_baseline_data_2_9"])
