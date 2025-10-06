import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
import matplotlib.colors as mcolors
from matplotlib.patches import Patch, Rectangle, Circle
import numpy as np
from matplotlib.gridspec import GridSpec
import matplotlib as mpl
from matplotlib.patches import Rectangle
import matplotlib.patheffects as path_effects
from matplotlib.collections import LineCollection



THEME_OPTIONS = {
    "traffic_light": {"Low":"#2E7D32", "Moderate":"#F9A825", "High":"#C62828"},  
    "gray": {"Low":"#95A5A6", "Moderate":"#34495E", "High":"#1E2A37"},            
}

# global style 
plt.style.use('seaborn-v0_8-whitegrid')
mpl.rcParams['font.family'] = 'Arial'
mpl.rcParams['font.weight'] = 'bold'
mpl.rcParams['axes.labelweight'] = 'bold'
mpl.rcParams['axes.titleweight'] = 'bold'
mpl.rcParams['figure.titlesize'] = 16
mpl.rcParams['axes.titlesize'] = 14
mpl.rcParams['axes.labelsize'] = 12
mpl.rcParams['xtick.labelsize'] = 10
mpl.rcParams['ytick.labelsize'] = 10
mpl.rcParams['legend.fontsize'] = 10
mpl.rcParams['legend.title_fontsize'] = 11
mpl.rcParams['figure.dpi'] = 300
mpl.rcParams['savefig.dpi'] = 300
mpl.rcParams['savefig.bbox'] = 'tight'
mpl.rcParams['savefig.transparent'] = False

def get_theme_colors(theme):
    if theme not in THEME_OPTIONS:
        raise ValueError(f"Theme {theme} not available. Choose from {list(THEME_OPTIONS.keys())}")
    return THEME_OPTIONS[theme]

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

    numeric_cols = required_columns[1:-2]  
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

# Professional combined plot with enhanced bubble chart
def professional_plot(df: pd.DataFrame, output_file: str, theme: str = "traffic_light"):
    colors = get_theme_colors(theme)
    line_width = 1.5
    fig_height = max(5, 0.4*len(df) + 2.5)
    
    
    fig = plt.figure(figsize=(16, fig_height))
    gs = GridSpec(1, 1, left=0.08, right=0.75, top=0.95, bottom=0.08)

   
    ax = fig.add_subplot(gs[0])
    
    
    domains = ["Selection", "Comparability", "Outcome/Exposure"]
    max_scores = {"Selection": 4, "Comparability": 2, "Outcome/Exposure": 3}
    
    
    bubble_data = []
    for _, row in df.iterrows():
        for domain in domains:
            stars = row[domain]
            normalized_size = stars / max_scores[domain]  
            risk = stars_to_rob(stars, domain)
            bubble_data.append({
                "Author, Year": row["Author, Year"],
                "Domain": domain,
                "Stars": stars,
                "NormalizedSize": normalized_size,
                "Risk": risk,
                "Color": colors[risk]
            })
    
    bubble_df = pd.DataFrame(bubble_data)
    
   
    domain_positions = {"Selection": 0, "Comparability": 3, "Outcome/Exposure": 6}
    bubble_df["X"] = bubble_df["Domain"].map(domain_positions)
    
 
    studies = df["Author, Year"].unique()
    study_positions = {study: i for i, study in enumerate(studies)}
    bubble_df["Y"] = bubble_df["Author, Year"].map(study_positions)
    
 
    min_size, max_size = 400, 1200
    bubble_df["Size"] = min_size + (max_size - min_size) * bubble_df["NormalizedSize"]
    

    for _, row in bubble_df.iterrows():
        
        glow = Circle((row["X"], row["Y"]), radius=row["Size"]/2000, 
                     facecolor=row["Color"], alpha=0.4)
        ax.add_patch(glow)
        
       
        bubble = Circle((row["X"], row["Y"]), radius=row["Size"]/2000, 
                       facecolor=row["Color"], alpha=0.9, edgecolor='black', linewidth=1.5)
        ax.add_patch(bubble)
        
        
        ax.text(row["X"], row["Y"], str(row["Stars"]), ha='center', va='center', 
                color='white', fontsize=14, fontweight='bold',
                path_effects=[path_effects.withStroke(linewidth=2, foreground='black')])
    
    
    for study in studies:
        study_data = bubble_df[bubble_df["Author, Year"] == study].sort_values("X")
        x_vals = study_data["X"].values
        y_vals = study_data["Y"].values
        
        
        for i in range(len(x_vals) - 1):
            segment = [(x_vals[i], y_vals[i]), (x_vals[i+1], y_vals[i+1])]
            color = colors[stars_to_rob(study_data.iloc[i]["Stars"], study_data.iloc[i]["Domain"])]
            lc = LineCollection([segment], colors=[color], linewidth=3, alpha=0.7)
            ax.add_collection(lc)
    

    ax.set_title("NOS Risk Assessment Bubble Chart", fontsize=18, pad=20)
    ax.set_xlabel("")
    ax.set_ylabel("Study", fontsize=14)
    ax.set_xticks([0, 3, 6])
    ax.set_xticklabels(domains, fontsize=14)
    ax.set_yticks(range(len(studies)))
    ax.set_yticklabels(studies, fontsize=12)
    ax.set_xlim(-1, 7)
    ax.set_ylim(-0.5, len(studies) - 0.5)
    ax.grid(False)
    

    ax.set_aspect('equal', adjustable='box')
    

    for spine in ax.spines.values():
        spine.set_visible(False)
    
   
    ax.grid(axis='x', linestyle='--', alpha=0.3)
    
  
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Low Risk', 
                markerfacecolor=colors["Low"], markersize=14, markeredgewidth=1.2, markeredgecolor='black'),
        Line2D([0], [0], marker='o', color='w', label='Moderate Risk', 
                markerfacecolor=colors["Moderate"], markersize=14, markeredgewidth=1.2, markeredgecolor='black'),
        Line2D([0], [0], marker='o', color='w', label='High Risk', 
                markerfacecolor=colors["High"], markersize=14, markeredgewidth=1.2, markeredgecolor='black')
    ]
    leg = ax.legend(handles=legend_elements, title="Risk Level", bbox_to_anchor=(1.02, 1), 
                   loc='upper left', edgecolor='black', facecolor='white', framealpha=1)

   
    plt.subplots_adjust(left=0.08, right=0.75, top=0.95, bottom=0.08)

    valid_ext = [".png", ".pdf", ".svg", ".eps"]
    ext = os.path.splitext(output_file)[1].lower()
    if ext not in valid_ext:
        raise ValueError(f"Unsupported file format: {ext}. Use one of {valid_ext}")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Professional combined plot saved to {output_file}")

# Enhanced Radar Chart with publication quality styling
def plot_domain_radar(df: pd.DataFrame, output_file: str, theme: str = "traffic_light"):
    colors_map = get_theme_colors(theme)
    
   
    max_scores = {"Selection": 4, "Comparability": 2, "Outcome/Exposure": 3}
    domains = list(max_scores.keys())
    
   
    fig = plt.figure(figsize=(14, 10))  
    ax = fig.add_subplot(111, polar=True)
    
    
    angles = np.linspace(0, 2 * np.pi, len(domains), endpoint=False).tolist()
    angles += angles[:1] 
    
    
    cmap = plt.colormaps.get_cmap('tab20')
    study_colors = [cmap(i) for i in np.linspace(0, 1, len(df))]
    
    
    for idx, row in df.iterrows():
        values = [row[domain] / max_scores[domain] for domain in domains]
        values += values[:1] 
        
     
        ax.plot(angles, values, 'o-', linewidth=2.5, color=study_colors[idx], alpha=0.8, 
                markeredgecolor='black', markeredgewidth=0.8)
        ax.fill(angles, values, alpha=0.2, color=study_colors[idx])
    
    
    ax.set_xticks(angles[:-1])
    
    ax.set_xticklabels(["A", "B", "C"], fontsize=15)
    ax.set_title("Domain Scores Radar Chart by Study", size=19, pad=20)
    ax.set_ylim(0, 1)
    
    
    ax.tick_params(axis='y', labelsize=14)
    
   
    ax.grid(True, linestyle='-', alpha=0.7, linewidth=1.5)
    
   
    legend_elements = [Line2D([0], [0], color=colors_map[rob], lw=2.5, label=rob) for rob in ["Low", "Moderate", "High"]]
    risk_legend = ax.legend(handles=legend_elements, title="Overall Risk", loc='center left', bbox_to_anchor=(1.2, 0.5))
    
   
    study_legend_elements = [Line2D([0], [0], color=study_colors[i], lw=2, label=row['Author, Year']) 
                            for i, (_, row) in enumerate(df.iterrows())]
    study_legend = ax.legend(handles=study_legend_elements, title="Study", loc='lower center', 
                            bbox_to_anchor=(0.5, -0.2), ncol=min(3, len(df)), fontsize=14)
    

    domain_mapping = {"A": "Selection", "B": "Comparability", "C": "Outcome/Exposure"}
    
    
    legend_x = 0.98
    legend_y = 0.05
    
   
    rect = Rectangle((legend_x - 0.02, legend_y - 0.05), 0.25, 0.15, 
                     transform=ax.transAxes, facecolor='white', 
                     edgecolor='black', alpha=0.8, linewidth=1.2)
    ax.add_patch(rect)
    

    y_offset = 0.03
    for letter, domain in domain_mapping.items():

        ax.text(legend_x, legend_y + y_offset, letter, transform=ax.transAxes, 
                fontsize=15, color='red', verticalalignment='bottom', 
                horizontalalignment='left', fontweight='bold')
        

        ax.text(legend_x + 0.03, legend_y + y_offset, f": {domain}", transform=ax.transAxes, 
                fontsize=14, color='black', verticalalignment='bottom', 
                horizontalalignment='left')
        
        y_offset += 0.04
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Domain radar chart saved to {output_file}")


def plot_theme_radar(df: pd.DataFrame, output_file: str, theme: str = "traffic_light"):
    colors_map = get_theme_colors(theme)
    

    max_scores = {"Selection": 4, "Comparability": 2, "Outcome/Exposure": 3}
    domains = list(max_scores.keys())
    
 
    fig = plt.figure(figsize=(14, 10))  
    ax = fig.add_subplot(111, polar=True)
    
    
    angles = np.linspace(0, 2 * np.pi, len(domains), endpoint=False).tolist()
    angles += angles[:1]  
    

    for idx, row in df.iterrows():
        values = [row[domain] / max_scores[domain] for domain in domains]
        values += values[:1] 
        
       
        color = colors_map.get(row["Overall RoB"], "grey")
       
        ax.plot(angles, values, 'o-', linewidth=2.5, color=color, alpha=0.8, 
                markeredgecolor='black', markeredgewidth=0.8)
        ax.fill(angles, values, alpha=0.2, color=color)
    
    
    ax.set_xticks(angles[:-1])

    ax.set_xticklabels(["A", "B", "C"], fontsize=15)  
    ax.set_title("Theme-based Domain Scores Radar Chart", size=19, pad=20)  
    ax.set_ylim(0, 1)
    

    ax.tick_params(axis='y', labelsize=14)
    

    ax.grid(True, linestyle='-', alpha=0.7, linewidth=1.5)
    
    
    legend_elements = [Line2D([0], [0], color=colors_map[rob], lw=2.5, label=rob) for rob in ["Low", "Moderate", "High"]]
    risk_legend = ax.legend(handles=legend_elements, title="Overall Risk", loc='center left', bbox_to_anchor=(1.2, 0.5))
    
    for text in risk_legend.get_texts():
        text.set_fontsize(14)
    
    
    domain_mapping = {"A": "Selection", "B": "Comparability", "C": "Outcome/Exposure"}
    
   
    legend_x = 0.98
    legend_y = 0.05
    
   
    rect = Rectangle((legend_x - 0.02, legend_y - 0.05), 0.25, 0.15, 
                     transform=ax.transAxes, facecolor='white', 
                     edgecolor='black', alpha=0.8, linewidth=1.2)
    ax.add_patch(rect)
    

    y_offset = 0.03
    for letter, domain in domain_mapping.items():
     
        ax.text(legend_x, legend_y + y_offset, letter, transform=ax.transAxes, 
                fontsize=15, color='red', verticalalignment='bottom',  
                horizontalalignment='left', fontweight='bold')
        
       
        ax.text(legend_x + 0.03, legend_y + y_offset, f": {domain}", transform=ax.transAxes, 
                fontsize=14, color='black', verticalalignment='bottom',  
                horizontalalignment='left')
        
        y_offset += 0.04
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Theme-based radar chart saved to {output_file}")


def plot_domain_heatmap(df: pd.DataFrame, output_file: str, theme: str = "traffic_light"):
    colors_map = get_theme_colors(theme)
    
   
    heatmap_df = df[["Author, Year", "Selection", "Comparability", "Outcome/Exposure", "Overall RoB"]].set_index("Author, Year")
    risk_df = heatmap_df.copy()
    

    for domain in ["Selection", "Comparability", "Outcome/Exposure"]:
        risk_df[domain] = risk_df[domain].apply(lambda x: stars_to_rob(x, domain))

    risk_map = {"High":0, "Moderate":1, "Low":2}
    numeric_df = risk_df.map(lambda x: risk_map[x])

    cmap = mcolors.ListedColormap([colors_map["High"], colors_map["Moderate"], colors_map["Low"]])
    bounds = [-0.5, 0.5, 1.5, 2.5]
    norm = mcolors.BoundaryNorm(bounds, cmap.N)

    fig_height = max(5, 0.3 * len(df))
    fig, ax = plt.subplots(figsize=(8, fig_height))
    

    sns.heatmap(numeric_df, cmap=cmap, norm=norm, linewidths=1.2, linecolor='white', ax=ax, cbar=False)

    ax.set_yticklabels(heatmap_df.index, fontsize=6)
    

    ax.set_xticklabels(heatmap_df.columns, rotation=45, ha='right', fontsize=8)


    legend_elements = [Patch(facecolor=colors_map[rob], label=rob, edgecolor='black', linewidth=1.2) 
                      for rob in ["High", "Moderate", "Low"]]
    

    ax.legend(handles=legend_elements, title="Overall Risk", bbox_to_anchor=(1.2, 0.5), 
              loc='center left', fontsize=8, title_fontsize=9)


    ax.set_title("Risk of Bias by Domain and Study", fontsize=10, pad=12)

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Domain heatmap plot saved to {output_file}")


def plot_star_distribution(df: pd.DataFrame, output_file: str, theme: str = "traffic_light"):
    colors_map = get_theme_colors(theme)
    domains = ["Selection", "Comparability", "Outcome/Exposure"]
    

    plot_data = []
    for domain in domains:
        for stars in range(0, 6):
            count = (df[domain] == stars).sum()
            plot_data.append({"Domain": domain, "Stars": stars, "Count": count})
    
    plot_df = pd.DataFrame(plot_data)
    

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=plot_df, x="Stars", y="Count", hue="Domain", 
                palette={"Selection": colors_map["Low"], 
                         "Comparability": colors_map["Moderate"],
                         "Outcome/Exposure": colors_map["High"]},
                ax=ax, edgecolor='black', linewidth=1.2, alpha=0.9)
    
    ax.set_title("Distribution of Star Ratings by Domain", fontsize=16, pad=12)
    ax.set_xlabel("Star Rating", fontsize=12)
    ax.set_ylabel("Number of Studies", fontsize=12)
    ax.legend(title="Domain", edgecolor='black', facecolor='white', framealpha=1)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    

    risk_legend_elements = [Patch(facecolor=colors_map[rob], label=rob, edgecolor='black', linewidth=1.2) 
                            for rob in ["High", "Moderate", "Low"]]
    ax.legend(handles=risk_legend_elements, title="Overall Risk", bbox_to_anchor=(1.2, 0.5), loc='center left')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Star distribution plot saved to {output_file}")


def plot_box_scores(df: pd.DataFrame, output_file: str, theme: str = "traffic_light"):
    colors_map = get_theme_colors(theme)
    

    plot_df = df.melt(id_vars=["Author, Year", "Overall RoB"], 
                      value_vars=["Selection", "Comparability", "Outcome/Exposure"],
                      var_name="Domain", value_name="Score")
    

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.boxplot(data=plot_df, x="Domain", y="Score", 
                palette={"Selection": colors_map["Low"], 
                         "Comparability": colors_map["Moderate"],
                         "Outcome/Exposure": colors_map["High"]},
                ax=ax, linewidth=1.5, boxprops=dict(alpha=0.9))
    

    sns.stripplot(data=plot_df, x="Domain", y="Score", 
                  hue="Overall RoB", palette=colors_map,
                  alpha=0.7, jitter=True, ax=ax, size=5, dodge=True, 
                  linewidth=0.8, edgecolor='black')
    
    ax.set_title("Distribution of Domain Scores", fontsize=16, pad=12)
    ax.set_xlabel("Domain", fontsize=12)
    ax.set_ylabel("Score", fontsize=12)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    

    risk_legend_elements = [Patch(facecolor=colors_map[rob], label=rob, edgecolor='black', linewidth=1.2) 
                            for rob in ["High", "Moderate", "Low"]]
    ax.legend(handles=risk_legend_elements, title="Overall Risk", bbox_to_anchor=(1.2, 0.5), loc='center left')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Box plot saved to {output_file}")


def plot_dot_profile(df: pd.DataFrame, output_file: str, theme: str = "traffic_light"):
    colors_map = get_theme_colors(theme)
    domains = ["Selection", "Comparability", "Outcome/Exposure"]
    

    fig, ax = plt.subplots(figsize=(10, 6))
    

    for idx, row in df.iterrows():
        scores = [row[domain] for domain in domains]
        color = colors_map.get(row["Overall RoB"], "grey")
        

        ax.plot(domains, scores, 'o-', color=color, alpha=0.8, linewidth=2.0, 
                markersize=8, markeredgecolor='black', markeredgewidth=0.8)
    

    for domain in domains:
        max_score = 4 if domain == "Selection" else (2 if domain == "Comparability" else 3)
        ax.axhline(y=max_score, color='gray', linestyle='--', alpha=0.5, linewidth=1.0)
    
    ax.set_title("Domain Score Profiles by Study", fontsize=16, pad=12)
    ax.set_xlabel("Domain", fontsize=12)
    ax.set_ylabel("Score", fontsize=12)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
   
    legend_elements = [Line2D([0], [0], color=colors_map[rob], lw=2.5, label=rob) for rob in ["Low", "Moderate", "High"]]
    ax.legend(handles=legend_elements, title="Overall Risk", loc='center left', bbox_to_anchor=(1.2, 0.5))
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Dot profile plot saved to {output_file}")


def plot_score_table(df: pd.DataFrame, output_file: str, theme: str = "traffic_light"):
    colors_map = get_theme_colors(theme)
    

    table_df = df[["Author, Year", "Selection", "Comparability", "Outcome/Exposure", "Total Score", "Overall RoB"]].copy()
    table_df = table_df.sort_values("Overall RoB", ascending=False)
    

    fig, ax = plt.subplots(figsize=(10, 0.3 * len(table_df) + 1.2))
    ax.axis('off')
    

    table = ax.table(
        cellText=table_df.values,
        colLabels=table_df.columns,
        cellColours=[[colors_map.get(row["Overall RoB"], "white") for _ in range(len(table_df.columns))] 
                    for _, row in table_df.iterrows()],
        loc='center',
        cellLoc='center'
    )
    

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    

    for key, cell in table.get_celld().items():
        cell.set_text_props(weight='bold')
        cell.set_edgecolor('white')
    
    table.scale(1, 1.2)
    

    for (i, j), cell in table.get_celld().items():
        if i == 0:  
            cell.set_facecolor('#f0f0f0')
            cell.set_edgecolor('white')
            cell.set_linewidth(1.2)
        else:
            cell.set_edgecolor('white')
            cell.set_linewidth(1.2)
    

    ax.set_title("NOS Scores by Study", fontsize=16, pad=12)
    

    legend_elements = [Patch(facecolor=colors_map[rob], label=rob, edgecolor='black', linewidth=1.2) 
                      for rob in ["High", "Moderate", "Low"]]
    ax.legend(handles=legend_elements, title="Overall Risk", bbox_to_anchor=(1.2, 0.5), loc='center left')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Score table plot saved to {output_file}")


def plot_donut_domain_risk(df: pd.DataFrame, output_file: str, theme: str = "traffic_light"):
    colors_map = get_theme_colors(theme)
    

    domains = ["Selection", "Comparability", "Outcome/Exposure"]
    

    fig, axs = plt.subplots(1, 3, figsize=(12, 4))
    
    for i, domain in enumerate(domains):

        risk_counts = df[domain].apply(lambda x: stars_to_rob(x, domain)).value_counts()
        order = ["High", "Moderate", "Low"]
        risk_counts = risk_counts.reindex(order, fill_value=0)
        

        wedges, texts, autotexts = axs[i].pie(risk_counts, labels=risk_counts.index, autopct='%1.1f%%',
                                            colors=[colors_map[rob] for rob in risk_counts.index],
                                            startangle=90, wedgeprops={'linewidth': 1.2, 'edgecolor': 'black'})
        

        center_circle = plt.Circle((0,0), 0.70, fc='white', edgecolor='black', linewidth=1.2)
        axs[i].add_artist(center_circle)
        

        for j, autotext in enumerate(autotexts):
            autotext.set_color('black')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)

            autotext.set_position((autotext.get_position()[0] * 0.9, autotext.get_position()[1] * 0.9))
        
        for j, text in enumerate(texts):
            text.set_fontweight('bold')
            text.set_fontsize(10)

            text.set_position((text.get_position()[0] * 1.1, text.get_position()[1] * 1.1))
        
        axs[i].set_title(f"{domain} Domain", fontsize=12)
    

    fig.suptitle("Risk Distribution by Domain", fontsize=16, y=1.05, fontweight='bold')
    

    legend_elements = [Patch(facecolor=colors_map[rob], label=rob, edgecolor='black', linewidth=1.2) 
                      for rob in ["High", "Moderate", "Low"]]
    fig.legend(handles=legend_elements, loc='center right', bbox_to_anchor=(1.15, 0.5))
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Donut chart saved to {output_file}")

def plot_line_ordered_scores(df: pd.DataFrame, output_file: str, theme: str = "traffic_light"):
    
    domain_colors = {
        "Selection": "#1f77b4",  
        "Comparability": "#ff7f0e",  
        "Outcome/Exposure": "#2ca02c" 
    }

    df_sorted = df.sort_values("Total Score")
    

    plot_df = df_sorted.melt(id_vars=["Author, Year", "Overall RoB"], 
                            value_vars=["Selection", "Comparability", "Outcome/Exposure"],
                            var_name="Domain", value_name="Score")
    

    fig, ax = plt.subplots(figsize=(12, 6))
    
    
    for domain in ["Selection", "Comparability", "Outcome/Exposure"]:
        domain_data = plot_df[plot_df["Domain"] == domain]
        ax.plot(domain_data["Author, Year"], domain_data["Score"], 
               'o-', label=domain, linewidth=2.0, markersize=6, 
               markeredgecolor='black', markeredgewidth=0.8, color=domain_colors[domain])
    

    ax.set_title("Domain Scores Ordered by Total Score", fontsize=16, pad=12)
    ax.set_xlabel("Study (Ordered by Total Score)", fontsize=12)
    ax.set_ylabel("Score", fontsize=12)
    ax.grid(alpha=0.7)
    
   
    plt.xticks(rotation=45, ha='right')
    
   
    ax.legend(title="Domain", bbox_to_anchor=(1.05, 1), loc='upper left', 
             edgecolor='black', facecolor='white', framealpha=1)
    
    
    plt.tight_layout(rect=[0, 0, 0.85, 1])
    
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Line plot saved to {output_file}")


def plot_lollipop_total(df: pd.DataFrame, output_file: str, theme: str = "traffic_light"):
    colors_map = get_theme_colors(theme)
    

    df_sorted = df.sort_values("Total Score")
    

    fig, ax = plt.subplots(figsize=(8, 6))
    

    ax.hlines(y=df_sorted["Author, Year"], xmin=0, xmax=df_sorted["Total Score"], 
             colors=df_sorted["Overall RoB"].map(colors_map), alpha=0.8, linewidth=2.0)
    ax.scatter(df_sorted["Total Score"], df_sorted["Author, Year"], 
              color=df_sorted["Overall RoB"].map(colors_map), alpha=0.9, s=80, 
              edgecolor='black', linewidth=0.8)
    

    for idx, row in df_sorted.iterrows():
        ax.text(row["Total Score"] + 0.1, row["Author, Year"], str(row["Total Score"]), 
               va='center', fontsize=10, fontweight='bold')
    

    ax.set_title("Total NOS Scores by Study (Lollipop Chart)", fontsize=16, pad=12)
    ax.set_xlabel("Total Score", fontsize=12)
    ax.set_ylabel("Study", fontsize=12)
    ax.grid(axis='x', alpha=0.7)
    

    legend_elements = [Line2D([0], [0], color=colors_map[rob], lw=2.5, label=rob) for rob in ["Low", "Moderate", "High"]]
    ax.legend(handles=legend_elements, title="Overall Risk", loc='center left', bbox_to_anchor=(1.2, 0.5))
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Lollipop chart saved to {output_file}")


def plot_pie_overall_rob(df: pd.DataFrame, output_file: str, theme: str = "traffic_light"):
    colors_map = get_theme_colors(theme)
    

    counts = df["Overall RoB"].value_counts()
    order = ["High", "Moderate", "Low"]
    counts = counts.reindex(order, fill_value=0)
    

    fig, ax = plt.subplots(figsize=(8, 8))
    

    ax.set_position([0.1, 0.1, 0.65, 0.65])
    
    wedges, texts, autotexts = ax.pie(counts, labels=counts.index, autopct='%1.1f%%',
                                      colors=[colors_map[rob] for rob in counts.index],
                                      startangle=90, wedgeprops={'linewidth': 1.2, 'edgecolor': 'black'})
    

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(11)
    
    for text in texts:
        text.set_fontweight('bold')
        text.set_fontsize(11)
    
    ax.set_title("Distribution of Overall Risk of Bias", fontsize=16, pad=12)
    

    legend_elements = [Patch(facecolor=colors_map[rob], label=rob, edgecolor='black', linewidth=1.2) 
                      for rob in ["High", "Moderate", "Low"]]
    ax.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1.2, 0.5))
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Pie chart saved to {output_file}")


def plot_stacked_area_risk(df: pd.DataFrame, output_file: str, theme: str = "traffic_light"):
    colors_map = get_theme_colors(theme)
    

    domains = ["Selection", "Comparability", "Outcome/Exposure"]
    risk_categories = ["High", "Moderate", "Low"]
    

    counts = {}
    for domain in domains:
        risk_counts = df[domain].apply(lambda x: stars_to_rob(x, domain)).value_counts()
        counts[domain] = [risk_counts.get(cat, 0) for cat in risk_categories]
    

    plot_df = pd.DataFrame(counts, index=risk_categories)
    

    plot_df_percent = plot_df.div(plot_df.sum(axis=0), axis=1) * 100
    

    fig, ax = plt.subplots(figsize=(8, 6))
    

    ax.stackplot(domains, plot_df_percent.loc[risk_categories], 
                colors=[colors_map[cat] for cat in risk_categories],
                labels=risk_categories,
                alpha=0.8,
                edgecolor='black',
                linewidth=1.2)
    

    ax.set_title("Risk Distribution by Domain (Stacked Area Chart)", fontsize=16, pad=12)
    ax.set_xlabel("Domain", fontsize=12)
    ax.set_ylabel("Percentage of Studies (%)", fontsize=12)
    

    ax.legend(title="Overall Risk", loc='center left', bbox_to_anchor=(1.2, 0.5))
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Stacked area chart saved to {output_file}")


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
    theme = sys.argv[3] if len(sys.argv) == 4 else "traffic_light"

    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        sys.exit(1)

    df = read_input_file(input_file)
    df = process_detailed_nos(df)
    
   
    base, ext = os.path.splitext(output_file)
    
    # Generate all plots
    professional_plot(df, output_file, theme)
    plot_domain_radar(df, f"{base}_radar{ext}", theme)
    plot_theme_radar(df, f"{base}_theme_radar{ext}", theme)
    plot_domain_heatmap(df, f"{base}_heatmap{ext}", theme)
    plot_dot_profile(df, f"{base}_dot_profile{ext}", theme)
    plot_score_table(df, f"{base}_table{ext}", theme)
    plot_donut_domain_risk(df, f"{base}_donut{ext}", theme)
    plot_line_ordered_scores(df, f"{base}_line_ordered{ext}", theme)
    plot_lollipop_total(df, f"{base}_lollipop{ext}", theme)
    plot_pie_overall_rob(df, f"{base}_pie{ext}", theme)
    plot_stacked_area_risk(df, f"{base}_stacked_area{ext}", theme)