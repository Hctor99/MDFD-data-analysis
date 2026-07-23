import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('bmh')
plt.rcParams['axes.facecolor'] = '#eaeaf2'  # light bluish-gray
plt.rcParams['grid.color'] = 'white'
plt.rcParams['grid.linewidth'] = 1.2         # make grid lines thicker
plt.rcParams['grid.linestyle'] = '-'         # solid grid lines
from utils import labels_mean_scores, grid_mean_scores, compute_correlation_matrix
from scipy.stats import binomtest, pearsonr, gaussian_kde


LABELS_DATAFILE='final_datafiles/MDFD_experiment_one_data.xlsx'
GRID_DATAFILE='final_datafiles/MDFD_experiment_two_data.xlsx'

# --- FIRST ANALYSIS: compute correlations between experimental variables across E1 and E2 ----
# Load processed datafiles
labels_scores_df = pd.read_excel(LABELS_DATAFILE, sheet_name='Labels condsXactors')
grid_val_df = pd.read_excel(GRID_DATAFILE, sheet_name='Valence condsXactors')
grid_aro_df = pd.read_excel(GRID_DATAFILE, sheet_name='Arousal condsXactors')
r_mean_df_withJSD = pd.read_excel(GRID_DATAFILE, sheet_name='CS+JSD condsXactors')

# Retrieve means
E1_mean_acc = np.array(labels_scores_df['MEAN'][:-1])
E2_mean_CS = np.array(r_mean_df_withJSD['MEAN'])
E2_mean_JSD = np.array(r_mean_df_withJSD['JSD'])
E2_mean_val = np.array(grid_val_df['MEAN'][:-1])
E2_mean_aro = np.array(grid_aro_df['MEAN'][:-1])

# Calculate Pearson correlations
E1_E2_mean_acc_CS_corr = pearsonr(E1_mean_acc, E2_mean_CS)
E1_E2_mean_acc_JSD_corr = pearsonr(E1_mean_acc, E2_mean_JSD)
E1_E2_mean_acc_val_corr = pearsonr(E1_mean_acc, E2_mean_val)
E1_E2_mean_acc_aro_corr = pearsonr(E1_mean_acc, E2_mean_aro)
print(f'Pearson correlation between E1 mean accuracy and E2 mean cluster size: r={E1_E2_mean_acc_CS_corr[0]:.2f}, p={E1_E2_mean_acc_CS_corr[1]:.3f}')
print(f'Pearson correlation between E1 mean accuracy and E2 mean JSD: r={E1_E2_mean_acc_JSD_corr[0]:.2f}, p={E1_E2_mean_acc_JSD_corr[1]:.3f}')
print(f'Pearson correlation between E1 mean accuracy and E2 mean valence: r={E1_E2_mean_acc_val_corr[0]:.2f}, p={E1_E2_mean_acc_val_corr[1]:.3f}')
print(f'Pearson correlation between E1 mean accuracy and E2 mean arousal: r={E1_E2_mean_acc_aro_corr[0]:.2f}, p={E1_E2_mean_acc_aro_corr[1]:.3f}')

# --- SECOND ANALYSIS: compute correlations between experimental variables across E1 and E2 ----

# Reconstructing dataframes from preprocessed datafiles
DATAFILE='preprocessed_datafiles/MDFD_all_blocks.xlsx'
labels_df = pd.read_excel(DATAFILE, sheet_name='Labels data')
labels_df = labels_df[labels_df['variable'] == 'score']
labels_df['condition'] = labels_df['condition'].str.capitalize()
condition_means_df, actor_means_df = labels_mean_scores(labels_df)
grid_df = pd.read_excel(DATAFILE, sheet_name='Grid data')
grid_df['condition'] = grid_df['condition'].str.capitalize()
val_condition_means_df, val_actor_means_df = grid_mean_scores(grid_df[grid_df['variable'] == 'val'])
aro_condition_means_df, aro_actor_means_df = grid_mean_scores(grid_df[grid_df['variable'] == 'aro'])

#Calculate mean valence and arousal values
actor_all_means_df = pd.DataFrame(actor_means_df['MEAN'])
actor_all_means_df = actor_all_means_df.rename(columns={'MEAN': 'Mean accuracy'})
actor_all_means_df = pd.concat([actor_all_means_df, pd.DataFrame(val_actor_means_df['MEAN'])], axis=1)
actor_all_means_df = actor_all_means_df.rename(columns={'MEAN': 'Mean valence'})
actor_all_means_df = pd.concat([actor_all_means_df, pd.DataFrame(aro_actor_means_df['MEAN'])], axis=1)
actor_all_means_df = actor_all_means_df.rename(columns={'MEAN': 'Mean arousal'})

actor_df = pd.read_excel(DATAFILE, sheet_name='Actor traits')
traits_df = actor_df.pivot(index='actor', columns='trait', values='mean')
traits_df.insert(len(traits_df.columns)-1, 'Similar age', traits_df.pop('similar_age'))
traits_df.insert(len(traits_df.columns)-1, 'Similar ethnicity', traits_df.pop('similar_ethnicity'))
traits_df.insert(len(traits_df.columns)-1, 'Similar social group', traits_df.pop('similar_socialg'))
traits_df.insert(len(traits_df.columns)-1, 'Similar worldview', traits_df.pop('similar_worldview'))
traits_df.insert(len(traits_df.columns)-1, 'Mindreading difficulty', traits_df.pop('mindreading_difficulty'))
traits_df = pd.concat([traits_df, actor_all_means_df], axis=1)
#traits_1 = ['attractive', 'familiar', 'likeable', 'trustworthy', 'Mindreading difficulty', 'Similar age', 'Similar ethnicity', 'Similar social group', 'Similar worldview']
#traits_1_df = traits_df[traits_1].T.round(2)

# Save processed datafiles
all_blocks_df = pd.ExcelFile(DATAFILE)
excel_writer_subs = pd.ExcelWriter('final_datafiles/MDFD_subjects_and_actors_data.xlsx', engine='xlsxwriter')
for sheet_name in all_blocks_df.sheet_names:
    if 'Grid' not in sheet_name and 'Labels' not in sheet_name:
        df = all_blocks_df.parse(sheet_name)
        df.to_excel(excel_writer_subs, sheet_name=sheet_name, index=False)
excel_writer_subs.close()
print('Saved processed data to: final_datafiles/MDFD_subjects_and_actors_data.xlsx')

# Plot 
compute_correlation_matrix(traits_df, correction_method=None)