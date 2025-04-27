import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind, pearsonr

# --- Paths to data ---
JATOS_RESULTS_PATH = "jatos_results_data_20250426131918"  # Folder containing JATOS results
SURVEY_FILE = "results-survey349233 (2).csv"  # Survey results file

# --- Load the survey data ---
survey_df = pd.read_csv(SURVEY_FILE)
survey_df.rename(columns=lambda col: col.strip(), inplace=True)
survey_df['jatosStudyResultId'] = survey_df['jatosStudyResultId'].astype(str).str.replace('.0', '', regex=False)

# --- Read and filter participant data ---
participants = []

for study_folder in os.listdir(JATOS_RESULTS_PATH):
    study_path = os.path.join(JATOS_RESULTS_PATH, study_folder)

    if os.path.isdir(study_path):
        for comp_result in os.listdir(study_path):
            comp_result_path = os.path.join(study_path, comp_result)
            data_file = os.path.join(comp_result_path, 'data.csv')

            if os.path.exists(data_file):
                try:
                    data = pd.read_csv(data_file)
                except pd.errors.EmptyDataError:
                    print(f"[WARNING] Skipping empty file: {data_file}")
                    continue

                if not data.empty:
                    # --- Filter rows containing 'stim' across all columns ---
                    stim_mask = data.apply(lambda col: col.astype(str).str.contains('stim', case=False, na=False)).any(axis=1)
                    data_stimuli = data[stim_mask]

                    if not data_stimuli.empty:
                        # Calculate total correct responses
                        total_correct = data_stimuli['correct'].sum()

                        # Calculate total number of stimulus trials
                        total_responses = len(data_stimuli)

                        # Compute average response time
                        if 'average_response_time' in data_stimuli.columns:
                            avg_rt = pd.to_numeric(data_stimuli['average_response_time'], errors='coerce').mean()
                        elif 'response_time' in data_stimuli.columns:
                            avg_rt = pd.to_numeric(data_stimuli['response_time'], errors='coerce').mean()
                        else:
                            avg_rt = np.nan

                        participants.append({
                            'participant_id': study_folder,
                            'total_correct': total_correct,
                            'total_responses': total_responses,
                            'accuracy': total_correct / total_responses if total_responses else np.nan,
                            'avg_rt': avg_rt
                        })
                    else:
                        print(f"[WARNING] No 'stim' trials found in {data_file}")
                else:
                    print(f"[WARNING] No data found after reading: {data_file}")

# --- Create DataFrame ---
results_df = pd.DataFrame(participants)

if results_df.empty:
    print("\n No participants with 'stimuli' trials found.")
else:
    # --- Merge with survey data ---
    results_df['participant_id_clean'] = results_df['participant_id'].str.replace('study_result_', '', regex=False)
    merged_df = pd.merge(results_df, survey_df, left_on='participant_id_clean', right_on='jatosStudyResultId', how='left')

    # --- Plots and Analyses ---
    sns.set(style="whitegrid")
    results = {}

    # 1. Histogram of accuracy rates
    overall_acc = merged_df['accuracy'] * 100
    plt.figure()
    sns.histplot(overall_acc.dropna(), bins=10, kde=True)
    plt.title('Distribution of Accuracy Rates (Stimuli Only)')
    plt.xlabel('Accuracy (%)')
    plt.ylabel('Number of Participants')
    plt.savefig('histogram_accuracy_stimuli.png')

    # 2. Tonal vs Non-Tonal Speakers Analysis
    tonal_speaker_col = 'Are you a native speaker of Mandarin Chinese?'

    if tonal_speaker_col in merged_df.columns:
        merged_df['Tonal Speaker'] = merged_df[tonal_speaker_col].map({'Yes': 'Tonal', 'No': 'Non-Tonal'})
        tonal_counts = merged_df['Tonal Speaker'].value_counts(dropna=True).to_dict()
        results['tonal_counts'] = tonal_counts

        if 'Tonal' in tonal_counts or 'Non-Tonal' in tonal_counts:
            # Boxplots
            plt.figure()
            sns.boxplot(x='Tonal Speaker', y='accuracy', data=merged_df)
            plt.title('Accuracy by Language Background (Stimuli Only)')
            plt.ylabel('Accuracy')
            plt.savefig('boxplot_accuracy_language_stimuli.png')

            plt.figure()
            sns.boxplot(x='Tonal Speaker', y='avg_rt', data=merged_df)
            plt.title('Reaction Time by Language Background (Stimuli Only)')
            plt.ylabel('Average Reaction Time (ms)')
            plt.savefig('boxplot_rt_language_stimuli.png')

            # T-test
            tonal = merged_df[merged_df['Tonal Speaker'] == 'Tonal']['accuracy'].dropna()
            non_tonal = merged_df[merged_df['Tonal Speaker'] == 'Non-Tonal']['accuracy'].dropna()

            if len(tonal) > 1 and len(non_tonal) > 1:
                t_stat, p_value = ttest_ind(tonal, non_tonal)
                results['t_test'] = {"t_statistic": t_stat, "p_value": p_value}
            else:
                results['t_test'] = "Not enough data for T-test."
        else:
            results['t_test'] = "No Tonal/Non-Tonal data found."
    else:
        results['tonal_counts'] = "Tonal Speaker column not found."
        results['t_test'] = "No Tonal/Non-Tonal data found."

    # 3. Correlation between Age and Accuracy
    if 'How old are you?' in merged_df.columns:
        merged_df['How old are you?'] = pd.to_numeric(merged_df['How old are you?'], errors='coerce')
        age_acc = merged_df.dropna(subset=['How old are you?', 'accuracy'])

        if len(age_acc) > 2:
            corr, p_corr = pearsonr(age_acc['How old are you?'], age_acc['accuracy'])
            results['correlation_age_accuracy'] = {"correlation_coefficient": corr, "p_value": p_corr}
        else:
            results['correlation_age_accuracy'] = "Not enough data for correlation."
    else:
        results['correlation_age_accuracy'] = "Age column not found."

    # 4. Histogram of Reaction Times
    plt.figure()
    sns.histplot(merged_df['avg_rt'].dropna(), bins=10, kde=True)
    plt.title('Distribution of Average Reaction Times (Stimuli Only)')
    plt.xlabel('Average Reaction Time (ms)')
    plt.ylabel('Number of Participants')
    plt.savefig('histogram_rt_stimuli.png')

    # 5. Scatter plot: Reaction Time vs Accuracy
    plt.figure()
    sns.scatterplot(x='avg_rt', y='accuracy', data=merged_df, hue=merged_df.get('Tonal Speaker', None))
    plt.title('Reaction Time vs Accuracy (Stimuli Only)')
    plt.xlabel('Average Reaction Time (ms)')
    plt.ylabel('Accuracy')
    plt.savefig('scatter_rt_vs_accuracy.png')

    # --- Save final merged file ---
    merged_df.to_csv('merged_results_stimuli_only.csv', index=False)

    print("\n=== Summary of Results ===\n")
    print(results)
    print("\n✅ Plots saved and 'merged_results_stimuli_only.csv' created successfully!")
