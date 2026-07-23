# 🧠 MDFD Data Analysis

Data analysis and visualization pipeline for the **McGill Diverse Face Database (MDFD)**. [https://www.researchgate.net/publication/397891829_The_McGill_Diverse_Face_Database_92_Complex_Mental_States_Across_Socially_Perceived_Racial_Categories](Link to preprint)

Minimal experience with Python? No problem. This guide is meant to walk you through everything step by step.

---

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

You should now see `(mdfd_env)` appear at the start of your terminal line — that means the environment is active.

### 5. Install the required packages

```bash
pip install -r requirements.txt
```

This installs all the packages needed for the analysis (e.g., `pandas`, `numpy`, `scipy`, etc)

### 6. Launch Jupyter Notebook

```bash
jupyter notebook
```

This opens Jupyter in your browser. From there, click on `analysis-and-visualization.ipynb` to open the main analysis notebook.

---

## ▶️ How to Run the Code

*(Placeholder sections below — to be filled in with actual run instructions)*

### Running `Final-data-table.py`

*TBD*

### Running `analysis-and-visualization.ipynb`

*TBD*

---

## 🙋 Need Help?

If something doesn't work, double check:
- You activated the environment (`conda activate mdfd_env`) before running `pip install` or `jupyter notebook`
- You're running the commands from inside the unzipped repository folder

Feel free to [open an issue](https://github.com/Hctor99/MDFD-data-analysis/issues) if you get stuck or contact me at hectorleosme@gmail.com
