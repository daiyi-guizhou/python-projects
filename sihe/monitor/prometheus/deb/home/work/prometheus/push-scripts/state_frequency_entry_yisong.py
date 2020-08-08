import requests
import time
import json
from workstatus import *

default_tags = {"cluster":"detection"}

# -1 -> Unknown state | flawck inactive
latestState = -1
stateChangeInLastDuration = []

stateStep = 1
frequencyStep = 60
pushInterval = 60
state_change_amount = 0


def service_start_rule():
    return True, 'state_frequency_entry_yisong.py'


def pushForStateStaff():
    updated_state_history = getUpdatedStateHistory()
    t = getTimeStamp()
    pushForStateChangeFreq(updated_state_history, t)


def pushForStateChangeFreq(updated_state_history, t):
    global state_change_amount
    # get the time of state change in the last minute
    oneMinuteAgo = t - 60
    _stateChangeInLastDuration = []
    global stateChangeInLastDuration
    # search the last list
    if len(stateChangeInLastDuration) > 0:
        for state in stateChangeInLastDuration:
            if state > oneMinuteAgo:
                _stateChangeInLastDuration.append(state)
    # search the updated list
    if len(updated_state_history) > 0:
        for record in updated_state_history:
            # if the flawck is inactive, -1 state is keep receiving
            # need to skip them to get correct frequency
            if record['state'] == -1:
                continue
            timestamp = round(record['entrytime'] / 1000)
            if timestamp > oneMinuteAgo:
                _stateChangeInLastDuration.append(timestamp)
    frequency = len(_stateChangeInLastDuration)
    state_change_amount = state_change_amount + frequency 
    stateChangeInLastDuration = _stateChangeInLastDuration
    push_one(metrics='state_change_count', values=state_change_amount,
                tag=default_tags)


def pushForStateHistory(updated_state_history, t):
    payload_list = []
    stateFreq = [0, 0, 0, 0, 0]
    for record in updated_state_history:
        stateFreq[record['state']] += 1
    for state in range(5):
        stateTag = default_tags.copy()
        stateTag['S'] = state
        if state == 4:
            stateTag['blow'] = getBlowDevice()
        if stateFreq[state]:
            push_one(metrics='state_entry',
                     values=stateFreq[state], tag=stateTag)


def main():
    pushForStateStaff()
