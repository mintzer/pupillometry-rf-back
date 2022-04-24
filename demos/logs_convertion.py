# -*- coding: utf-8 -*-

import pandas as pd

class LogsConversion(object):
    def __init__(self, filepath, sep=','):
        self.path = filepath
        self.file = pd.read_csv(filepath, sep=sep)
        self.names_conversion = {
                        #'Unnamed: 0': 'index',
                        'UTC': 'RecordingTimestamp',
                        'device_time_stamp': 'EyetrackerTimestamp',
                        # 'system_time_stamp',
                        'left_pupil_diameter': 'PupilDiameterLeft',
                        'right_pupil_diameter': 'PupilDiameterRight',
                        #'left_pupil_validity': 'ValidityLeft',
                        #'right_pupil_validity': 'ValidityRight',
                        'left_gaze_point_in_user_coordinate_system_z': 'EyePositionLeftZ_RCSmm_',
                        'right_gaze_point_in_user_coordinate_system_z': 'EyePositionRightZ_RCSmm_',
                        #'left_gaze_point_on_display_area_x',
                       #'left_gaze_point_on_display_area_y',
                       # 'left_gaze_point_in_user_coordinate_system_x',
                       # 'left_gaze_point_in_user_coordinate_system_y',
                        # 'left_gaze_origin_in_trackbox_coordinate_system_x',
                         #'left_gaze_origin_in_trackbox_coordinate_system_y',
                         #'left_gaze_origin_in_trackbox_coordinate_system_z',
                         #'left_gaze_origin_in_user_coordinate_system_x',
                         #'left_gaze_origin_in_user_coordinate_system_y',
                         #'left_gaze_origin_in_user_coordinate_system_z',
                        #'left_gaze_origin_validity'
             }

    def convert(self):
        self.file = self.file[(self.file['right_pupil_validity'] == 1) & (self.file['left_pupil_validity'] == 1)] # only trusted data
        self.file = self.file[list(self.names_conversion)] # keep only the relevant columns
        self.file = self.file.rename(self.names_conversion, axis=1)
        return self

    def save(self):
        self.file.to_csv(f'{self.path[:-4]}.tbi', index = False)
        return self


class IsCorrect(object):
    def __init__(self, filepath, sep=','):
        self.path_vars = filepath
        self.path_user_inputs = filepath[:-8] + 'user_inputs.csv'
        self.vars_df = pd.read_csv(filepath, sep=sep)
        self.user_inputs_df = pd.read_csv(self.path_user_inputs, sep=sep)
        self.user_inputs_df = self.user_inputs_df[['block', 'is_correct']]
        #print(self.user_inputs_df)
        self.updated_vars_df = pd.merge(self.vars_df, self.user_inputs_df, on = 'block', how='left')

    def save(self):
        self.updated_vars_df.to_csv(self.path_vars, index = False)
        return self

#g = LogsConversion(r"C:\Python\Titta-master\demos\logs\testfile_11_11_21_14_18_44.tsv")

#g = IsCorrect(r"C:\Python\Titta-master\demos\logs\319314381\run_red_07_04_15_32_vars.csv")
#g.save()