import pandas as pd
import numpy as np
import pympi
import glob
import os

def assign_task_bin(row, times, bins, ini_threshold=0):
    """
    Assigns a time bin to an event based on its StartTime and EndTime.

    Parameters:
    - row (Series): A Pandas row containing 'StartTime' and 'EndTime' values.
    - times (list): A list of time thresholds (in milliseconds) defining bin limits.
    - bins (list): A list of labels corresponding to the time bins.
    - ini_threshold (int, optional): If set, ignores events that start before this threshold. Default is 0.

    Returns:
    - str: The assigned bin label (e.g., '0-1', '1-2', etc.).
    - 'Undefined': If the event extends beyond the allowed 25% threshold of a bin.
    - '5+': If the event starts beyond 300,000 ms.

    Logic:
    - If an event fully fits within a bin, it is assigned to that bin.
    - If an event crosses a bin boundary but extends no more than 25% beyond it, it remains in the original bin.
    - If an event extends beyond 25% of a bin, it is marked as 'Undefined'.
    - If an event starts at or beyond 300,000 ms, it is assigned to '5+'.

    """
    for bin, thr in zip(times, bins):
        if ini_threshold and row['StartTime'] < ini_threshold:
            continue  # Ignore events before the initial threshold

        if row['StartTime'] <= bin and row['EndTime'] <= bin:
            return thr  # Event fully within the bin

        if row['StartTime'] <= bin and row['EndTime'] > bin:
            if row['EndTime'] <= bin + 0.25 * bin:
                return thr  # Event extends within allowed range
            else:
                return 'Undefined'  # Event extends too far

    if row['StartTime'] >= 300000:
        return '5+'

    return 'Undefined'  # If no bin matches
def generateBodyDescriptives(DIR, timepoint):
    """
       Extracts and processes body movement annotation data from ELAN (.eaf) files,
       compiling them into a structured dataset.

       Parameters:
       timepoint (str): The timepoint directory containing the ELAN files.

       Returns:
       pd.DataFrame: A DataFrame containing the extracted body movement data,
                     sorted by ID and start time, and saved as a CSV file.
    """
    data_pos = {}
    for file in glob.glob(DIR + timepoint + '/body/*/*.eaf'):
        elan_file = pympi.Elan.Eaf(file)
        filename = os.path.basename(file)[:7]
        df_pos = pd.DataFrame(columns=['StartTime', 'EndTime', 'Duration', 'Tier'])

        for tier in elan_file.get_tier_names():
            if tier != 'Claps':
                for ann in elan_file.get_annotation_data_for_tier(tier):
                    if ann[2] == "":
                        df3 = pd.DataFrame(
                            {'id': filename, 'TimePoint': filename[-1], 'StartTime': ann[0], 'EndTime': ann[1], 'Duration': ann[1] - ann[0],
                             'Tier': tier}, index=[0])
                        df_pos = pd.concat([df_pos, df3], ignore_index=True)

                data_pos[filename] = df_pos.sort_values('StartTime').reset_index(drop=True)

    body = pd.concat(data_pos.values(), ignore_index=True)
    body = body.sort_values(['id', 'StartTime']).reset_index(drop=True)
    body.to_csv(DIR + timepoint + '/body.csv')
    return body

def generateManualDescriptives(DIR, timepoint):
    """
        Extracts and processes manual annotation data from ELAN (.eaf) files,
        focusing on specific tiers related to object handling.

        Parameters:
        timepoint (str): The timepoint directory containing the ELAN files.

        Returns:
        pd.DataFrame: A DataFrame containing the extracted manual annotation data,
                      sorted by ID and start time, and saved as a CSV file.
    """
    data_manual = {}
    tiers_analysis = ['inhand_right_child', 'inhand_left_child']
    for file in glob.glob(DIR + timepoint + '/manual/*/*.eaf'):

        elan_file = pympi.Elan.Eaf(file)
        filename = os.path.basename(file)[:7]
        df_man = pd.DataFrame(columns=['StartTime', 'EndTime', 'Duration', 'Tier', 'Label'])
        for tier in elan_file.get_tier_names():
            if tier in tiers_analysis:
                for ann in elan_file.get_annotation_data_for_tier(tier):
                    if ann[2] != "":
                        df2 = pd.DataFrame({'id': filename, 'TimePoint': filename[-1], 'StartTime': ann[0], 'EndTime': ann[1],
                                            'Duration': ann[1] - ann[0], 'Tier': tier, 'Label': ann[2]}, index=[0])
                        df_man = pd.concat([df_man, df2], ignore_index=True)

                data_manual[filename] = df_man.sort_values('StartTime').reset_index(drop=True)
    manual = pd.concat(data_manual.values(), ignore_index=True)

    manual = manual.sort_values(['id', 'StartTime'])
    manual.to_csv(DIR + timepoint + '/manual.csv')
    return manual

def check_sitting(row, participant_data_bod):
    new_row = pd.Series(dtype=float)
    new_row['Label'] = row['Label']
    new_row['Tier'] = row['Tier']
    new_row['id'] = row['id']
    new_row['StartTime'] = np.nan
    new_row['EndTime'] = np.nan

    for idx, sitting_ep in participant_data_bod.iterrows():
        if (row['StartTime'] < sitting_ep['EndTime']) & (row['EndTime'] > sitting_ep['StartTime']):
            if row['StartTime'] < sitting_ep['StartTime']:
                new_row['StartTime'] = sitting_ep['StartTime']
            elif row['StartTime'] >= sitting_ep['StartTime']:
                new_row['StartTime'] = row['StartTime']
            else:
                continue
            if row['EndTime'] > sitting_ep['EndTime']:
                new_row['EndTime'] = sitting_ep['EndTime']

            elif row['EndTime'] <= sitting_ep['EndTime']:
                new_row['EndTime'] = row['EndTime']
            else:
                continue
            return new_row
        else:
            continue

    return new_row

def calculate_sampling_across_positions(manual,
                                        body,
                                        position,
                                        toys):

    sampling_across_positions = pd.DataFrame(
        columns=['StartTime', 'EndTime', 'Duration', 'Tier', 'Label', 'Position', 'id'])
    manual['Label'] = manual['Label'].apply(lambda x: x if x in toys else np.nan)
    limbs_dict = {}

    for limb, label in zip(['inhand_left_child', 'inhand_right_child'],
                           ['change_left', 'change_right']):
        manual_cop = manual.copy()
        manual_cop['Tier'] = manual_cop['Tier'].apply(lambda x: x if x == limb else np.nan)
        manual_cop = manual_cop.dropna()
        limbs_dict[label] = manual_cop

    body['Tier'] = body['Tier'].apply(lambda x: x if x in position else np.nan)
    body = body.dropna()
    body = body[body['Duration'] > 3000]

    participants = manual['id'].unique()

    rows = ['change_left', 'change_right']

    for idx, participant in enumerate(participants):

        participant_data_bod = body[body['id'] == participant].reset_index(drop=True)

        for name, group in participant_data_bod.groupby('Tier'):

            for pos, row in zip(range(len(rows)), rows):
                manual_df = limbs_dict[row].copy()
                participant_data_man = manual_df[manual_df['id'] == participant].reset_index(drop=True)

                if len(group) != 0:
                    df_man = participant_data_man.copy()
                    df_man_cop = df_man.apply(lambda sampling_ep: check_sitting(sampling_ep, group), axis=1)

                    if isinstance(df_man_cop, pd.Series):
                        if (df_man_cop['StartTime'].isna()) | (df_man_cop['EndTime'].isna()):
                            df_man_cop = pd.DataFrame()

                    elif isinstance(df_man_cop, pd.DataFrame):
                        df_man_cop = df_man_cop.dropna(subset=['StartTime', 'EndTime'])

                    if not df_man_cop.empty:
                        df_man_cop['Position'] = name
                        df_man_cop['Duration'] = df_man_cop['EndTime'] - df_man_cop['StartTime']
                        df_man_cop[['StartTime', 'EndTime', 'Duration', 'id']] = df_man_cop[
                            ['StartTime', 'EndTime', 'Duration', 'id']].astype(int)

                    else:
                        df_man_cop = pd.DataFrame()

                else:
                    df_man_cop = pd.DataFrame()

                sampling_across_positions = pd.concat([sampling_across_positions, df_man_cop], axis=0)

    return sampling_across_positions.reset_index(drop=True)

def extract_sampling_across_positions(DIR, timepoint, body_or=None, manual_or=None):
    if manual_or is None:
        manual_or = pd.read_csv(DIR + timepoint + '/manual.csv', index_col=0)
    if body_or is None:
        body_or = pd.read_csv(DIR + timepoint + '/body.csv', index_col=0)

    manual = manual_or.copy()
    body = body_or.copy()

    manual['id'] = manual['id'].transform(lambda x: x[:5]).astype(int)
    body['id'] = body['id'].transform(lambda x: x[:5]).astype(int)

    all_positions = [x for x in body['Tier'].unique() if x not in ["Claps", 'Undefined']]

    sampling_across_positions = calculate_sampling_across_positions(manual=manual,
                                                                    body=body,
                                                                    position=all_positions,
                                                                    toys=['bubbles', 'dino', 'klickity', 'spinner'])


    sitting = sampling_across_positions[sampling_across_positions['Position'] == 'Sitting']
    sitting['Condition'] = ['Independent sitting'] * len(sitting)
    id_sitters = sitting['id'].to_numpy()

    sampling_across_positions['sitter_yes_no'] = sampling_across_positions['id'].isin(id_sitters)
    sampling_across_positions['Duration'] = sampling_across_positions['Duration'] / 1000
    sampling_across_positions = sampling_across_positions[['Duration', 'Tier', 'Label', 'Position', 'id']]

    map_toys = {'bubbles': 'graspable',
                'dino': 'graspable',
                'klickity': 'stationary',
                'spinner': 'stationary'}

    sampling_across_positions['Affordances'] = sampling_across_positions['Label'].replace(map_toys)
    sampling_across_positions['Condition'] = sampling_across_positions['Position'].apply(lambda x: 'Independent sitting' if x=='Sitting' else 'Other')
    sampling_across_positions.to_csv(DIR + timepoint + '/sampling_across_positions.csv')

    print(f'File saved successfully inside {DIR}/data/{timepoint}/')
    return sampling_across_positions

def extract_sampling_per_id(DIR, sampling_across_positions, timepoint):
    length = pd.read_excel(DIR + timepoint + '/length_T3.xlsx')[['id', 'video_length']]

    all_combinations = pd.MultiIndex.from_product(
        [sampling_across_positions['id'].unique(),
         sampling_across_positions['Affordances'].unique(),
         sampling_across_positions['Condition'].unique()],
        names=['id', 'Affordances', 'Condition']
    )
    # Group by id, Label, and Position to calculate count and median
    grouped = sampling_across_positions.groupby(['id', 'Affordances', 'Condition'])['Duration'].agg(['count', 'sum'])
    grouped = grouped.reindex(all_combinations).reset_index()
    grouped['count'] = grouped['count'].fillna(0)
    grouped['sum'] = grouped['sum'].fillna(0)
    grouped['count'] = grouped['count'].astype(int)

    grouped = grouped.merge(length, on='id', how='left')
    grouped['count_per_min'] = grouped['count'] / (grouped['video_length'] / 60000)
    grouped['time_s_per_min'] = (grouped['sum']) / (grouped['video_length'] / 60000).fillna(0) # time in seconds spent sampling in the specific position per minute
    grouped.to_csv(DIR + timepoint + '/sampling_across_positions_counts.csv')
    grouped[grouped['count'] > 0].to_csv(DIR + timepoint + '/art_anova_count.csv')

    print(f'File saved successfully inside /data/{timepoint}/')
    return grouped