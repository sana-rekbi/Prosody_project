# Prosody Project

**Link to the experiment:** [Mindprobe JATOS Link](https://jatos.mindprobe.eu/publix/21TAbU2U8nC)

## 📂 Project Description

This repository contains the data and analysis scripts for a prosody perception experiment focused on Mandarin Chinese tones and syllable structures.

The experiment investigates whether Mandarin's different tones, initials, or finals affect syllable discrimination performance.  
Participants heard two syllables and judged whether they were the same ("m") or different ("q").

---

## 📄 Files and Folders

### `Prosody_experiement_sheet (1).xlsx`

This Excel file contains **detailed information** about the experiment stimuli:

- **Stimulus block** (target syllable pairs) and **filler block** (non-target pairs).
- For each trial:
  - **Order** of presentation,
  - **Syllable combinations** (CV, CVV, CVC, CCVCC structures),
  - **Sound 1** and **Sound 2** names,
  - **Correct response** (`m` for same, `q` for different).

Example of the sheet structure:

| Order | Syllable Combinations | Sound 1 | Sound 2 | Correct Response |
|:------|:----------------------|:--------|:--------|:-----------------|
| 1     | CV (MA)               | ma1     | ma2     | q                |
| 7     | CV (MA)               | ma2     | ma2     | m                |
| 9     | CV (YI)               | yi1     | yi1     | m                |
| ...   | ...                   | ...     | ...     | ...              |

🔹 **Research Question**:  
How Mandarin's different tones, initials, or finals affect perception.

🔹 **Independent Variables**:  
- Mandarin 4 tones,
- Syllable combinations (CV, CVV, CVC, CCVCC).

🔹 **Task type**:  
Discrimination task — participants hear two syllables and judge whether they are the same or different.

---

### `jatos_results_data_20250426131918/`

This folder contains the **raw JATOS experiment results** for **16 participants**:

- Each participant has a separate folder with `data.csv` inside.
- These files record trial-by-trial responses (stimuli, response, reaction times, etc.).

---

### `results-survey349233 (2).csv` and `results-survey349233 (1).xlsx`

These files contain the **LimeSurvey questionnaire results**:

- Participants' background information (e.g., native language, age),
- Additional metadata about each participant.

---

### 📈 Analysis Outputs

- `merged_results.csv`: Combined participant performance metrics merged with survey responses.
- `stimuli_results_detailed.csv`: Detailed trial-by-trial data (stimuli trials only).

- Plots generated during analysis:
  - `histogram_accuracy.png`
  - `histogram_accuracy_stimuli.png`
  - `boxplot_accuracy_language.png`
  - `boxplot_accuracy_language_stimuli.png`
  - `boxplot_rt_language.png`
  - `boxplot_rt_language_stimuli.png`
  - `histogram_rt_stimuli.png`
  - `scatter_rt_vs_accuracy.png`
  - `accuracy_per_tone_pair_stim.png`
  - `accuracy_tone_pair.png`

These plots illustrate distributions of accuracy and reaction times, group comparisons (Tonal vs Non-Tonal speakers), and correlation analyses.

---

### 🛠️ Analysis Scripts

- `script_analyse.py`:  
  Script analyzing all trials (stimuli + fillers).  
  Generates merged results and plots.

- `stim_analysis.py`:  
  Script focusing only on **stimuli trials**.  
  Filters stimulus trials, calculates performance metrics, and produces visualizations related to stimuli discrimination only.
