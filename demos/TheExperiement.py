# coding: utf-8
# Import relevant modules
import pickle
import random

import pandas as pd
from psychopy import visual, monitors, core, event
from titta import Titta, helpers_tobii as helpers
import time
from logs_convertion import LogsConversion, IsCorrect

global events_df, vars_df, start_time
global tracker

# %%  Monitor/geometry

subject = '2'
COLORS = ['red'] #, 'red', 'red', 'red']
#COLORS = ['blue', 'blue', 'blue', 'blue']

#COLORS = ['blue', 'red']
# number of blocks
BLOCKS = 1
# NON_DOMINANT = 'red'
# DOMINANT = 'blue'
MY_MONITOR = 'testMonitor'  # needs to exists in PsychoPy monitor center
FULLSCREEN = True
SCREEN_RES = [1920, 1080] #[2560, 1440]
SCREEN_WIDTH = 52.7  # cm
VIEWING_DIST = 63  # distance from eye to center of screen (cm)
LOG_FOLDER_PATH = r'logs/'
heb_colors = {'red': 'אדום',
              'blue': 'כחול'}
keys_conversion = {'x': 'q', 'X': 'q', 'o': 'p', 'O': 'p'}

monitor_refresh_rate = 60  # frames per second (fps)
mon = monitors.Monitor(MY_MONITOR)  # Defined in defaults file
mon.setWidth(SCREEN_WIDTH)          # Width of screen (cm)
mon.setDistance(VIEWING_DIST)       # Distance eye / monitor (cm)
mon.setSizePix(SCREEN_RES)
#im_name = 'im1.jpeg'

# %%  ET settings
et_name = 'Tobii Pro X3-120' # EPU
# et_name = 'IS4_Large_Peripheral'
# et_name = 'Tobii Pro Nano'

dummy_mode = False
bimonocular_calibration = False

# Change any of the default dettings?e
settings = Titta.get_defaults(et_name)
settings.FILENAME = 'run'
settings.N_CAL_TARGETS = 5

#image = visual.ImageStim(win, image=im_name, units='norm', size=(2, 2))

def connect_and_calibrate():
    global tracker, win
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
    global events_df, vars_df, input_df
    if logger == 'events':
        events_df = events_df.append(log_data, ignore_index=True)
    if logger == 'vars':
        vars_df = vars_df.append(log_data, ignore_index=True)
    if logger == 'input':
        input_df = input_df.append(log_data, ignore_index=True)


def now_time():
    return str(round(1000 * (time.time() - start_time)))

# main loop
def main_loop(block_num):
    global events_df, vars_df, start_time, fixation_point, win
    #prints text to the screen
    visual.TextStim(win,
                    text=f"ברוכה הבאה לבלוק מספר "
                         f"{block_num + 1}!\n"
                         f"תזכורת: בכל רגע נתון תצטרכי לזכור\n"
                         f"מה היא האות האחרונה\n"
                         f"שהופיעה בצבע "
                         f"{heb_colors[DOMINANT]}\n\n"
                         f"בנוסף, בכל צעד:\n"
                         f"אם מופיעה האות X - לחצי על Q\n"
                         f"אם מופיעה האות O - לחצי על P\n"
                         f"\n\nלחצי על כל כפתור כדי להמשיך",
                    languageStyle='RTL',
                    color=DOMINANT).draw()
    # updates the screen
    win.flip()

    # initial vars
    go = True
    num = 0
    last_color = ''
    last_figure = ''
    last_dominant = ''
    event.waitKeys()
    # until go == False
    while go:
        first_step = False
        # DEFINE TASK PARAMETERS ---
        # randomly choosing figure
        figure = random.choice(['X','O'])

        if last_color != '':
            # 5:3 ratio
            color = random.choice(['blue', 'red', 'blue', 'red', 'blue', 'red', last_color, last_color])
        else:
            color = random.choice(['blue', 'red'])
        if num == 0:
            color = DOMINANT
            first_step = True
        update = False
        color_change = False
        figure_change = False
        if figure != last_figure and last_figure != '':
            figure_change = True
        # saving the last figure for next iteration
        last_figure = figure

        if color != last_color and last_color != '':
            color_change = True
        # saving the last color for next iteration
        last_color = color
        # STEP 1 - INITIAL FIXATION
        # drawing fixation point
        fixation_point.draw()
        # updates the screen
        win.flip()
        # updating the events log
        update_log('events', {'Event': 'TRIALID',
                              'RecordingTimestamp': now_time()})
        update_log('events',{'Event': '!E TRIAL_EVENT_VAR fixation',
                             'RecordingTimestamp': now_time()})
        # letting the fixation point appear 1 second
        core.wait(1)

        # STEP 2 - DRAWING STIMULUS
        # record the start time of the trial
        trial_start_time = time.time()

        visual.TextStim(win,text=figure, color=color, height=4.5).draw()
        #visual.Rect(win, size=(4,4), lineColor=color).draw()
        #print(time.time())
        # updates the screen
        win.flip()
        # updating the events log
        update_log('events', {'Event': '!E TRIAL_EVENT_VAR stimulus_on',
                              'RecordingTimestamp': now_time()})

        # wait for the user to press q or p
        pressed_key = event.waitKeys(keyList=['q', 'p'])

        #core.wait(2)
        fixation_point.draw()
        # updates the screen
        win.flip()
        time_passed = time.time() - trial_start_time # in seconds
        time_left = 3.5 - time_passed
        core.wait(time_left)
        update_log('events', {'Event': '!E TRIAL_EVENT_VAR stimulus_off',
                              'RecordingTimestamp': now_time()})

        # fixation to complete 3 seconds from the start of the trial
        # calculate the time that has passed since the start of the trial
        # and wait for the remaining time to complete 3 seconds

        #win.flip()

        if color == DOMINANT:
            last_dominant = figure
            update = True
        if num > 2:
            if random.randint(1,10) == 1:
                go = False
        if num >= 14:
            go = False
        update_log('vars', {'trial_id': str(num),
                            'figure': figure,
                            'border_color': color,
                            'is_color_change': color_change,
                            'is_figure_change': figure_change,
                            'is_update': update,
                            'is_first': first_step,
                            'pressed_key': pressed_key[0],
                            'is_correct_key': pressed_key[0] == keys_conversion[figure],
                            'rt': time_passed,
                            'dominant': DOMINANT,
                            'block': f'b_{block_num}'})
        num += 1
        update_log('events',{
            'Event': 'TRIAL_END',
            'RecordingTimestamp': now_time()})

    # STEP 5 - PROBE ( OUT OF LOOP)
    visual.TextStim(win, text=f"מה האות האחרונה שהופיעה ב"
                              f"{heb_colors[DOMINANT]}?\n"
                              f"אם X - לחצי Q\n"
                              f"אם O - לחצי P\n",
                    languageStyle='RTL', color=DOMINANT).draw()
    # add input from user
    # drop block when user got wrong answer
    win.flip()
    key = event.waitKeys()[0] # waiting for input
    print(key)
    print(str.lower(key) == keys_conversion[last_dominant])
    update_log('input', {'pressed_key': key,
                         'last_dominant': last_dominant,
                        'is_correct': str.lower(key) == keys_conversion[last_dominant],
                        'block': f'b_{block_num}'})

def stop_and_save_logs():
    global tracker, start_time, win,  vars_df
    win.flip()
    tracker.stop_recording(gaze_data=True)

    # Close window and save data
    win.close()
    tracker.save_data(mon)  # Also save screen geometry from the monitor object

    # %% Open pickle and write et-data and messages to tsv-files.
    f = open(settings.FILENAME + '.pkl', 'rb')
    gaze_data = pickle.load(f)
    msg_data = pickle.load(f)
    timestamp = time.strftime("%d_%m_%H_%M")
    main_path = f'{LOG_FOLDER_PATH}{subject}/{settings.FILENAME}_{DOMINANT}_{timestamp}'
    #  Save data and messages
    df = pd.DataFrame(gaze_data, columns=tracker.header)
    #print(df)
    df['UTC'] = df['UTC'].apply(lambda x: str(round(1000 * (x - start_time))))
    df.to_csv(main_path + '.csv', sep=',', index = False)
    #df.to_csv(settings.FILENAME + timestamp + '.csv', sep=',')
    #print(events_df)
    #df_msg = pd.DataFrame(msg_data, columns=['system_time_stamp', 'msg'])
    events_df.to_csv(main_path + '_events.csv', sep=',', index = False)
    vars_df['is_color_change'] = vars_df['is_color_change'].map({True: 'color_change', False: 'no_color_change'})
    vars_df['is_figure_change'] = vars_df['is_figure_change'].map({True: 'figure_change', False: 'no_figure_change'})
    vars_df['is_update'] = vars_df['is_update'].map({True: 'update', False: 'no_update'})
    vars_df['is_first'] = vars_df['is_first'].map({True: 'first', False: 'not_first'})
    vars_df['is_correct_key'] = vars_df['is_correct_key'].map({True: 'correct', False: 'incorrect'})
    vars_df.to_csv(main_path + '_vars.csv', sep=',', index = False)
    #df_msg.to_csv(settings.FILENAME + '_msg' + timestamp + '.csv', sep='\t')
    input_df['is_correct'] = input_df['is_correct'].map({True: 'correct', False: 'incorrect'})
    input_df.to_csv(main_path + '_user_inputs.csv', sep=',', index=False)
    tbi_file = LogsConversion(main_path + '.csv')
    tbi_file.convert().save()
    vars_df = IsCorrect(main_path + '_vars.csv')
    vars_df.save()

def show_summary():
    print(f'total time: {round(time.time() - start_time)} seconds\n\
          number of blocks: {BLOCKS}')

def main():
    global tracker, fixation_point, win, start_time, DOMINANT, vars_df, events_df, input_df
    from pathlib import Path
    experiment_start_time = time.time()
    Path(fr"logs/{subject}").mkdir(parents=True, exist_ok=True)
    for color in COLORS:
        vars_df = pd.DataFrame()
        events_df = pd.DataFrame()
        input_df = pd.DataFrame()
        start_time = time.time()
        win = visual.Window(monitor=mon, fullscr=FULLSCREEN,
                            screen=1, size=SCREEN_RES, units='deg')
        fixation_point = helpers.MyDot2(win)
        tracker = Titta.Connect(settings)
        if dummy_mode:
            tracker.set_dummy_mode()
        tracker.init()
        DOMINANT = color
        visual.TextStim(win,
                       text=f"ברוכה הבאה! :)\n"
                            f"הניסוי מורכב משתי הוראות פשוטות:\n\n"
                            f"1. בכל שלב תופיע על\n"
                            f"המסך אות אחת: "
                            f"X או O\n"
                            f"אם הופיעה האות X - הקישי על Q\n"
                            f"אם הופיעה האות O - הקישי על P\n\n"
                            f"2. החזיקי כל הזמן בראש מה\n"
                            f"הייתה האות האחרונה בצבע "
                            f"{heb_colors[DOMINANT]}\n\n"
                            f"לחצי על כל כפתור כדי להמשיך",
                       languageStyle='RTL', color=DOMINANT).draw()
        win.flip()
        event.waitKeys()
        connect_and_calibrate()
        for i in range(BLOCKS):
            main_loop(i)
        stop_and_save_logs()
        show_summary()

if __name__ == '__main__':
    main()
