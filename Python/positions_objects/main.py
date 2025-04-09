import pandas as pd
from matplotlib import pyplot as plt
from plotting.plot_data import make_boxplots_interaction, make_boxplots_interaction_count
from imports.import_data import extract_sampling_across_positions, extract_sampling_per_id, generateBodyDescriptives, \
    generateManualDescriptives

timepoint = 'T3'
extract_data = 0
DIR = 'G:/Mój dysk/POSITION_TOY_9MO/SCRIPTS/clean_code/data/'
OUT_DIR = 'G:/Mój dysk/POSITION_TOY_9MO/SCRIPTS/clean_code/plots/'

if extract_data:
    body = generateBodyDescriptives(DIR,timepoint)
    manual = generateManualDescriptives(DIR, timepoint)
    sampling_across_positions = extract_sampling_across_positions(DIR, timepoint, body, manual)
    sampling_per_id = extract_sampling_per_id(DIR, sampling_across_positions[sampling_across_positions['Tier'] != 'mouthing'], timepoint)

# Load data
else:
    sampling_across_positions = pd.read_csv(DIR + timepoint + '/sampling_across_positions.csv', index_col=0)
    sampling_per_id = pd.read_csv(DIR + timepoint + '/sampling_across_positions_counts.csv', index_col=0)

sampling_across_positions = sampling_across_positions[sampling_across_positions['Tier'] != 'mouthing'].reset_index(drop=True)
sampling_per_id = sampling_per_id[sampling_per_id['count'] > 0].reset_index(drop=True)

df_sit = sampling_across_positions[sampling_across_positions['Position'] == 'Sitting']
df_non = sampling_across_positions[sampling_across_positions['Position'] != 'Sitting']

sampling_per_id_sit = sampling_per_id[sampling_per_id['Condition'] == 'Independent sitting']
sampling_per_id_non = sampling_per_id[sampling_per_id['Condition'] == 'Other']

df_sit_mdn = df_sit.groupby(['id', 'Affordances', 'Condition'])['Duration'].median().reset_index(drop=False)
df_non_mdn = df_non.groupby(['id', 'Affordances', 'Condition'])['Duration'].median().reset_index(drop=False)

make_boxplots_interaction(df_sit_mdn, df_non_mdn,
                          y_var='Duration',
                          toys=['graspable', 'stationary'],
                          colors={"graspable": "#2bc3db",
                         "stationary": "#bfd739"},
                          toy_images={'graspable':
                            {'dino_img': plt.imread(DIR + timepoint + '/images/dino.png'),
                            'bubbles_img': plt.imread(DIR + timepoint + '/images/bubbles.png')},
                          'stationary':
                            {'klickity_img': plt.imread(DIR + timepoint + '/images/klickity.png'),
                            'spinner_img': plt.imread(DIR + timepoint + '/images/spinner.png')}},
                          fig_size=(10, 10),
                          save_name=f"{OUT_DIR}/{timepoint}/boxplots_interaction_mdn.png",
                          )

make_boxplots_interaction_count(sampling_per_id_sit, sampling_per_id_non,
                          y_var='count_per_min',
                          toys=['graspable', 'stationary'],
                          colors={"graspable": "#2bc3db",
                         "stationary": "#bfd739"},
                          toy_images={'graspable':
                            {'dino_img': plt.imread(DIR + timepoint + '/images/dino.png'),
                            'bubbles_img': plt.imread(DIR + timepoint + '/images/bubbles.png')},
                          'stationary':
                            {'klickity_img': plt.imread(DIR + timepoint + '/images/klickity.png'),
                            'spinner_img': plt.imread(DIR + timepoint + '/images/spinner.png')}},
                          fig_size=(10, 10),
                          save_name=f"{OUT_DIR}{timepoint}/vboxplots_count_interaction.png",
                          )


