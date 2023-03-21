from utils import *
from models import *

import numpy as np

TERMINATE_SIGNAL = "stop"
VALID_PRESS_THRESHOLD = 100
NUM_PASSWORD = 6

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
X = []
valid_X = []
while True:
    line = com.readline()
    if is_stop_sign(line):
        ret, fisrt_flip, last_flip  = is_valid_sample(X)
        if not ret:
            com_send_string(com, "invalid signal")
        else:
            valid_X.append(X[fisrt_flip:last_flip+1])
            # inference with model
            pred = model.predict(valid_X)
            if pred:
                com_send_string(com, "success")
            else:
                com_send_string(com, "fail")
        # reset buffer
        X.clear()
        valid_X.clear()
    else:
        import pdb
        pdb.set_trace()

