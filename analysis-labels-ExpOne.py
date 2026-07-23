import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('bmh')
plt.rcParams['axes.facecolor'] = '#eaeaf2'  # light bluish-gray
plt.rcParams['grid.color'] = 'white'
plt.rcParams['grid.linewidth'] = 1.2         # make grid lines thicker
plt.rcParams['grid.linestyle'] = '-'         # solid grid lines
from statsmodels.stats.multitest import multipletests
from utils import labels_mean_scores, my_heatmap, my_heatmap_grays, plot_distributions

DATAFILE='preprocessed_datafiles/MDFD_all_blocks.xlsx'

#Read datafile
labels_df = pd.read_excel(DATAFILE, sheet_name='Labels data')
labels_df = labels_df[labels_df['variable'] == 'score']

#Capitalize conditions
labels_df['condition'] = labels_df['condition'].str.capitalize()

# - Scores DF -
labels_scores_df = labels_df.pivot(index='condition', columns='actor', values='mean')
ACTORS = list(labels_scores_df.columns[:-1])

# - P-values DF -
labels_pvals_df = labels_df.pivot(index='condition', columns='actor', values='p')

#Calculate means
condition_means_df, actor_means_df = labels_mean_scores(labels_df)
labels_scores_df = pd.merge(labels_scores_df, condition_means_df['MEAN'], left_index=True, right_index=True)
labels_scores_df = pd.merge(labels_scores_df.T, actor_means_df['MEAN'], how='outer', left_index=True, right_index=True).T
labels_pvals_df = pd.merge(labels_pvals_df, condition_means_df['pval'], left_index=True, right_index=True)
labels_pvals_df = pd.merge(labels_pvals_df.T, actor_means_df['pval'], how='outer', left_index=True, right_index=True).T
labels_pvals_df = labels_pvals_df.rename(columns={'pval':'MEAN'}, index={'pval':'MEAN'})

#Round
labels_scores_df = labels_scores_df.round(3).astype(float)
labels_pvals_df = labels_pvals_df.astype(float)

#---Apply Benjamini-Hochberg procedure to correct for multiple comparisons---

# Flatten the DataFrame into a Series
pvals_flat = labels_pvals_df.values.flatten()
mask = ~np.isnan(pvals_flat)  # Ignore NaNs if you have them

# Apply Benjamini-Hochberg procedure to correct for multiple comparisons
adjusted = np.full_like(pvals_flat, np.nan, dtype=float)
_, pvals_corrected, _, _ = multipletests(pvals_flat[mask], alpha=0.05, method='fdr_bh')
adjusted[mask] = pvals_corrected

# Reshape back to original shape
labels_pvals_corrected = pd.DataFrame(adjusted.reshape(labels_pvals_df.shape), 
                             index=labels_pvals_df.index, 
                             columns=labels_pvals_df.columns)

# Scores + asterisks DF
pval_to_asterisk = lambda p_val: '***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else ''
labels_scores_asterisks_df = labels_pvals_corrected.copy()
for col in labels_pvals_corrected.columns:
    col_scores = [str(round(score, 2)) for score in list(labels_scores_df[col])]
    col_asterisks = list(labels_pvals_corrected[col].apply(pval_to_asterisk))
    labels_scores_asterisks_df[col] =list(map(str.__add__, col_scores, col_asterisks))


# Print significance results
all_stimuli_scores_df = labels_scores_asterisks_df[:-1].drop(columns=['MEAN'])
all_stimuli_scores = all_stimuli_scores_df.values.flatten()
all_stimuli_scores = [x for x in all_stimuli_scores if str(x) != 'nan']
all_stimuli_asterisks = [x for x in all_stimuli_scores if '*' in x]
all_stimuli_no_asterisks = [x for x in all_stimuli_scores if '*' not in x]
print(f'Number of stimuli with significant differences: {len(all_stimuli_asterisks)} / {len(all_stimuli_scores)} ({round(100*(len(all_stimuli_asterisks) / len(all_stimuli_scores)))}%)')
print(f'Number of stimuli without significant differences: {len(all_stimuli_no_asterisks)} / {len(all_stimuli_scores)}')
actor_asterisks = {}
for actor in ACTORS:
    all_actor_scores_df = list(all_stimuli_scores_df[actor])
    all_actor_asterisks = [x for x in all_actor_scores_df if '*' in str(x)]
    actor_asterisks[actor] = len(all_actor_asterisks)
sorted_actor_asterisks = sorted(actor_asterisks.items(), key=lambda x: x[1], reverse=True)
print('Number of significant stimuli per actor = ', end='')
for actor, count in sorted_actor_asterisks:
    print(f'{actor}={count}, ', end='')
stimuli_asterisks = {}
for condition in all_stimuli_scores_df.index:
    all_condition_scores_df = list(all_stimuli_scores_df.loc[condition])
    all_condition_asterisks = [x for x in all_condition_scores_df if '*' in str(x)]
    stimuli_asterisks[condition] = len(all_condition_asterisks)
stimuli_asterisks_sorted = sorted(stimuli_asterisks.items(), key=lambda x: x[1], reverse=True)
print('\nNumber of significant stimuli per condition = ', end='')
for condition, count in stimuli_asterisks_sorted:
    print(f'{condition}={count}, ', end='')
asterisks_count = {}
for condition, count in stimuli_asterisks_sorted:
    if count not in asterisks_count:
        asterisks_count[count] = 0
    asterisks_count[count] += 1
print('\nNumber of recognized stimuli per number of actors:')
for count, num_stimuli in asterisks_count.items():
    print(f'{count} actors: {num_stimuli} stimuli')

# Save processed datafiles
all_blocks_df = pd.ExcelFile(DATAFILE)
excel_writer_e1 = pd.ExcelWriter('final_datafiles/MDFD_experiment_one_data.xlsx', engine='xlsxwriter')
for sheet_name in all_blocks_df.sheet_names:
    if 'Labels' in sheet_name:
        df = all_blocks_df.parse(sheet_name)
        df.to_excel(excel_writer_e1, sheet_name=sheet_name, index=False)
labels_scores_df.to_excel(excel_writer_e1, sheet_name='Labels condsXactors', index=True)
labels_scores_asterisks_df.to_excel(excel_writer_e1, sheet_name='Labels condsXactors binom', index=True)
excel_writer_e1.close()
print('Saved processed data to: final_datafiles/MDFD_experiment_one_data.xlsx')

# Save plots 
my_heatmap(labels_scores_df, cmap='Oranges', plot_title='Accuracy scores in 4-AFC paradigm', png_title='Accuracy_scores.png')
my_heatmap_grays(labels_scores_df, labels_scores_asterisks_df, cmap='Oranges', plot_title='Accuracy scores in 4-AFC paradigm (with Benjamini-Hochberg method)', png_title='Accuracy_scores_with_significance.png')
plot_distributions(labels_scores_df, 'Recognition accuracy')