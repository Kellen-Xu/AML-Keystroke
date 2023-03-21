from utils import *
from models import *

import numpy as np

TERMINATE_SIGNAL = "stop"
VALID_PRESS_THRESHOLD = 100
NUM_PASSWORD = 6
NUM_KEYS = 4
def parse_line(line):
    line = line.decode().strip()


def is_stop_sign(line):
    if line == TERMINATE_SIGNAL:
        print("Received signals, trigger inferencing")
        return True
    return False


def is_valid_sample(X):
    num_flips = 0
    cur_status = False
    flip_pos = []
    for i, x in enumerate((np.sum(X, axis=1) > VALID_PRESS_THRESHOLD).tolist()):
        if x != cur_status:
            cur_status = x
            num_flips += 1
            flip_pos.append(i)
    first_flip = flip_pos[0]
    last_flip = flip_pos[-1]

    # if num_flips >= 12 and num_flips <= 14:
    if num_flips == NUM_PASSWORD * 2:
        return True, first_flip, last_flip
    return False, None, None
    
    
# model initializing 
model = FakeModel()

com = get_serial_com()
channels = [[], [], [], []]
X = []
valid_X = []
while True:
    line = com.readline()
    if is_stop_sign(line):
        # convert channels in to X
        min_len = min([len(x) for x in channels])
        for i in range(NUM_KEYS):
            channels[i] = channels[i][:min_len]
        X = np.array(channels).T
        
        # validate X
        ret, fisrt_flip, last_flip  = is_valid_sample(X)
        if not ret:
            com_send_string(com, "invalid signal")
        else:
            valid_X = X[fisrt_flip:last_flip+1]
            # inference with model
            pred = model.predict(valid_X)
            if pred:
                com_send_string(com, "success")
            else:
                com_send_string(com, "fail")
        # reset buffer
        channels.clear()
    else:
        # process data
        try:
            segs = [int(x) for x in line.split(' ') if x != '']
        except:
            continue
        if len(segs) != 2:
            continue
        if segs[0] > 3:
            continue
        channels[segs[0]].append(segs[1])

