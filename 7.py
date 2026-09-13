import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman'],
    'font.size': 8,
    'axes.titlesize': 8,
    'axes.labelsize': 8,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 8
})

# --------------------------------------------------
# Configuration
# --------------------------------------------------

# A1 removed so it never appears in plots/statistics
CEFR_ORDER = ['A2', 'B1', 'B2', 'C1', 'C2']

PARAMS = [
    'Grammar CEFR',
    'Intonation CEFR',
    'Pronunciation CEFR',
    'Vocabulary CEFR'
]

PARAM_NAMES = [
    'Grammar',
    'Intonation',
    'Pronunciation',
    'Vocabulary'
]

# Outcome column to analyze from "whole table"
OUTCOME_COL = 'Speech rate/wpm'
OUTCOME_LABEL = 'Speech Rate (WPM)'

# --------------------------------------------------
# Audio IDs to exclude (rejected files)
# --------------------------------------------------

EXCLUDE_AUDIO_IDS = {
    "022_09_27_161749-31ceb303-cef0-4afb-b869-d8ffec3e66ea_us",
    "022_09_28_050127-016342db-3a92-4610-86e0-f8194658bb02_eu",
    "2022_10_10_015426-001c3cc2-dcda-4549-aae3-0ff19741f8a0_us",
    "2022_10_10_021951-ffd92b78-e6ba-458d-803d-df9b56623d42_us",
    "2022_10_10_113051-40214422-f92f-4ecb-b6d6-adcf42ee179e_as",
    "2022_10_10_113802-d7d6a3dc-993b-4436-9109-0adf61595cb5_as",
    "2022_10_10_124102-caddab9a-9abd-4420-a38e-b1ba01d681d5_us",
    "2022_10_10_144522-77f1a92d-872e-440a-993f-fdea92171697_as",
    "2022_10_18_085705-6116563d-ba63-4b6b-96dd-bc971b82063f_eu",
    "2022_10_18_090223-56a89377-5a17-4d5d-90fd-c4457f199575_eu",
    "2022_10_18_090426-142a9c9d-7f4a-4640-9462-22cde3901af1_eu",
    "2022_10_30_172514-9b20ee98-7932-414f-816d-099699c5b91c_eu",
    "2022_11_13_034956-5ecf8146-014d-4d23-8e83-4b26f7efe094_us",
    "2022_09_15_210712-0f9b1622-6875-48d1-ae16-b094e71d1957_eu",
    "2022_09_15_215237-87dd2194-893b-4300-ac0c-b1bec4c3942d_eu",
    "2022_09_23_173347-6ca719f1-1583-41f0-abbe-d1ce53e6aae9_us"
}

# --------------------------------------------------
# Data loading
# --------------------------------------------------

def load_data(file_path):
    """Load and merge the datasets from Excel."""
    df_main = pd.read_excel(file_path, sheet_name='whole table')
    df_cefr = pd.read_excel(file_path, sheet_name='CEFR')

    df = pd.merge(df_main, df_cefr, on='Audio ID', how='inner')

    # ---- EXCLUDE REJECTED FILES (ONLY ADDITION) ----
    before = len(df)
    df = df[~df['Audio ID'].astype(str).isin(EXCLUDE_AUDIO_IDS)]
    after = len(df)
    print(f"Excluded {before - after} rejected files based on Audio ID list.")

    return df

# --------------------------------------------------
# Four-panel CI figure (Speech rate)
# --------------------------------------------------

def create_four_panel_ci_figure(df, output_dir='.'):
    """
    Create a 2x2 figure: Speech rate (wpm) across CEFR levels
    for Grammar / Intonation / Pronunciation / Vocabulary.
    """

    # Ensure outcome column is numeric (coerce errors to NaN)
    df = df.copy()
    df[OUTCOME_COL] = pd.to_numeric(df[OUTCOME_COL], errors='coerce')

    fig, axes = plt.subplots(2, 2, figsize=(6.8, 5.5))
    fig.suptitle(
        f'{OUTCOME_LABEL} across CEFR levels (Mean ± 95% CI)',
        y=0.98
    )

    # Numeric map for Spearman (A1 excluded)
    cefr_map = {'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5, 'C2': 6}

    for idx, (param, pname) in enumerate(zip(PARAMS, PARAM_NAMES)):
        ax = axes[idx // 2, idx % 2]

        # Keep only rows with both outcome + CEFR rating
        df_param = df[[OUTCOME_COL, param]].dropna()

        # Exclude A1 explicitly (extra safety)
        df_param = df_param[df_param[param].isin(CEFR_ORDER)]

        stats_rows = []
        for level in CEFR_ORDER:
            vals = df_param.loc[df_param[param] == level, OUTCOME_COL]
            if len(vals) > 0:
                mean = float(np.mean(vals))
                se = float(np.std(vals, ddof=1) / np.sqrt(len(vals))) if len(vals) > 1 else 0.0
                ci = 1.96 * se
                stats_rows.append({
                    'level': level,
                    'mean': mean,
                    'ci': ci,
                    'n': int(len(vals))
                })

        if not stats_rows:
            ax.set_title(f'{pname}\n(no data)')
            ax.axis('off')
            continue

        stats_df = pd.DataFrame(stats_rows)
        x = np.arange(len(stats_df))

        # Plot mean ± 95% CI (APA-friendly: black)
        ax.errorbar(
            x,
            stats_df['mean'].values,
            yerr=stats_df['ci'].values,
            fmt='o-',
            color='black',
            markersize=4,
            linewidth=1,
            capsize=3
        )

        # Add n labels
        y_span = (stats_df['mean'].max() - stats_df['mean'].min())
        y_offset = 0.03 * y_span if y_span > 0 else 1.0
        for i, r in stats_df.iterrows():
            ax.text(i, r['mean'] + y_offset, f"n={r['n']}", ha='center', va='bottom')

        # Spearman correlation using individual samples
        cefr_numeric = df_param[param].map(cefr_map)
        valid = cefr_numeric.notna() & df_param[OUTCOME_COL].notna()

        if valid.sum() >= 3:
            rho, p = stats.spearmanr(
                cefr_numeric[valid],
                df_param.loc[valid, OUTCOME_COL]
            )
            p_str = '< .001' if p < 0.001 else f'= {p:.3f}'
            title = f'{pname}\nρ = {rho:.2f}, p {p_str}'
        else:
            title = f'{pname}\n(ρ not computed)'

        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(stats_df['level'].values)
        ax.set_xlabel('CEFR level')

        if idx % 2 == 0:
            ax.set_ylabel(OUTCOME_LABEL)

        ax.grid(alpha=0.3)
        ax.set_axisbelow(True)

        # Clean spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    plt.tight_layout()

    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, 'fig_speechrate_features_ci.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved: {save_path}")

# --------------------------------------------------
# Main
# --------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate speech rate vs CEFR figures')
    parser.add_argument(
        '--input', '-i',
        default=r"C:\Users\AnaIs\Desktop\Faculdade\Mestrado\tese\Mehtodology\Excel_for_each_file_1.xlsx",
        help='Path to input Excel file'
    )
    parser.add_argument(
        '--output', '-o',
        default=r"C:\Users\AnaIs\Desktop\Faculdade\Mestrado\tese\Mehtodology\figures",
        help='Output directory for figures'
    )

    args = parser.parse_args()

    df = load_data(args.input)
    create_four_panel_ci_figure(df, output_dir=args.output)

if __name__ == "__main__":
    main()