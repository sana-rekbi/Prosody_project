import os
import pandas as pd
import numpy as np

# --- Paths to the data ---
JATOS_RESULTS_PATH = "jatos_results_data_20250426131918"  # Folder containing JATOS results
SURVEY_FILE = "results-survey349233 (2).csv"  # Survey results file

# --- Load the survey file ---
survey_df = pd.read_csv(SURVEY_FILE)
survey_df.rename(columns=lambda col: col.strip(), inplace=True)  # Clean column names
survey_df['jatosStudyResultId'] = survey_df['jatosStudyResultId'].astype(str).str.replace('.0', '', regex=False)

# --- Read participants' results ---
participants_summary = []
all_stimuli_trials = []

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
                    print(f"[warning] Skipping empty file: {data_file}")
                    continue

                if not data.empty:
                    # --- Keep only trials related to 'stim' ---
                    stim_mask = (
                        data['sound1'].astype(str).str.contains('stim', case=False, na=False) |
                        data['sound2'].astype(str).str.contains('stim', case=False, na=False) |
                        data['sound_1'].astype(str).str.contains('stim', case=False, na=False) |
                        data['sound_2'].astype(str).str.contains('stim', case=False, na=False)
                    )
                    data_stimuli = data[stim_mask].copy()

                    if not data_stimuli.empty:
                        # Check if the response is correct
                        data_stimuli['is_correct'] = data_stimuli['response'] == data_stimuli['correct_response']
                        data_stimuli['participant_id'] = study_folder
                        all_stimuli_trials.append(data_stimuli)

                        # Summarize results for this participant
                        total_stimuli = len(data_stimuli)
                        total_correct = data_stimuli['is_correct'].sum()

                        # Compute average response time
                        avg_rt = np.nan
                        if 'average_response_time' in data_stimuli.columns:
                            avg_rt = pd.to_numeric(data_stimuli['average_response_time'], errors='coerce').mean()
                        elif 'response_time' in data_stimuli.columns:
                            avg_rt = pd.to_numeric(data_stimuli['response_time'], errors='coerce').mean()

                        participants_summary.append({
                            'participant_id': study_folder,
                            'total_correct': total_correct,
                            'total_responses': total_stimuli,
                            'accuracy': total_correct / total_stimuli if total_stimuli else np.nan,
                            'avg_rt': avg_rt
                        })
                    else:
                        print(f"[warning] No 'stim' trials found in {data_file}")
                else:
                    print(f"[warning] Empty data after reading: {data_file}")

# --- Merge and save results ---
results_df = pd.DataFrame(participants_summary)

if results_df.empty:
    print("\n No participants with 'stim' trials found.")
else:
    print(f"\n Results processed for {len(results_df)} participants.")

    # Clean participant IDs
    results_df['participant_id_clean'] = results_df['participant_id'].str.replace('study_result_', '', regex=False)

    # Merge with survey responses
    merged_df = pd.merge(results_df, survey_df, left_on='participant_id_clean', right_on='jatosStudyResultId', how='left')

    # Save merged results
    merged_df.to_csv('merged_results_stimuli_only.csv', index=False)
    print(" 'merged_results_stimuli_only.csv' created.")

    # Save all detailed stimuli trials
    full_stimuli_df = pd.concat(all_stimuli_trials, ignore_index=True)
    full_stimuli_df[['participant_id', 'sound1', 'sound2', 'sound_1', 'sound_2', 'correct_response', 'response', 'is_correct']].to_csv('stimuli_results_detailed.csv', index=False)
    print(" 'stimuli_results_detailed.csv' created (all stimuli trials for all participants).")
