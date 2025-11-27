# ---------- Sankey: Trust (before->after) ----------
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
import numpy as np
from PIL import Image

LIKERT5 = ['Strongly disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly agree']

THREE_BINS = ['Disagree', 'Neutral', 'Agree']

def _to_three_bins(s: pd.Series) -> pd.Series:
    s = s.astype(str).str.strip()
    return (
        s.replace({
            'Strongly disagree': 'Disagree',
            'Disagree': 'Disagree',
            'Neutral': 'Neutral',
            'Agree': 'Agree',
            'Strongly agree': 'Agree'
        })
        .where(lambda x: x.isin(THREE_BINS))
        .dropna()
    )

def _clean_likert(s: pd.Series) -> pd.Series:
    s = s.astype(str).str.strip()
    s = s.where(s.isin(LIKERT5))
    return s.dropna()

def make_trust_sankey(p1: pd.DataFrame, p2: pd.DataFrame, out_dir: Path,
                      before_col_idx: int = 7, after_col_idx: int = 7,
                      out_name: str = "sankey_trust"):
    """
    Build a Sankey diagram for Trust at the individual level.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    before = _clean_likert(p1.iloc[:, before_col_idx]).reset_index(drop=True)
    after  = _clean_likert(p2.iloc[:, after_col_idx]).reset_index(drop=True)
    df = pd.DataFrame({"before": before, "after": after}).dropna().reset_index(drop=True)
    trans = (pd.crosstab(df["before"], df["after"])
               .reindex(index=LIKERT5, columns=LIKERT5, fill_value=0))
    trans.to_csv(out_dir / f"{out_name}_transition.csv")


    before_nodes = [f"Before: {lab}" for lab in LIKERT5]
    after_nodes  = [f"After: {lab}"  for lab in LIKERT5]
    labels = before_nodes + after_nodes

    src, tgt, val = [], [], []
    for i_b, b in enumerate(LIKERT5):
        for i_a, a in enumerate(LIKERT5):
            v = int(trans.loc[b, a])
            if v > 0:
                src.append(i_b)
                tgt.append(5 + i_a)
                val.append(v)


    node_colors = (
        ['#B22222', '#F08080', '#C0C0C0', '#6495ED', '#00008B'] +  # Before
        ['#B22222', '#F08080', '#C0C0C0', '#6495ED', '#00008B']     # After
    )

    fig = go.Figure(data=[go.Sankey(
        arrangement="fixed",
        node=dict(
            pad=10, thickness=10,
            line=dict(color="rgba(0,0,0,0)", width=0.1),
            label=labels, color=node_colors,
            # x=x_positions,
            # y=y_positions
        ),
        link=dict(source=src, target=tgt, value=val))])

    fig.update_layout(font=dict(size=18.5),
                      margin=dict(l=10, r=10, t=10, b=10),
    height = 400,
    width = 700
    )
    fig.write_image(str(out_dir / f"{out_name}.png"), scale=4)
    png_path = str(out_dir / f"{out_name}.png")
    try:
        pdf_path = str(out_dir / f"{out_name}.pdf")
        img = Image.open(png_path)

        if img.mode == 'RGBA':
            img = img.convert('RGB')
        img.save(pdf_path, "PDF", resolution=300, quality=100)
        print(f"PDF saved to {pdf_path}")
    except Exception as e:
        print(f"PDF export failed: {e}")

    print(f"Sankey saved to {out_dir / (out_name + '.png')} and CSV saved to {out_dir / (out_name + '_transition.csv')}")


def make_trust_sankey_3bin(p1: pd.DataFrame, p2: pd.DataFrame, out_dir: Path,
                           before_col_idx: int = 7, after_col_idx: int = 7,
                           out_name: str = "sankey_trust_3x3"):
    out_dir.mkdir(parents=True, exist_ok=True)
    # Map to 3 bins
    before = _to_three_bins(p1.iloc[:, before_col_idx]).reset_index(drop=True)
    after  = _to_three_bins(p2.iloc[:, after_col_idx]).reset_index(drop=True)
    df = pd.DataFrame({"before": before, "after": after}).dropna().reset_index(drop=True)
    # 3x3 transition matrix with fixed order
    trans = (pd.crosstab(df["before"], df["after"])
               .reindex(index=THREE_BINS, columns=THREE_BINS, fill_value=0))
    trans.to_csv(out_dir / f"{out_name}_transition.csv")

    # nodes & links
    before_nodes = [f"Before: {lab}" for lab in THREE_BINS]
    after_nodes  = [f"After: {lab}"  for lab in THREE_BINS]
    labels = before_nodes + after_nodes

    src, tgt, val = [], [], []
    for i_b, b in enumerate(THREE_BINS):
        for i_a, a in enumerate(THREE_BINS):
            v = int(trans.loc[b, a])
            if v > 0:
                src.append(i_b)
                tgt.append(len(THREE_BINS) + i_a)  # 3 + i_a
                val.append(v)

    node_colors = (
        ['#F08080', '#C0C0C0', '#6495ED'] +
        ['#F08080', '#C0C0C0', '#6495ED']
    )

    fig = go.Figure(data=[go.Sankey(
        arrangement="fixed",
        node=dict(
            pad=10, thickness=10,
            line=dict(color="rgba(0,0,0,0)", width=0.1),
            label=labels, color=node_colors
        ),
        link=dict(source=src, target=tgt, value=val,
                  color="rgba(128,128,128,0.45)"))
    ])


    fig.update_layout(font=dict(size=18.5),
                      margin=dict(l=10, r=10, t=10, b=10),
    height = 400,
    width = 700

    )

    fig.write_image(str(out_dir / f"{out_name}.png"), scale=4)
    png_path = str(out_dir / f"{out_name}.png")
    try:
        pdf_path = str(out_dir / f"{out_name}.pdf")
        img = Image.open(png_path)

        if img.mode == 'RGBA':
            img = img.convert('RGB')
        img.save(pdf_path, "PDF", resolution=300, quality=100)
        print(f"PDF saved to {pdf_path}")
    except Exception as e:
        print(f"PDF export failed: {e}")

    print(f"3-bin Sankey saved to {out_dir / (out_name + '.png')}")


THREE_BINS_ORDERED = ['Agree', 'Neutral', 'Disagree']
# THREE_BINS_ORDERED = ['Disagree', 'Neutral', 'Agree']

def make_trust_sankey_3bin_ordered(p1: pd.DataFrame, p2: pd.DataFrame, out_dir: Path,
                           before_col_idx: int = 7, after_col_idx: int = 7,
                           out_name: str = "sankey_trust_3x3"):
    out_dir.mkdir(parents=True, exist_ok=True)
    # Map to 3 bins
    before = _to_three_bins(p1.iloc[:, before_col_idx]).reset_index(drop=True)
    after  = _to_three_bins(p2.iloc[:, after_col_idx]).reset_index(drop=True)
    df = pd.DataFrame({"before": before, "after": after}).dropna().reset_index(drop=True)
    # 3x3 transition matrix with fixed order
    trans = (pd.crosstab(df["before"], df["after"])
               .reindex(index=THREE_BINS, columns=THREE_BINS, fill_value=0))
    trans.to_csv(out_dir / f"{out_name}_transition.csv")

    # nodes & links
    before_nodes = [f"Before: {lab}" for lab in THREE_BINS]
    after_nodes  = [f"After: {lab}"  for lab in THREE_BINS]
    labels = before_nodes + after_nodes

    src, tgt, val = [], [], []
    for i_b, b in enumerate(THREE_BINS):
        for i_a, a in enumerate(THREE_BINS):
            v = int(trans.loc[b, a])
            if v > 0:
                src.append(i_b)
                tgt.append(len(THREE_BINS) + i_a)  # 3 + i_a
                val.append(v)

    node_colors = (
            ['#F08080', '#C0C0C0', '#6495ED'] +
            ['#F08080', '#C0C0C0', '#6495ED']
    )
    # node_colors = (
    #     ['#F08080', '#C0C0C0', '#6495ED'] +
    #     ['#F08080', '#C0C0C0', '#6495ED']
    # )
    y_positions = [0.15, 0.50, 0.85]
    x_positions = [0.01] * 3 + [0.99] * 3
    y_all = y_positions + y_positions

    fig = go.Figure(data=[go.Sankey(
        arrangement="snap",
        node=dict(
            pad=10, thickness=10,
            line=dict(color="rgba(0,0,0,0)", width=0.1),
            label=labels, color=node_colors,
            x=x_positions,
            y=y_all
        ),
        link=dict(source=src, target=tgt, value=val,
                  color="rgba(128,128,128,0.45)"))
    ])


    fig.update_layout(font=dict(size=18.5), margin=dict(l=10, r=10, t=10, b=100),
                      height=400,
                      width=700
                      )

    fig.write_image(str(out_dir / f"{out_name}.png"), scale=4)
    png_path = str(out_dir / f"{out_name}.png")
    try:
        pdf_path = str(out_dir / f"{out_name}.pdf")
        img = Image.open(png_path)

        if img.mode == 'RGBA':
            img = img.convert('RGB')
        img.save(pdf_path, "PDF", resolution=300, quality=100)
        print(f"PDF saved to {pdf_path}")
    except Exception as e:
        print(f"PDF export failed: {e}")


    print(f"3-bin Sankey saved to {out_dir / (out_name + '.png')}")



if __name__ == '__main__':
    # ---------------- paths & data ----------------
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    DATA_DIR = PROJECT_ROOT / "data"
    OUT_DIR = PROJECT_ROOT / "output"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    p1 = pd.read_excel(DATA_DIR / "P1-1-30.xlsx")
    p2 = pd.read_excel(DATA_DIR / "P2-1-30.xlsx")

    # likert order
    likert_scale = ['Strongly disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly agree']
    make_trust_sankey(p1, p2, OUT_DIR, before_col_idx=7, after_col_idx=7, out_name="sankey_trust_5x5")

    # Sankey per group:
    # g1_p1 = p1.iloc[1:16].reset_index(drop=True)
    # g1_p2 = p2.iloc[1:16].reset_index(drop=True)
    # g2_p1 = p1.iloc[16:31].reset_index(drop=True)
    # g2_p2 = p2.iloc[16:31].reset_index(drop=True)
    # Group 1: IDs 1–15
    g1_p1 = p1.iloc[0:15].reset_index(drop=True)
    g1_p2 = p2.iloc[0:15].reset_index(drop=True)
    # Group 2: IDs 16–30
    g2_p1 = p1.iloc[15:30].reset_index(drop=True)
    g2_p2 = p2.iloc[15:30].reset_index(drop=True)
    make_trust_sankey(g1_p1, g1_p2, OUT_DIR / "group1", before_col_idx=7, after_col_idx=7,
                      out_name="sankey_trust_5x5_group1")
    make_trust_sankey(g2_p1, g2_p2, OUT_DIR / "group2", before_col_idx=7, after_col_idx=7,
                      out_name="sankey_trust_5x5_group2")

    make_trust_sankey_3bin(p1, p2, OUT_DIR, before_col_idx=7, after_col_idx=7,
                           out_name="sankey_trust_3x3")

    make_trust_sankey_3bin(g1_p1, g1_p2, OUT_DIR / "group1",
                           before_col_idx=7, after_col_idx=7,
                           out_name="sankey_trust_3x3_group1")

    make_trust_sankey_3bin(g2_p1, g2_p2, OUT_DIR / "group2",
                           before_col_idx=7, after_col_idx=7,
                           out_name="sankey_trust_3x3_group2")

    make_trust_sankey_3bin_ordered(p1, p2, OUT_DIR, before_col_idx=7, after_col_idx=7,
                           out_name="sankey_trust_3x3_ordered")

    make_trust_sankey_3bin_ordered(g1_p1, g1_p2, OUT_DIR / "group1",
                           before_col_idx=7, after_col_idx=7,
                           out_name="sankey_trust_3x3_ordered_group1")

    make_trust_sankey_3bin_ordered(g2_p1, g2_p2, OUT_DIR / "group2",
                           before_col_idx=7, after_col_idx=7,
                           out_name="sankey_trust_3x3_ordered_group2")

