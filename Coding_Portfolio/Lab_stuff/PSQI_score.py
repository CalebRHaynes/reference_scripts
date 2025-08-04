import pandas as pd
import numpy as np
from datetime import datetime, timedelta

df = pd.read_csv("PSQI.csv")

psqi_cols = [col for col in df.columns if col.startswith("PSQI_")]
df = df.dropna(subset=psqi_cols, how='all')

# Data cleaning
# number of minutes, remove question marks
df['PSQI_002'] = pd.to_numeric(df['PSQI_002'].astype(str).str.replace(r'[a-zA-Z?()]', '', regex=True), errors='coerce')
df['PSQI_004'] = pd.to_numeric(df['PSQI_004'].astype(str).str.replace(r'[a-zA-Z?()]', '', regex=True), errors='coerce')

# Calculate Component Scores
# 0 is good 3 is worse sleep score
# Summary Score is sum of 7 component scores- cannot be scored if missing data

'''
Component 1: Subjective Sleep Quality
Component 2: Sleep Latency
Component 3: Sleep Duration
Component 4: Habitual Sleep Efficiency
Component 5: Sleep Disturbances
Component 6: Use of Sleeping Medication
Component 7: Daytime Dysfunction
'''

# Component 1 - Subjective Sleep Quality

# PSQI_016, 0-3
df['Component_1_Subjective_Sleep_Quality'] = pd.to_numeric(df['PSQI_016'], errors='coerce')
df.loc[~df['Component_1_Subjective_Sleep_Quality'].between(0, 3, inclusive='both'), 'Component_1_Subjective_Sleep_Quality'] = pd.NA

# Component 2- Sleep Latency

# Sum of PSQI_002 and PSQI_005:
# Q2 <= 15 min = 0, 16-30 min = 1, 31-60 min = 2, > 60 min = 3
# Q5, 0-3

def score_latency_minutes(minutes):
    if pd.isna(minutes):
        return pd.NA
    elif minutes <= 15:
        return 0
    elif 16 <= minutes <= 30:
        return 1
    elif 31 <= minutes <= 60:
        return 2
    else:
        return 3

df['PSQI_002_Score'] = df['PSQI_002'].apply(score_latency_minutes)
df['PSQI_005'] = pd.to_numeric(df['PSQI_005'], errors='coerce')
df.loc[~df['PSQI_005'].between(0, 3, inclusive='both'), 'PSQI_005'] = pd.NA
df['Component_2_Sum'] = df[['PSQI_002_Score', 'PSQI_005']].sum(axis=1, skipna=False)

# Assign component 2 score based on sum of PSQI_002 and PSQI_005
# 0 = 0, 1-2 = 1, 3-4 = 2, 5-6 = 3
def assign_component_2_score(total_sum):
    if pd.isna(total_sum):
        return pd.NA
    elif total_sum == 0:
        return 0
    elif 1 <= total_sum <= 2:
        return 1
    elif 3 <= total_sum <= 4:
        return 2
    elif 5 <= total_sum <= 6:
        return 3

df['Component_2_SleepLatency'] = df['Component_2_Sum'].apply(assign_component_2_score)

# drop intermediate cols
df.drop(columns=['PSQI_002_Score', 'Component_2_Sum'], inplace=True)

# Component 3: Sleep Duration

# PSQI_004
# >= 7 hours = 0, 6-7 = 1, 5-6 hours = 2, < 5 = 3
df['PSQI_004'] = pd.to_numeric(df['PSQI_004'], errors='coerce')

def score_sleep_duration(hours):
    if pd.isna(hours):
        return pd.NA
    elif hours >= 7:
        return 0
    elif 6 <= hours < 7:
        return 1
    elif 5 <= hours < 6:
        return 2
    elif hours < 5:
        return 3

df['Component_3_SleepDuration'] = df['PSQI_004'].apply(score_sleep_duration)

# Component 4: Habitual Sleep Efficiency

# PSQI_004 (hours of sleep)
# Hours in bed = PSQI_003 time to to PSQI_001 time (sleep to wake)
# Efficiency percentage = PSQI_004/ hours in bed * 100 = %
# Component 4 score:
# > 85% = 0, 75-84% = 1, 65-74% = 2, < 65% = 3

def calculate_hours_in_bed(sleep_time, wake_time):
    if pd.isna(sleep_time) or pd.isna(wake_time):
        return pd.NA
    # Parse times using the correct format
    sleep_time = datetime.strptime(sleep_time, '%I:%M:%S %p')
    wake_time = datetime.strptime(wake_time, '%I:%M:%S %p')
    if wake_time <= sleep_time:
        wake_time += timedelta(days=1)
    # Calculate duration in hours
    duration = (wake_time - sleep_time).total_seconds() / 3600
    return duration

# Apply the function to calculate Hours_in_Bed
df['Hours_in_Bed'] = df.apply(lambda row: calculate_hours_in_bed(row['PSQI_001'], row['PSQI_003']), axis=1)

# Calculate efficiency with cap at 100%
df['Sleep_Efficiency_Pct'] = (df['PSQI_004'] / df['Hours_in_Bed']) * 100
df['Sleep_Efficiency_Pct'] = df['Sleep_Efficiency_Pct'].apply(lambda x: min(x, 100) if x > 100 else x)

def score_sleep_efficiency(efficiency):
    if pd.isna(efficiency):
        return pd.NA
    elif efficiency >= 85:
        return 0
    elif 75 <= efficiency < 85:
        return 1
    elif 65 <= efficiency < 75:
        return 2
    else:
        return 3

df['Component_4_HabitualSleepEfficiency'] = df['Sleep_Efficiency_Pct'].apply(score_sleep_efficiency)
df.drop(columns=['Sleep_Efficiency_Pct'], inplace=True)

# Component 5: Step Disturbances
# sum of PSQI_006, PSQI_007, PSQI_008, PSQI_009, PSQI_010, PSQI_0011
# PSQI_012, PSQI_013, PSQI_015

# Component 5 score: 0 = 0, 1-9 = 1, 10-18=2, 19-27 = 3
df['Component_5_SleepDisturbances'] = df[['PSQI_006', 'PSQI_007', 'PSQI_008', 'PSQI_009', 'PSQI_010', 'PSQI_011', 'PSQI_012', 'PSQI_013', 'PSQI_015']].sum(axis=1)

def score_step_disturbances(value):
    if pd.isna(value):
        return pd.NA
    elif value == 0:
        return 0
    elif 1 <= value <= 9:
        return 1
    elif 10 <= value <= 18:
        return 2
    else:
        return 3

df['Component_5_SleepDisturbances'] = df['Component_5_SleepDisturbances'].apply(score_step_disturbances)

# Component 6: Use of Sleeping medication

#PSQI_017, 0-3
df['Component_6_SleepingMedication'] = df['PSQI_017']

# Component 7: Daytime Dysfunction

# Sum of: PSQI_018, 0-3; PSQI_019, 0-3
# Component Score
#0 = 0, 1-2 = 1, 3-4 = 2, 5-6 = 3

df['Component_7_DaytimeDysfunction'] = df[['PSQI_018', 'PSQI_019']].sum(axis=1)

def score_daytime_dysfunction(value):
    if pd.isna(value):
        return pd.NA
    elif value == 0:
        return 0
    elif 1 <= value <= 2:
        return 1
    elif 3 <= value <= 4:
        return 2
    else:
        return 3

df['Component_7_DaytimeDysfunction'] = df['Component_7_DaytimeDysfunction'].apply(score_daytime_dysfunction)

# Global Score is Sum of Components 1-7
df['Global_Score'] = df[['Component_1_Subjective_Sleep_Quality',
                         'Component_2_SleepLatency',
                         'Component_3_SleepDuration',
                         'Component_4_HabitualSleepEfficiency',
                         'Component_5_SleepDisturbances',
                         'Component_6_SleepingMedication',
                         'Component_7_DaytimeDysfunction'
                         ]].sum(axis=1, skipna=False)


df.to_csv("PSQI_scored.csv", index = False)


