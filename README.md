# 🧠 MDFD Data Analysis

Data analysis and visualization pipeline for the **McGill Diverse Face Database (MDFD)**. ([Link to preprint](https://www.researchgate.net/publication/397891829_The_McGill_Diverse_Face_Database_92_Complex_Mental_States_Across_Socially_Perceived_Racial_Categories))

Minimal experience with Python? No problem. This guide is meant to walk you through everything step by step.

---

## 📂 Data

All data and figures can already be found in this repository.

- ```preprocessed_datafiles``` contains the experimental data in each of the three blocks, as well as a version which merges them all together.

- ```final_datafiles``` contains the output of this analysis pipeline.
    - ```MDFD_experiment_one_data.xlsx``` contains individual responses for the 4-AFC paradigm, as well as the table included in the publication listing the mean recognition accuracy values.
    - ```MDFD_experiment_two_data.xlsx``` contains individual responses for the grid paradigm, mean values for valence and arousal, and the reported measures of agreement (i.e., cluster size and JSD).
    - ```MDFD_subjects_and_actors_data.xlsx``` contains demographic information of participants, survey scores, as well as the reported actor traits.

## 📦 Installation

You'll need **Python** and a few scientific packages installed. The easiest way to manage this is with **conda**, a tool that creates an isolated environment so this project's packages don't interfere with anything else on your computer.

### 1. Install conda (if you don't already have it)

If you don't have conda installed, download **Miniconda** (a lightweight version of Anaconda):
👉 [https://www.anaconda.com/docs/getting-started/miniconda/install](https://www.anaconda.com/docs/getting-started/miniconda/install)

Follow the installer for your operating system (Windows, macOS, or Linux).

### 2. Download this repository

- Click the green **`<> Code`** button at the top of this page → **Download ZIP**
- Unzip it somewhere easy to find, like your Desktop or Documents folder

*(If you're comfortable with git, you can alternatively run `git clone https://github.com/Hctor99/MDFD-data-analysis.git`)*

### 3. Open a terminal

- **macOS**: open the **Terminal** app (search for it with Spotlight, `Cmd + Space`)
- **Windows**: open **Anaconda Prompt** (installed alongside Miniconda)

Navigate into the folder you just unzipped, for example:

```bash
cd Desktop/MDFD-data-analysis
```

### 4. Create the conda environment

```bash
conda create -n mdfd_env python=3.11
conda activate mdfd_env
```

You should now see `(mdfd_env)` appear at the start of your terminal line. That means the environment is active.

### 5. Install the required packages

```bash
pip install -r requirements.txt
```

This installs all the packages needed for the analysis (e.g., `pandas`, `numpy`, `scipy`, etc)

---

## ▶️ How to Run the Code

### Preprocessing

The script `merge-datafiles.py` fetches the preprocessed datafiles for the three experimental blocks (**B1**, **B2**, **B3**), merges them together into a single combined dataset, and computes some basic statistics.

To run it, activate your environment and run:

```bash
conda activate mdfd_env
python merge-datafiles.py
```

**Output:** the merged data is saved to:

```
preprocessed_datafiles/MDFD_all_blocks.xlsx
```

> 💡 **You can skip this step if you'd like.** This output file is already included in the repository, so if you just want to explore the final merged data, you can go straight to the next step.

### Main analyses

To reproduce all analyses and figures related to Experiment One, run: 

```bash
python analysis-labels-ExpOne.py
```

To reproduce all analyses and figures related to Experiment Two, run: 

```bash
python analysis-grid-ExpTwo.py
```

Finally, to reproduce the correlation analyses, run:

```bash
python analysis-correlations.py
```

**Output:** all figures are saved to ```figures```, and all processed data is saved to ```final_datafiles```

> 💡 See **[📂 Data](#-data)** for more details.

If Jupyter Notebook is preferred, all these analyses can also be run in ```analysis-and-visualization.ipynb```.

---

## 🙋 Need Help?

If something doesn't work, double check:
- You activated the environment (`conda activate mdfd_env`) before running `pip install` or `jupyter notebook`
- You're running the commands from inside the unzipped repository folder

Feel free to [open an issue](https://github.com/Hctor99/MDFD-data-analysis/issues) if you get stuck or contact me at hectorleosme@gmail.com
