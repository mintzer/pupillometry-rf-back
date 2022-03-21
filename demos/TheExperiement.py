# Import relevant modules
import pickle
import random

import pandas as pd
from psychopy import visual, monitors, core
from titta import Titta, helpers_tobii as helpers
import time
from logs_convertion import LogsConversion

global events_df, vars_df, start_time
global tracker

vars_df = pd.DataFrame()
events_df = pd.DataFrame()
start_time = time.time()

# %%  Monitor/geometry
MY_MONITOR = 'testMonitor'  # needs to exists in PsychoPy monitor center
FULLSCREEN = True
SCREEN_RES = [1920, 1080]
SCREEN_WIDTH = 52.7  # cm
VIEWING_DIST = 63  # distance from eye to center of screen (cm)
LOG_FOLDER_PATH = r'logs/'

monitor_refresh_rate = 60  # frames per second (fps)
mon = monitors.Monitor(MY_MONITOR)  # Defined in defaults file
mon.setWidth(SCREEN_WIDTH)          # Width of screen (cm)
mon.setDistance(VIEWING_DIST)       # Distance eye / monitor (cm)
mon.setSizePix(SCREEN_RES)
#im_name = 'im1.jpeg'

# %%  ET settings
et_name = 'Tobii Pro X3-120 EPU'
# et_name = 'IS4_Large_Peripheral'
# et_name = 'Tobii Pro Nano'

dummy_mode = False
bimonocular_calibration = False

# Change any of the default dettings?e
settings = Titta.get_defaults(et_name)
settings.FILENAME = 'testfile.tsv'
settings.N_CAL_TARGETS = 5

win = visual.Window(monitor=mon, fullscr=FULLSCREEN,
                    screen=1, size=SCREEN_RES, units='deg')

fixation_point = helpers.MyDot2(win)
#image = visual.ImageStim(win, image=im_name, units='norm', size=(2, 2))

tracker = Titta.Connect(settings)
if dummy_mode:
    tracker.set_dummy_mode()
tracker.init()

def connect_and_calibrate():
    global tracker
    # %% Connect to eye tracker and calibrate
    # Window set-up (this color will be used for calibration)


     #Calibrate
    if bimonocular_calibration:
        tracker.calibrate(win, eye='left', calibration_number='first')
        tracker.calibrate(win, eye='right', calibration_number='second')
    else:
        tracker.calibrate(win)

    # # %% Record some data
    tracker.start_recording(gaze_data=True, store_data=True)

def update_log(logger, log_data):
    global events_df, vars_df
    if logger == 'events':
        events_df = events_df.append(log_data, ignore_index=True)
    if logger == 'vars':
        events_df = events_df.append(log_data, ignore_index=True)


def now_time():
    return str(1000 * (time.time() - start_time))


# main loop
def main_loop(session_num):
    global events_df, vars_df, start_time

    go = True
    num = 1
    last_color = ''
    last_figure = ''
    color_change = False
    figure_change = False
    while go:
        update_log('events', {'Event': 'TRIALID',
                              'RecordingTimestamp': now_time()})
        figure = random.choice(['X','Y'])
        color = random.choice(['blue','red'])

        if figure != last_figure and last_figure != '':
            figure_change = True
        last_figure = color

        if color != last_color and last_color != '':
            color_change = True
        last_color = color

        if num == 1:
            color = 'red'
        fixation_point.draw()
        win.flip()
        update_log('events',{'Event': '!E TRIAL_EVENT_VAR fixation',
                             'RecordingTimestamp': now_time()})
        core.wait(1)

        visual.TextStim(win, height=2.5, text=figure).draw()
        visual.Rect(win, size=(3,3), lineColor=color).draw()
        #print(time.time())
        win.flip()
        update_log('events', {'Event': '!E TRIAL_EVENT_VAR stimulus_onset',
                              'RecordingTimestamp': now_time()})
        core.wait(1)

        if color == 'red':
            last_red = figure
        if num != 1:
            if random.randint(1,10) == 10:
                go = False

        update_log('vars',{'trial_id': str(num),
                           'figure': figure,
                           'border color': color,
                           'is_color_change': color_change,
                           'is_figure_change': figure_change,
                           'session_num': session_num})

        update_log('events',{
            'Event': 'TRIAL_END',
            'RecordingTimestamp': now_time()})

        num += 1

def stop_and_save_logs():
    global tracker, start_time
    win.flip()
    tracker.stop_recording(gaze_data=True)

    # Close window and save data
    win.close()
    tracker.save_data(mon)  # Also save screen geometry from the monitor object

    # %% Open pickle and write et-data and messages to tsv-files.
    f = open(settings.FILENAME[:-4] + '.pkl', 'rb')
    gaze_data = pickle.load(f)
    msg_data = pickle.load(f)
    timestamp = time.strftime("_%d_%m_%y_%H_%M_%S")

    #  Save data and messages
    df = pd.DataFrame(gaze_data, columns=tracker.header)
    df['UTC'] = df['UTC'].apply(lambda x: str(1000 * (x - start_time)))
    df.to_csv(LOG_FOLDER_PATH + settings.FILENAME[:-4] + timestamp + '.csv', sep=',', index = False)
    #df.to_csv(settings.FILENAME[:-4] + timestamp + '.csv', sep=',')

    #df_msg = pd.DataFrame(msg_data, columns=['system_time_stamp', 'msg'])
    events_df.to_csv(LOG_FOLDER_PATH + settings.FILENAME[:-4] + timestamp + 'events.csv', sep=',', index = False)
    vars_df.to_csv(LOG_FOLDER_PATH + settings.FILENAME[:-4] + timestamp + 'vars.csv', sep=',', index = False)
    #df_msg.to_csv(settings.FILENAME[:-4] + '_msg' + timestamp + '.csv', sep='\t')

    tbi_file = LogsConversion(LOG_FOLDER_PATH + settings.FILENAME[:-4] + timestamp + '.csv')
    tbi_file.convert().save()


def main():
    global tracker
    connect_and_calibrate()
    main_loop(1)
    stop_and_save_logs()


if __name__ == '__main__':
    main()
