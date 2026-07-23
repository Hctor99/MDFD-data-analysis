import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import os
import numpy as np
import pprint
from scipy.stats import binomtest

DATATABLE_B3 = 'preprocessed_datafiles/MDFD_B3.xlsx'
DATATABLE_B2 = 'preprocessed_datafiles/MDFD_B2.xlsx'
DATATABLE_B1 = 'preprocessed_datafiles/MDFD_B1.xlsx'
OUTPUT_FILE = 'preprocessed_datafiles/MDFD_all_blocks.xlsx'

ACTOR_TRAITS1 = ['trustworthy', 'likeable', 'familiar', 'attractive', 'similar', 'mindreading']
ACTOR_TRAITS2 = ['leader', 'sensitive', 'dominant', 'weak', 'emotional', 'intelligent', 'independent', 'shy', 'active', 'enthusiastic', 'helpful', 'wholesome', 'rebellious', 'noisy', 'promiscuous']


def get_traits_sheet(B1_surveys, B2_surveys, B3_surveys, final_ids):
    B1_traits = B1_surveys[['id']+[col for col in B1_surveys.columns if '_' in col and col.split('_')[1] in ACTOR_TRAITS1 + ACTOR_TRAITS2]]
    B2_traits = B2_surveys[['id']+[col for col in B2_surveys.columns if '_' in col and col.split('_')[1] in ACTOR_TRAITS1 + ACTOR_TRAITS2]]
    B3_traits = B3_surveys[['id']+[col for col in B3_surveys.columns if '_' in col and col.split('_')[1] in ACTOR_TRAITS1 + ACTOR_TRAITS2]]
    All_traits = pd.merge(pd.merge(B3_traits, B2_traits, on='id'), B1_traits, on='id')
    #Sort according to final_ids
    All_traits['id'] = pd.Categorical(All_traits['id'], categories=final_ids+['block'], ordered=True)
    All_traits = All_traits.sort_values(by='id')
    All_traits = All_traits.T
    All_traits.columns = All_traits.iloc[0]
    All_traits = All_traits.drop(All_traits.index[0]).astype(str).astype(int)
    All_traits['mean'] = All_traits.mean(axis=1)
    All_traits['std'] = All_traits.loc[:,[col for col in All_traits.columns if col != "mean"]].std(axis=1)
    All_traits = All_traits.reset_index()
    All_traits.insert(loc = 0, column = 'actor', value = All_traits['index'].str.partition('_')[0])
    All_traits.insert(loc = 1, column = 'trait', value = All_traits['index'].str.partition('_')[2])
    All_traits.insert(loc = 0, column = 'survey_num', value = All_traits['trait'].apply(lambda t: 2 if t in ACTOR_TRAITS2 else 1))
    All_traits.insert(loc = 3, column = 'mean', value = All_traits.pop('mean'))
    All_traits.insert(loc = 4, column = 'std', value = All_traits.pop('std'))
    All_traits = All_traits.drop(['index'], axis=1)
    All_traits = All_traits.sort_values(['actor', 'survey_num', 'trait'], ascending=[True, True, True])
    return All_traits

def get_surveys_sheet(B1_surveys, B2_surveys, B3_surveys):
    #Survey batch 1
    All_surveys = B1_surveys[['id']+[col for col in B1_surveys.columns if '_' not in col or col.split('_')[1] not in ACTOR_TRAITS1 + ACTOR_TRAITS2]]
    for i, col_name in enumerate(['exp_type', 'block_s1', 'age', 'gender', 'ethnicity', 'religion', 'Language', 'country_origin', 'country_residence', 'country_residence_years', 'Employment status', 'Total approvals']):
        All_surveys.insert(loc = 1+i, column = col_name, value = All_surveys.pop(col_name))
    All_surveys.loc[:, 'ethnicity'] = All_surveys['ethnicity'].apply(lambda x: x.split('.')[0])
    All_surveys.loc[:, 'country_origin'] = All_surveys['country_origin'].apply(lambda x: 'United Kingdom' if 'United Kingdom' in x else x)
    All_surveys.loc[:, 'country_residence'] = All_surveys['country_origin'].apply(lambda x: 'United Kingdom' if 'United Kingdom' in x else x)
    All_surveys.loc[:, 'religion'] = All_surveys['religion'].apply(lambda x: 'Christian' if 'Christian' in x else x)
    All_surveys = All_surveys.loc[:,~All_surveys.columns.duplicated()]
    All_surveys.pop('Nationality')
    All_surveys.pop('complete?')
    All_surveys.pop('Time taken')
    All_surveys = All_surveys.rename(columns={"total approvals": "total_approvals", "block_s1": "block_session1_batch1"})
    All_surveys.columns = [x.lower() for x in All_surveys.columns]
    #Survey batch 2
    B2_surveys = B2_surveys[['id', 'block_s1']+[col for col in B2_surveys.columns if 'icq' in col]]
    B2_surveys = B2_surveys.rename(columns={"block_s1": "block_session1_batch2"})
    All_surveys = pd.merge(All_surveys, B2_surveys, on='id')
    All_surveys.insert(loc = 3, column = 'block_session1_batch2', value = All_surveys.pop('block_session1_batch2'))
    #Survey batch 3
    B3_surveys = B3_surveys[['id', 'block_s1']+[col for col in B3_surveys.columns if 'RMET' in col]]
    B3_surveys = B3_surveys.rename(columns={"block_s1": "block_session1_batch3"})
    All_surveys = pd.merge(All_surveys, B3_surveys, on='id')
    All_surveys.insert(loc = 4, column = 'block_session1_batch3', value = All_surveys.pop('block_session1_batch3'))
    All_surveys = All_surveys.sort_values(['exp_type', 'block_session1_batch1', 'block_session1_batch2', 'block_session1_batch3'])
    return All_surveys

def get_labels_stats(df):
    #Get df that only contains 'score' variable
    numeric_data = df.apply(pd.to_numeric, errors='coerce')
    score_data = numeric_data.iloc[1:-1:3]
    parts_num = score_data.iloc[0].count()
        
    #Calculate mean and standard deviation (https://www.researchgate.net/post/Can-standard-deviation-and-standard-error-be-calculated-for-a-binary-variable)
    mean_values = np.array(score_data.mean(axis=1))
    std_values = np.array(np.sqrt(mean_values * (1 - mean_values) / parts_num))

    #Perform a binomial test for each stimulus (25% guess rate)
    xs = np.nansum(score_data, axis=1)      #Total correct responses
    ns = [parts_num] * score_data.shape[0]  #Total number of participants
    p_values = [binomtest(int(x), n, p=0.25, alternative='greater').pvalue for x,n in zip(xs, ns)]
    #Get stats into columns that fit our df
    my_idx = 0
    means_column = []
    stds_column = []
    p_values_column = []
    for i in list(numeric_data.index):
        means_column.append(mean_values[my_idx] if i in list(score_data.index) else np.nan)
        stds_column.append(std_values[my_idx] if i in list(score_data.index) else np.nan)
        p_values_column.append(p_values[my_idx] if i in list(score_data.index) else np.nan)
        my_idx = my_idx + 1 if i in list(score_data.index) else my_idx
    return means_column, stds_column, p_values_column

def euclidian_distance(df):
    data_only_cols = [c for c in df.columns if len(c) < 4 and ('G' in c or 'L' in c)]

    #Since we're using df copy, we compute the first steps of the calculation in place
    df[data_only_cols] = np.power(df['mean'].values[:, None] - df[data_only_cols].values, 2)
    df_list = []
    for actor in df['actor'].unique():
        for condition in df['condition'].unique():
            actor_df = df[df['actor'] == actor]
            actor_cond_df = actor_df[actor_df['condition'] == condition]
            if len(actor_cond_df.index) == 0:
                continue
            actor_cond_df.index = [0,1,2]
            #Using the rt row to store eucledian distances per participant
            actor_cond_df.loc[2, data_only_cols] = (actor_cond_df.loc[0, data_only_cols] + actor_cond_df.loc[1, data_only_cols]).pow(0.5)

            r_mean = actor_cond_df.loc[2, data_only_cols].mean()
            df_list.append([actor, condition, 
                            actor_cond_df.loc[0, 'mean'], 
                            actor_cond_df.loc[0, 'median'], 
                            actor_cond_df.loc[0, 'std'], 
                            actor_cond_df.loc[1, 'mean'], 
                            actor_cond_df.loc[1, 'median'], 
                            actor_cond_df.loc[1, 'std'],
                            r_mean])
    new_df = pd.DataFrame(df_list, columns = ['actor', 'condition', 'valence_mean', 'valence_median', 'valence_std', 'arousal_mean', 
                                            'arousal_median', 'arousal_std', 'r_mean'])
 
    return new_df

def get_exp_data(df, final_ids, exp_type):
    #Merge data from both blocks, saving the block as a new variable
    data_B1 = df.parse(f'{exp_type} B1')
    data_B2 = df.parse(f'{exp_type} B2') 
    assert data_B1.shape[0] == data_B2.shape[0], 'Block 1 and 2 have different number of participants!!'
    data_B1.loc[len(data_B1)] = {col: 'one' if col != 'id' else 'block' for col in data_B1.columns}
    data_B2.loc[len(data_B2)] = {col: 'two' if col != 'id' else 'block' for col in data_B2.columns}
    data_merged = pd.merge(data_B1.drop('session', axis=1), data_B2.drop('session', axis=1), on='id')

    #Keep data only from final participans (obtained from Batch 3) and sort based on order in final_ids
    data_merged = data_merged[data_merged['id'].isin(final_ids+['block'])]
    data_merged['id'] = pd.Categorical(data_merged['id'], categories=final_ids+['block'], ordered=True)
    data_merged = data_merged.sort_values(by='id')

    #Transpose, change to numeric, etc.
    data_merged = data_merged.T
    data_merged.columns = data_merged.iloc[0]
    data_merged = data_merged.drop(data_merged.index[0])
    for col in data_merged.columns:
        if exp_type == 'Grid':
            data_merged[col] = data_merged[col].astype(int) if col != 'block' else data_merged[col]
        else:
            data_merged[col] = data_merged[col].astype(int) if 'score' in col or '_rt' in col else data_merged[col]

    #Split new variables from index: actor-name_condition_variable
    data_merged = data_merged.reset_index()
    data_merged.insert(loc = 0, column = 'block', value = data_merged.pop('block'))
    data_merged.insert(loc = 1, column = 'actor', value = data_merged['index'].str.partition('_')[0])
    data_merged.insert(loc = 2, column = 'condition', value = data_merged['index'].str.partition('_')[2].str.partition('_')[0])
    data_merged.insert(loc = 3, column = 'variable', value = data_merged['index'].str.partition('_')[2].str.partition('_')[2])
    data_merged = data_merged.drop(['index'], axis=1)
    
    #CALCULATE STATISTICS
    if exp_type == 'Labels':
        means, stds, p_values = get_labels_stats(data_merged)
        data_merged.insert(loc = 4, column = 'mean', value = means)
        data_merged.insert(loc = 5, column = 'std', value = stds)
        data_merged.insert(loc = 6, column = 'p', value = p_values)
        stats_df = pd.DataFrame([])
    else:
        mean_values = data_merged.mean(axis=1, numeric_only=True)
        median_values = data_merged.median(axis=1, numeric_only=True)
        std_values = data_merged.std(axis=1, numeric_only=True)
        data_merged.insert(loc = 4, column = 'mean', value = mean_values)
        data_merged.insert(loc = 5, column = 'median', value = median_values)
        data_merged.insert(loc = 6, column = 'std', value = std_values)
        stats_df = euclidian_distance(data_merged.copy())

    data_merged = data_merged.replace({"block": {'one': 1, 'two': 2}})
    if exp_type == 'Grid':
        data_merged = data_merged.replace({"variable": {'x': 'val', 'y': 'aro'}})
    data_merged['block'] = data_merged['block'].astype(int)

    return data_merged, stats_df

def main():
  
    #Set working directory
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    #Extract data from preprocessed datafiles
    excel_writer = pd.ExcelWriter(OUTPUT_FILE, engine='xlsxwriter')
    B1_data = pd.ExcelFile(DATATABLE_B1)
    B2_data = pd.ExcelFile(DATATABLE_B2)
    B3_data = pd.ExcelFile(DATATABLE_B3)
    B1_surveys = B1_data.parse('Surveys')
    B2_surveys = B2_data.parse('Surveys')
    B3_surveys = B3_data.parse('Surveys')

    #Get participants information + actor traits
    all_surveys_df = get_surveys_sheet(B1_surveys, B2_surveys, B3_surveys)
    final_ids = list(all_surveys_df['id'])
    all_traits_df = get_traits_sheet(B1_surveys, B2_surveys, B3_surveys, final_ids)
   
    #Get experimental data from Grid and Labels
    B3_grid_df, B3_grid_stats_df = get_exp_data(B3_data, final_ids, 'Grid')
    B2_grid_df, B2_grid_stats_df = get_exp_data(B2_data, final_ids, 'Grid')
    B1_grid_df, B1_grid_stats_df = get_exp_data(B1_data, final_ids, 'Grid')
    all_grid_df = pd.concat([B1_grid_df, B2_grid_df, B3_grid_df])
    all_grid_stats_df = pd.concat([B1_grid_stats_df, B2_grid_stats_df, B3_grid_stats_df])
    all_grid_df = all_grid_df.sort_values(['actor', 'condition'])
    all_grid_stats_df = all_grid_stats_df.sort_values(['actor', 'condition'])
    B3_labels_df, B3_labels_stats_df = get_exp_data(B3_data, final_ids, 'Labels')
    B2_labels_df, B2_labels_stats_df = get_exp_data(B2_data, final_ids, 'Labels')
    B1_labels_df, B1_labels_stats_df = get_exp_data(B1_data, final_ids, 'Labels')
    all_labels_df = pd.concat([B1_labels_df, B2_labels_df, B3_labels_df])
    all_labels_df = all_labels_df.sort_values(['actor', 'condition'])

    #Split all_surveys_df into two dfs
    all_demographics_df = all_surveys_df[[col for col in all_surveys_df if not ('icq' in col or 'iri' in col or 'RMET' in col)]]
    all_questionnaires_df = all_surveys_df[[col for col in all_surveys_df if col == 'id' or ('icq' in col or 'iri' in col or 'RMET' in col)]]
    all_questionnaires_df = all_questionnaires_df.loc[:, ~all_questionnaires_df.columns.str.contains('_x')]
    all_questionnaires_df.columns = [col.replace('_y', '') for col in all_questionnaires_df.columns]

    #Save dataframes in their own Excel sheets
    all_demographics_df.to_excel(excel_writer, sheet_name='Demographics', index=False) 
    all_questionnaires_df.to_excel(excel_writer, sheet_name='IRI, ICQ, RMET', index=False) 
    all_traits_df.to_excel(excel_writer, sheet_name='Actor traits', index=False) 
    all_grid_df.to_excel(excel_writer, sheet_name='Grid data', index=False)
    all_grid_stats_df.to_excel(excel_writer, sheet_name='Grid stats', index=False) 
    all_labels_df.to_excel(excel_writer, sheet_name='Labels data', index=False) 
    
    excel_writer.close()

    print('Done!')

if __name__ == "__main__":
    main()

