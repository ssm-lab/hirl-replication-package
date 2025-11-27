import os
import pandas as pd
import matplotlib.pyplot as plt
from plot_likert import plot_likert
from plot_likert import colors as lkcolors
from PyPDF2 import PdfReader, PdfWriter
from pathlib import Path
import numpy as np
from scipy.stats import chi2_contingency


def autosize_height(n_items, per_bar=0.5, pad=0.6):
    return n_items * per_bar + pad

def build_fig1_frames(p1, p2):
    # (a)–(f), before/after interleaved
    fig1_before = pd.DataFrame({
        '(a) Trust in AI (Before)': p1.iloc[:, 7],
        '(b) Ease of Use (Before)': p1.iloc[:, 8],
        '(c) Dependability (Before)': p1.iloc[:, 9],
        '(d) Predictability (Before)': p1.iloc[:, 10],
        '(e) Goal Alignment (Before)': p1.iloc[:, 11],
        '(f) Transparency (Before)': p1.iloc[:, 12]
    })
    fig1_after = pd.DataFrame({
        '(a) Trust in AI (After)': p2.iloc[:, 7],
        '(b) Ease of Use (After)': p2.iloc[:, 8],
        '(c) Dependability (After)': p2.iloc[:, 9],
        '(d) Predictability (After)': p2.iloc[:, 10],
        '(e) Goal Alignment (After)': p2.iloc[:, 11],
        '(f) Transparency (After)': p2.iloc[:, 12]
    })
    fig1_data = pd.DataFrame()
    for letter in ['(a)', '(b)', '(c)', '(d)', '(e)', '(f)']:
        before_col = [col for col in fig1_before.columns if col.startswith(letter)][0]
        after_col  = [col for col in fig1_after.columns  if col.startswith(letter)][0]
        fig1_data[before_col] = fig1_before[before_col]
        fig1_data[after_col]  = fig1_after[after_col]
    return fig1_data

def build_fig2_frames(p2):
    return pd.DataFrame({
        'Observation → improved confidence':      p2.iloc[:, 13],
        'Observation → improved understandability': p2.iloc[:, 14],
        'Collaboration was useful for performance':    p2.iloc[:, 15],
        'I prefer the agent to work without guidance': p2.iloc[:, 16]
    })

def build_fig3_frames(p2):
    return pd.DataFrame({
        'Increased Focus':    p2.iloc[:, 17],
        'Decreased Confidence': p2.iloc[:, 18]
    })


def draw_combined_and_save(all_data, likert_scale, width, out_pdf,
                           show_y_labels=True):
    n1 = 12
    n2 = 4
    n3 = 2
    PER_BAR = 0.5
    HEIGHT = autosize_height(n1, PER_BAR) + autosize_height(n2, PER_BAR) + autosize_height(n3, PER_BAR) + 0.4

    ax = plot_likert(all_data, likert_scale,
                     plot_percentage=True,
                     colors=lkcolors.default_with_darker_neutral,
                     figsize=(width, HEIGHT),
                     legend=False)

    for side in ["top", "right", "left", "bottom"]:
        ax.spines[side].set_visible(False)
    if show_y_labels:
        ax.tick_params(axis='y', labelsize=15)
    if not show_y_labels:
        ax.tick_params(axis="y", length=0)
        ax.set_yticklabels([])
    ax.tick_params(axis="x", length=0)
    ax.set_xticklabels([])
    ax.set_xlabel("")

    label_colors = ['white','white','white','white','white','white']
    for i, (bars, color) in enumerate(zip(ax.containers, label_colors)):
        if i == 0:
            continue
        labels = [f'{v:.0f}%' if v > 3 else '' for v in bars.datavalues]
        ax.bar_label(bars, labels=labels, label_type='center', fontsize=12.5, weight='bold', color=color)

    fig = ax.figure
    fig.tight_layout()
    fig.savefig(OUT_DIR / out_pdf,   bbox_inches='tight')
    return (n1, n2, n3)

def crop_by_rows(src_pdf, n1, n2, n3, out1, out2, out3):
    reader = PdfReader(str(OUT_DIR / src_pdf))
    page = reader.pages[0]
    page_height = float(page.mediabox.height)
    page_width  = float(page.mediabox.width)

    total_bars = n1 + n2 + n3
    bar_height = page_height / total_bars

    split1 = page_height - (bar_height * n1)
    split2 = page_height - (bar_height * (n1 + n2))

    # fig1
    w1 = PdfWriter()
    p1 = reader.pages[0]
    p1.mediabox.lower_left  = (0, split1)
    p1.mediabox.upper_right = (page_width, page_height)
    w1.add_page(p1)
    with open(OUT_DIR / out1, 'wb') as f:
        w1.write(f)

    # fig2
    w2 = PdfWriter()
    p2 = reader.pages[0]
    p2.mediabox.lower_left  = (0, split2)
    p2.mediabox.upper_right = (page_width, split1)
    w2.add_page(p2)
    with open(OUT_DIR / out2, 'wb') as f:
        w2.write(f)

    # fig3
    w3 = PdfWriter()
    p3 = reader.pages[0]
    p3.mediabox.lower_left  = (0, 0)
    p3.mediabox.upper_right = (page_width, split2)
    w3.add_page(p3)
    with open(OUT_DIR / out3, 'wb') as f:
        w3.write(f)


# --- chi square helpers ---
# --- Chi-square helpers (row-based split, 3-bin Likert) ---

THREE_BINS = ['Disagree', 'Neutral', 'Agree']

def collapse_to_three(series: pd.Series) -> np.ndarray:
    s = series.astype(str).str.strip()
    return np.where(s.isin(['Strongly disagree','Disagree']), 'Disagree',
           np.where(s.eq('Neutral'), 'Neutral',
           np.where(s.isin(['Agree','Strongly agree']), 'Agree', np.nan)))

def counts_three(series: pd.Series) -> np.ndarray:
    s3 = pd.Series(collapse_to_three(series)).dropna()
    return s3.value_counts().reindex(THREE_BINS, fill_value=0).to_numpy()

def pooled_counts_cols(df: pd.DataFrame, col_idx: list[int], row_slice: slice) -> np.ndarray:
    """Concatenate responses for df.iloc[row_slice, col_idx] then count into 3 bins."""
    pooled = pd.concat([df.iloc[row_slice, i] for i in col_idx], ignore_index=True)
    return counts_three(pooled)

def chisq_2x3(g1_counts: np.ndarray, g2_counts: np.ndarray):
    table = np.vstack([g1_counts, g2_counts])  # shape (2,3)
    chi2, p, dof, expected = chi2_contingency(table, correction=False)
    n = table.sum()
    return chi2, p, dof, table, expected

def run_group_chi2_by_rows(p1: pd.DataFrame, p2: pd.DataFrame, out_csv_path):
    """
    Group1: rows 2–16 (iloc[1:16]); Group2: rows 17–31 (iloc[16:31]).
    Figure 1 = P2 cols 7–12.
    Figure 2 = P2 cols 13–16.
    Figure 3 = P2 cols 17–18.
    """
    g1_rows = slice(1, 16)
    g2_rows = slice(16, 31)

    fig1_after_cols = list(range(7, 13))
    fig2_cols = list(range(13, 17))
    fig3_cols = list(range(17, 19))

    results = []
    for name, cols in [
        ("Figure1_After_only", fig1_after_cols),
        ("Figure2_Collaboration", fig2_cols),
        ("Figure3_Time", fig3_cols),
    ]:
        g1 = pooled_counts_cols(p2, cols, g1_rows)
        g2 = pooled_counts_cols(p2, cols, g2_rows)
        chi2, p, dof, table, expected = chisq_2x3(g1, g2)

        print(f"\n{name}")
        print(f"  Group1 counts [Disagree, Neutral, Agree]: {g1.tolist()}")
        print(f"  Group2 counts [Disagree, Neutral, Agree]: {g2.tolist()}")
        print(f"  Chi²={chi2:.3f}, dof={dof}, p={p:.4f}")

        results.append({
            "set": name,
            "g1_disagree": int(g1[0]), "g1_neutral": int(g1[1]), "g1_agree": int(g1[2]),
            "g2_disagree": int(g2[0]), "g2_neutral": int(g2[1]), "g2_agree": int(g2[2]),
            "chi2": chi2, "dof": dof, "p_value": p
        })

    pd.DataFrame(results).to_csv(out_csv_path, index=False)
    print("\nSaved chi-square summary to:", out_csv_path)


# ================= MAIN =================
if __name__ == "__main__":
    # ---------------- paths & data ----------------
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    DATA_DIR = PROJECT_ROOT / "data"
    OUT_DIR = PROJECT_ROOT / "output"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    p1 = pd.read_excel(DATA_DIR / "P1-1-30.xlsx")
    p2 = pd.read_excel(DATA_DIR / "P2-1-30.xlsx")

    # likert order
    likert_scale = ['Strongly disagree','Disagree','Neutral','Agree','Strongly agree']
    width = 15

    # ---------- FULL SAMPLE ----------
    fig1_data = build_fig1_frames(p1, p2)
    fig2_data = build_fig2_frames(p2)
    fig3_data = build_fig3_frames(p2)
    all_data  = pd.concat([fig1_data, fig2_data, fig3_data], axis=1)

    draw_combined_and_save(
        all_data, likert_scale, width,
        out_pdf='label_all_combined.pdf',
        show_y_labels=True
    )
    n1, n2, n3 = draw_combined_and_save(
        all_data, likert_scale, width,
        out_pdf='all_combined.pdf',
        show_y_labels=False
    )
    crop_by_rows('label_all_combined.pdf', n1, n2, n3,
                 'label_figure1.pdf', 'label_figure2.pdf', 'label_figure3.pdf')
    crop_by_rows('all_combined.pdf', n1, n2, n3,
                 'figure1.pdf', 'figure2.pdf', 'figure3.pdf')




    # ---------- SUB GROUP GENERATION ----------
    # Group 1: IDs 1–15
    g1_p1 = p1.iloc[1:16].reset_index(drop=True)
    g1_p2 = p2.iloc[1:16].reset_index(drop=True)
    # Group 2: IDs 16–30
    g2_p1 = p1.iloc[16:31].reset_index(drop=True)
    g2_p2 = p2.iloc[16:31].reset_index(drop=True)

    # ---------- GROUP 1: IDs 1–15 ----------
    g1_fig1 = build_fig1_frames(g1_p1, g1_p2)
    g1_fig2 = build_fig2_frames(g1_p2)
    g1_fig3 = build_fig3_frames(g1_p2)
    g1_all = pd.concat([g1_fig1, g1_fig2, g1_fig3], axis=1)

    draw_combined_and_save(
        g1_all, likert_scale, width,
        out_pdf='group1/label_all_combined_Group1.pdf',
        show_y_labels=True
    )
    n1, n2, n3 = draw_combined_and_save(
        g1_all, likert_scale, width,
        out_pdf='group1/all_combined_Group1.pdf',
        show_y_labels=False
    )
    crop_by_rows('group1/label_all_combined_Group1.pdf', n1, n2, n3,
                 'group1/label_figure1-Group1.pdf', 'group1/label_figure2-Group1.pdf', 'group1/label_figure3-Group1.pdf')
    crop_by_rows('group1/all_combined_Group1.pdf', n1, n2, n3,
                 'group1/figure1-Group1.pdf', 'group1/figure2-Group1.pdf', 'group1/figure3-Group1.pdf')

    # ---------- GROUP 2: IDs 16–30 ----------
    g2_fig1 = build_fig1_frames(g2_p1, g2_p2)
    g2_fig2 = build_fig2_frames(g2_p2)
    g2_fig3 = build_fig3_frames(g2_p2)
    g2_all = pd.concat([g2_fig1, g2_fig2, g2_fig3], axis=1)

    draw_combined_and_save(
        g2_all, likert_scale, width,
        out_pdf='group2/label_all_combined_Group2.pdf',
        show_y_labels=True
    )
    n1, n2, n3 = draw_combined_and_save(
        g2_all, likert_scale, width,
        out_pdf='group2/all_combined_Group2.pdf',
        show_y_labels=False
    )
    crop_by_rows('group2/label_all_combined_Group2.pdf', n1, n2, n3,
                 'group2/label_figure1-Group2.pdf', 'group2/label_figure2-Group2.pdf', 'group2/label_figure3-Group2.pdf')
    crop_by_rows('group2/all_combined_Group2.pdf', n1, n2, n3,
                 'group2/figure1-Group2.pdf', 'group2/figure2-Group2.pdf', 'group2/figure3-Group2.pdf')

    # --- chi-square: Group1 vs Group2 ---
    run_group_chi2_by_rows(p1, p2, OUT_DIR / "chi2_group1_vs_group2.csv")
