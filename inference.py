from utils import *
from models import *

import numpy as np

TERMINATE_SIGNAL = "Ready"
VALID_PRESS_THRESHOLD = 100
NUM_PASSWORD = 6
NUM_KEYS = 4
def parse_line(line):
    line = line.decode().strip()
    return line

def is_stop_sign(line):
    if line == TERMINATE_SIGNAL:
        print("Received signals, trigger inferencing")
        return True
    return False    


def is_clear_sign(line):
    if line == "Clear":
        return True
    return False

def is_valid_sample(X):
    num_flips = 0
    cur_status = False
    flip_pos = []
    last_flip = 0

    X_sum = np.sum(X, axis=1)
    for i, x in enumerate((X_sum > VALID_PRESS_THRESHOLD).tolist()):
        if x != cur_status:
            cur_status = x
            num_flips += 1
            flip_pos.append(i)
        if X_sum[i] > VALID_PRESS_THRESHOLD:
            last_flip = i
    
    first_flip = flip_pos[0]
    last_flip = X.shape[0]
    print(f"num_flips={num_flips}")
    # if num_flips >= 12 and num_flips <= 14:
    if num_flips in [NUM_PASSWORD * 2 - 1, NUM_PASSWORD * 2]:
        return True, first_flip, last_flip
    return False, None, None

def com_send_string(com, str):
    com.write(bytes(str.encode()))
    
    
# model initializing 
model = FakeModel()

com = get_serial_com()
channels = [[], [], [], []]

while True:
    line = parse_line(com.readline())
    print(line)
    if is_clear_sign(line):
        channels = [[], [], [], []]
    elif is_stop_sign(line):
        # convert channels in to X
        min_len = min([len(x) for x in channels])
        for i in range(NUM_KEYS):
            channels[i] = channels[i][:min_len]
        X = np.array(channels).T
        
        # validate X
        ret, fisrt_flip, last_flip  = is_valid_sample(X)
        if not ret:
            com_send_string(com, "Invalid Signal")
        else:
            valid_X = X[fisrt_flip:last_flip]
            # if X.sum() != valid_X.sum():
            #     import pdb
            #     pdb.set_trace()
            # inference with model
            pred = model.predict(valid_X)
            if pred:
                com_send_string(com, "Success")
            else:
                com_send_string(com, "Fail")
        # reset buffer
        channels = [[], [], [], []]
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

