import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D


# Processing the detailed NOS table

def process_detailed_nos(df: pd.DataFrame) -> pd.DataFrame:
    required_columns = [
        "Author, Year",
        "Representativeness", "Non-exposed Selection", "Exposure Ascertainment", "Outcome Absent at Start",
        "Comparability (Age/Gender)", "Comparability (Other)",
        "Outcome Assessment", "Follow-up Length", "Follow-up Adequacy",
        "Total Score", "Overall RoB"
    ]

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Validate numeric values
    numeric_cols = required_columns[1:-2]  # all star columns
    for col in numeric_cols:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise ValueError(f"Column {col} must be numeric.")
        if df[col].min() < 0 or df[col].max() > 5:
            raise ValueError(f"Column {col} contains invalid star values (0-5 allowed).")

    df["Selection"] = df["Representativeness"] + df["Non-exposed Selection"] + df["Exposure Ascertainment"] + df["Outcome Absent at Start"]
    df["Comparability"] = df["Comparability (Age/Gender)"] + df["Comparability (Other)"]
    df["Outcome/Exposure"] = df["Outcome Assessment"] + df["Follow-up Length"] + df["Follow-up Adequacy"]

    df["ComputedTotal"] = df["Selection"] + df["Comparability"] + df["Outcome/Exposure"]
    mismatches = df[df["ComputedTotal"] != df["Total Score"]]
    if not mismatches.empty:
        print("⚠️ Warning: Total Score mismatches detected:")
        print(mismatches[["Author, Year", "Total Score", "ComputedTotal"]])

    return df


# Map stars to risk colors
def stars_to_rob(stars, domain):
    if domain == "Selection":
        return "Low" if stars >= 3 else "Moderate" if stars == 2 else "High"
    elif domain == "Comparability":
        return "Low" if stars == 2 else "Moderate" if stars == 1 else "High"
    elif domain == "Outcome/Exposure":
        return "Low" if stars == 3 else "Moderate" if stars == 2 else "High"
    return "High"

def map_color(stars, domain, colors):
    risk = stars_to_rob(stars, domain)
    return colors.get(risk, "grey")


# Professional combined plot

def professional_plot(df: pd.DataFrame, output_file: str, theme: str = "default"):
    #  Color Themes 
    theme_options = {
        "default": {"Low":"#06923E","Moderate":"#FFD93D","High":"#DC2525"},  # updated green
        "blue": {"Low":"#3a83b7","Moderate":"#bdcfe7","High":"#084582"},
        "gray": {"Low":"#7f7f7f","Moderate":"#b0b0b0","High":"#3b3b3b"}
    }

    if theme not in theme_options:
        raise ValueError(f"Theme {theme} not available. Choose from {list(theme_options.keys())}")
    colors = theme_options[theme]

    line_width = 1.5
    fig_height = max(6, 0.7*len(df) + 5)
    fig = plt.figure(figsize=(18, fig_height))
    gs = GridSpec(2, 1, height_ratios=[len(df)*0.7, 1.5], hspace=0.4)

    # Traffic-Light Plot
    ax0 = fig.add_subplot(gs[0])
    plot_df = df.melt(id_vars=["Author, Year"], 
                      value_vars=["Selection","Comparability","Outcome/Exposure"],
                      var_name="Domain", value_name="Stars")
    plot_df["Color"] = plot_df.apply(lambda x: map_color(x["Stars"], x["Domain"], colors), axis=1)

    unique_colors = plot_df["Color"].unique()
    palette = {color: color for color in unique_colors}

    sns.scatterplot(
        data=plot_df,
        x="Domain",
        y="Author, Year",
        hue="Color",
        palette=palette,
        s=350,
        marker="s",
        legend=False,
        ax=ax0
    )

    ax0.set_title("NOS Traffic-Light Plot", fontsize=18, fontweight="bold")
    ax0.set_xlabel("")
    ax0.set_ylabel("Study", fontsize=12, fontweight="bold")
    ax0.set_xticks([0,1,2])
    ax0.set_xticklabels(["Selection","Comparability","Outcome/Exposure"], fontsize=12, fontweight="bold")
    ax0.tick_params(axis='y', labelsize=11, width=line_width, color='black')
    ax0.grid(axis='x', linestyle='--', alpha=0.25, linewidth=line_width, color='black')
    for spine in ax0.spines.values():
        spine.set_linewidth(line_width)
        spine.set_color('black')

    # Weighted Horizontal Stacked Bar Plot 
    ax1 = fig.add_subplot(gs[1])
    ax1.set_position([0.12, ax1.get_position().y0, 0.75, ax1.get_position().height])

    stacked_df = pd.DataFrame()
    for domain in ["Selection","Comparability","Outcome/Exposure"]:
        temp = df[[domain]].copy()
        temp["Domain"] = domain
        temp["RoB"] = temp[domain].apply(lambda x: stars_to_rob(x, domain))
        stacked_df = pd.concat([stacked_df, temp[["Domain","RoB"]]], axis=0)

    counts = stacked_df.groupby(["Domain","RoB"]).size().unstack(fill_value=0)
    counts_percent = counts.div(counts.sum(axis=1), axis=0) * 100

    bottom = None
    for rob in ["High","Moderate","Low"]:
        if rob in counts_percent.columns:
            ax1.barh(counts_percent.index, counts_percent[rob], left=bottom, color=colors[rob], edgecolor='black', linewidth=line_width, label=rob)
            bottom = counts_percent[rob] if bottom is None else bottom + counts_percent[rob]

    for i, domain in enumerate(counts_percent.index):
        left = 0
        for rob in ["High","Moderate","Low"]:
            if rob in counts_percent.columns:
                width = counts_percent.loc[domain, rob]
                if width > 0:
                    ax1.text(left + width/2, i, f"{width:.0f}%", ha='center', va='center', color='black', fontsize=10, fontweight='bold')
                    left += width

    ax1.set_xlim(0,100)
    ax1.set_xlabel("Percentage of Studies (%)", fontsize=13, fontweight="bold")
    ax1.set_ylabel("NOS Domain", fontsize=13, fontweight="bold")
    ax1.set_title("Distribution of Risk-of-Bias Judgments by Domain", fontsize=18, fontweight="bold")
    ax1.tick_params(axis='y', labelsize=12, width=line_width, color='black')
    ax1.grid(axis='x', linestyle='--', alpha=0.25, linewidth=line_width, color='black')
    for spine in ax1.spines.values():
        spine.set_linewidth(line_width)
        spine.set_color('black')

    
    leg = ax1.legend(title="RoB", loc="center left", bbox_to_anchor=(1.2,0.5), fontsize=12, title_fontsize=14, edgecolor='black', facecolor='white', framealpha=1, frameon=True)
    leg.get_frame().set_linewidth(line_width)

    
    legend_elements = [
        Line2D([0],[0], marker='s', color='w', label='Low Risk', markerfacecolor=colors["Low"], markersize=20),
        Line2D([0],[0], marker='s', color='w', label='Moderate Risk', markerfacecolor=colors["Moderate"], markersize=20),
        Line2D([0],[0], marker='s', color='w', label='High Risk', markerfacecolor=colors["High"], markersize=20)
    ]
    leg_top = ax0.legend(handles=legend_elements, title="Domain Risk", bbox_to_anchor=(1.15, 1), loc='upper left', fontsize=14, title_fontsize=16, edgecolor='black', facecolor='white', framealpha=1, frameon=True)
    leg_top.get_frame().set_linewidth(line_width)

    plt.tight_layout()

    
    valid_ext = [".png", ".pdf", ".svg", ".eps"]
    ext = os.path.splitext(output_file)[1].lower()
    if ext not in valid_ext:
        raise ValueError(f"Unsupported file format: {ext}. Use one of {valid_ext}")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Professional combined plot saved to {output_file}")


# Helper: Read CSV or Excel
def read_input_file(file_path: str) -> pd.DataFrame:
    ext = os.path.splitext(file_path)[1].lower()
    if ext in [".csv"]:
        return pd.read_csv(file_path)
    elif ext in [".xls", ".xlsx"]:
        return pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}. Provide a CSV or Excel file.")

# Main
if __name__ == "__main__":
    if len(sys.argv) not in [3,4]:
        print("Usage: python3 nos_tlplot.py input_file output_file.(png|pdf|svg|eps) [theme]")
        sys.exit(1)

    input_file, output_file = sys.argv[1], sys.argv[2]
    theme = sys.argv[3] if len(sys.argv) == 4 else "default"

    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        sys.exit(1)

    df = read_input_file(input_file)
    df = process_detailed_nos(df)
    professional_plot(df, output_file, theme)
