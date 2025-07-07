from plotting.plot_data import make_boxplots_interaction, make_boxplots_interaction_count
from imports.import_data import extract_sampling_across_positions, extract_sampling_per_id, generateBodyDescriptives, \
    generateManualDescriptives

DIR = ''
OUT_DIR = ''

body = generateBodyDescriptives(DIR)
manual = generateManualDescriptives(DIR)
sampling_across_positions = extract_sampling_across_positions(DIR, body, manual)
sampling_per_id = extract_sampling_per_id(DIR)

sampling_per_id = sampling_per_id[sampling_per_id['count'] > 0].reset_index(drop=True)

df_sit = sampling_across_positions[sampling_across_positions['Position'] == 'Independent sitting']
df_non = sampling_across_positions[sampling_across_positions['Position'] != 'Sitting']

sampling_per_id_sit = sampling_per_id[sampling_per_id['Position'] == 'Independent sitting']
sampling_per_id_non = sampling_per_id[sampling_per_id['Position'] == 'Other']

df_sit_mdn = df_sit.groupby(['id', 'Object', 'Position'])['Duration'].median().reset_index(drop=False)
df_non_mdn = df_non.groupby(['id', 'Object', 'Position'])['Duration'].median().reset_index(drop=False)

make_boxplots_interaction(df_sit_mdn, df_non_mdn,
                          y_var='Duration',
                          toys=['graspable', 'stationary'],
                          colors={"graspable": "#2bc3db",
                                  "stationary": "#bfd739"},
                          toy_images={'graspable':
                                            {'dino_img': 'PATH',
                                            'bubbles_img': 'PATH'},
                                       'stationary':
                                            {'klickity_img': 'PATH',
                                            'spinner_img': 'PATH'}},
                          fig_size=(10, 10),
                          )

make_boxplots_interaction_count(sampling_per_id_sit, sampling_per_id_non,
                          y_var='count_per_min',
                          toys=['graspable', 'stationary'],
                          colors={"graspable": "#2bc3db",
                                  "stationary": "#bfd739"},
                          toy_images={'graspable':
                                            {'dino_img': 'PATH',
                                             'bubbles_img': 'PATH'},
                                        'stationary':
                                            {'klickity_img': 'PATH',
                                             'spinner_img': 'PATH'}},
                          fig_size=(10, 10),
                          )