import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('bmh')
plt.rcParams['axes.facecolor'] = '#eaeaf2'  # light bluish-gray
plt.rcParams['grid.color'] = 'white'
plt.rcParams['grid.linewidth'] = 1.2         # make grid lines thicker
plt.rcParams['grid.linestyle'] = '-'         # solid grid lines
from utils import *

DATAFILE='preprocessed_datafiles/MDFD_all_blocks.xlsx'
SAVE_JSD_FIGURES = False     #Set to True to save individual JSD figures

#Read datafile
grid_df = pd.read_excel(DATAFILE, sheet_name='Grid data')
#Capitalize conditions
grid_df['condition'] = grid_df['condition'].str.capitalize()
#Keep only variables of interest
grid_val_df = grid_df[grid_df['variable'] == 'val']
grid_aro_df = grid_df[grid_df['variable'] == 'aro']
grid_val_out_df = grid_val_df.copy()
grid_aro_out_df = grid_aro_df.copy()

# - Scores DF -
#Rearrange to desired format
grid_val_df = grid_val_df.pivot(index='condition', columns='actor', values='mean')
grid_aro_df = grid_aro_df.pivot(index='condition', columns='actor', values='mean')
#Fix dimension of arousal scores
grid_aro_df += 150

#Calculate means
val_condition_means_df, val_actor_means_df = grid_mean_scores(grid_df[grid_df['variable'] == 'val'])
grid_val_df = pd.merge(grid_val_df, val_condition_means_df['MEAN'], left_index=True, right_index=True)
grid_val_df = pd.merge(grid_val_df.T, val_actor_means_df['MEAN'], how='outer', left_index=True, right_index=True).T
aro_condition_means_df, aro_actor_means_df = grid_mean_scores(grid_df[grid_df['variable'] == 'aro'])
aro_condition_means_df += 150
aro_actor_means_df += 150
grid_aro_df = pd.merge(grid_aro_df, aro_condition_means_df['MEAN'], left_index=True, right_index=True)
grid_aro_df = pd.merge(grid_aro_df.T, aro_actor_means_df['MEAN'], how='outer', left_index=True, right_index=True).T

#Round
grid_val_df = grid_val_df.astype(float).round(0)
grid_aro_df = grid_aro_df.astype(float).round(0)

#Cluster size
grid_agreeement_scores_df = pd.read_excel(DATAFILE, sheet_name='Grid stats')
#grid_agreeement_scores_df = grid_agreeement_scores_df.replace({"actor": actor_coding})
grid_agreeement_scores_df['condition'] = grid_agreeement_scores_df['condition'].str.capitalize()
r_mean_df = grid_agreeement_scores_df.pivot(index='condition', columns='actor', values='r_mean')
for col in r_mean_df.columns:
    r_mean_df[col] = r_mean_df[col].round(1).astype(float)
    r_mean_df[col] = r_mean_df[col].replace({pd.NA: np.nan})
r_mean_df['MEAN'] = round(r_mean_df.mean(axis=1),1)

#Conduct JSD analysis (saving plots optional)
JSD_dict = JSD_analysisNplots(grid_df, grid_val_df, grid_aro_df, r_mean_df, save_figs = SAVE_JSD_FIGURES)
r_mean_df_withJSD = r_mean_df.copy()
my_title = 'grid/cluster-size.png'
jsd_col = pd.DataFrame.from_dict(JSD_dict, orient='index')
r_mean_df_withJSD.insert(len(r_mean_df_withJSD.columns), 'JSD', jsd_col)

# Save processed datafiles
all_blocks_df = pd.ExcelFile(DATAFILE)
excel_writer_e2 = pd.ExcelWriter('final_datafiles/MDFD_experiment_two_data.xlsx', engine='xlsxwriter')
for sheet_name in all_blocks_df.sheet_names:
    if 'Grid' in sheet_name:
        df = all_blocks_df.parse(sheet_name)
        df.to_excel(excel_writer_e2, sheet_name=sheet_name, index=False)
grid_val_df.to_excel(excel_writer_e2, sheet_name='Valence condsXactors', index=True)
grid_aro_df.to_excel(excel_writer_e2, sheet_name='Arousal condsXactors', index=True)
r_mean_df_withJSD.to_excel(excel_writer_e2, sheet_name='CS+JSD condsXactors', index=True)
excel_writer_e2.close()
print('Saved processed data to: final_datafiles/MDFD_experiment_two_data.xlsx')

#Save plots
my_heatmap(r_mean_df, cmap='inferno_r', plot_title='', png_title='Cluster_size_scores.png', fmt='g', save_plot=True)
my_heatmap(grid_val_df, cmap='plasma', plot_title='Valence scores in "point-and-click" paradigm', png_title='Valence_scores.png', fmt='g')
my_heatmap(grid_aro_df, cmap='plasma', plot_title='Arousal scores in "point-and-click" paradigm', png_title='Arousal_scores.png', fmt='g')
plot_distributions(grid_val_df, 'Valence')
plot_distributions(grid_aro_df, 'Arousal')

#1-D manifold analysis 
n_components = 5
actor = 'MEAN'
grid_df = np.array([grid_val_df[actor][:-1], grid_aro_df[actor][:-1]]).T
main_embeddings, main_components_explained_variance, dist_from_neutral = compute_isomap(grid_df, n_components=n_components, n_neighbors=11)
main_PC1_embedding = main_embeddings[:, 0]
#print(f"Main components explained variance: {main_components_explained_variance}")
plot_main_grid(grid_val_df, grid_aro_df, actor,  main_embeddings[:, 1]) 
plot_scree_plot(main_components_explained_variance, n_components, actor)
plot_mini_grid(grid_val_df, grid_aro_df, actor, dist_from_neutral, cmap='inferno_r', colorbar_label='Distance to vertex in PC1', var='mean_cluster_size')

