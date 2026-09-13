import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import os

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

# A1 removed here so it never appears in plots/statistics
CEFR_ORDER = ['A2', 'B1', 'B2', 'C1', 'C2']

PARAMS = [
    'Grammar CEFR',
    'Intonation CEFR',
    'Pronunciation CEFR',
    'Vocabulary CEFR'
]

PARAM_NAMES = [
    'grammar',
    'intonation',
    'pronunciation',
    'vocabulary'
]

# Okabe–Ito color-blind friendly palette
CEFR_COLORS = {
    'A1': '#000000',  # kept for completeness, but not used
    'A2': '#E69F00',
    'B1': '#56B4E9',
    'B2': '#009E73',
    'C1': '#0072B2',
    'C2': '#999999'
}

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
    df_main = pd.read_excel(file_path, sheet_name='whole table')
    df_cefr = pd.read_excel(file_path, sheet_name='CEFR')

    df = pd.merge(df_main, df_cefr, on='Audio ID', how='inner')
    df['disruptive_pct'] = df['% of pauses and lengthenings breaking syntactic units']

    # ---- EXCLUDE REJECTED FILES (ONLY ADDITION) ----
    before = len(df)
    df = df[~df['Audio ID'].astype(str).isin(EXCLUDE_AUDIO_IDS)]
    after = len(df)
    print(f"Excluded {before - after} rejected files based on Audio ID list.")

    return df

# --------------------------------------------------
# Boxplots (one per parameter)
# --------------------------------------------------

def create_boxplots_all_params(df, output_dir):
    for param, short_name in zip(PARAMS, PARAM_NAMES):

        df_param = df[['disruptive_pct', param]].dropna()
        df_param = df_param[df_param[param].isin(CEFR_ORDER)]

        plot_data = []
        levels = []

        for level in CEFR_ORDER:
            values = df_param.loc[df_param[param] == level, 'disruptive_pct']
            if len(values) > 0:
                plot_data.append(values.values)
                levels.append(level)

        if not plot_data:
            continue

        fig, ax = plt.subplots(figsize=(3.4, 2.6))

        bp = ax.boxplot(
            plot_data,
            patch_artist=True,
            widths=0.6,
            showfliers=True,
            flierprops=dict(marker='o', markersize=3),
            medianprops=dict(color='black', linewidth=1),
            boxprops=dict(linewidth=0.8),
            whiskerprops=dict(linewidth=0.8),
            capprops=dict(linewidth=0.8)
        )

        for patch, level in zip(bp['boxes'], levels):
            patch.set_facecolor(CEFR_COLORS.get(level, '#CCCCCC'))
            patch.set_edgecolor('black')

        ax.set_xlabel('CEFR level')
        ax.set_ylabel('Proportion of disruptive pauses and lengthenings ([0, 1] range)')

        ax.set_xticks(range(1, len(levels) + 1))
        ax.set_xticklabels(levels)

        ax.set_ylim(0, 1.0)
        ax.grid(axis='y', alpha=0.3)
        ax.set_axisbelow(True)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()

        filename = f'fig_box_{short_name}.png'
        plt.savefig(
            os.path.join(output_dir, filename),
            dpi=300,
            bbox_inches='tight',
            facecolor='white'
        )
        plt.close()

# --------------------------------------------------
# Four-panel CI figure
# --------------------------------------------------

def create_four_panel_figure(df, output_dir):

    fig, axes = plt.subplots(2, 2, figsize=(6.8, 5.5))
    fig.suptitle(
        'Disruptive pause and lengthening patterns across CEFR levels (95% CI)',
        y=0.98
    )

    cefr_map = {'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5, 'C2': 6}

    for idx, (param, short_name) in enumerate(zip(PARAMS, PARAM_NAMES)):
        ax = axes[idx // 2, idx % 2]

        df_param = df[['disruptive_pct', param]].dropna()
        df_param = df_param[df_param[param].isin(CEFR_ORDER)]

        stats_data = []
        for level in CEFR_ORDER:
            vals = df_param.loc[df_param[param] == level, 'disruptive_pct']
            if len(vals) > 0:
                mean = float(np.mean(vals))
                se = float(np.std(vals, ddof=1) / np.sqrt(len(vals))) if len(vals) > 1 else 0.0
                ci = 1.96 * se
                stats_data.append((level, mean, ci, int(len(vals))))

        if not stats_data:
            ax.set_title(f'{short_name.capitalize()} (no data)')
            ax.axis('off')
            continue

        levels, means, cis, ns = zip(*stats_data)
        x = np.arange(len(levels))

        ax.errorbar(
            x, means, yerr=cis,
            fmt='o-', color='black',
            markersize=4, linewidth=1,
            capsize=3
        )

        y_min = min(means) - max(cis)
        y_max = max(means) + max(cis)
        y_span = (y_max - y_min) if (y_max - y_min) > 0 else 1.0
        for i, n in enumerate(ns):
            ax.text(i, means[i] + 0.03 * y_span, f'n={n}', ha='center', va='bottom')

        # --------------------------------------------------
        # Spearman correlation using individual samples
        # --------------------------------------------------
        cefr_numeric = df_param[param].map(cefr_map)
        valid = cefr_numeric.notna() & df_param['disruptive_pct'].notna()

        if valid.sum() >= 3:
            rho, p = stats.spearmanr(
                cefr_numeric[valid],
                df_param.loc[valid, 'disruptive_pct']
            )
            p_str = '< .001' if p < 0.001 else f'= {p:.3f}'
            ax.set_title(f'{short_name.capitalize()} (ρ = {rho:.2f}, p {p_str})')
        else:
            ax.set_title(f'{short_name.capitalize()} (ρ not computed)')

        ax.set_xticks(x)
        ax.set_xticklabels(levels)
        ax.set_xlabel('CEFR level')

        if idx % 2 == 0:
            ax.set_ylabel('Proportion of disruptive pauses and lengthenings')

        ax.grid(alpha=0.3)
        ax.set_axisbelow(True)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    plt.tight_layout()

    plt.savefig(
        os.path.join(output_dir, 'fig_features_ci.png'),
        dpi=300,
        bbox_inches='tight',
        facecolor='white'
    )
    plt.close()

# --------------------------------------------------
# Main
# --------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input', '-i',
        default=r'c:/Users/AnaIs/Desktop/Faculdade/Mestrado/tese/Mehtodology/Excel_for_each_file_1.xlsx'
    )
    parser.add_argument(
        '--output', '-o',
        default=r'C:\Users\AnaIs\Desktop\Faculdade\Mestrado\tese\Mehtodology\figures'
    )

    args = parser.parse_args()
    os.makedirs(args.output, exist_ok=True)

    df = load_data(args.input)

    create_boxplots_all_params(df, args.output)
    create_four_panel_figure(df, args.output)

if __name__ == "__main__":
    main()