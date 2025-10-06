import streamlit as st
import pandas as pd
from nos_tlplot import (
    process_detailed_nos, professional_plot, plot_domain_radar, 
    plot_theme_radar, plot_domain_heatmap, plot_dot_profile, 
    plot_score_table, plot_donut_domain_risk, plot_line_ordered_scores, 
    plot_lollipop_total, plot_pie_overall_rob, plot_stacked_area_risk
)
import tempfile
import os
import shutil
from io import BytesIO
import base64
import streamlit.components.v1 as components
import gc  # For garbage collection

st.set_page_config(
    page_title="NOS-TLPlot",
    layout="wide",
    page_icon="./assets/icon.png"  
)

# Hide menu & footer
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Hide Streamlit default sidebar
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {display: none;}
    button[title="Toggle sidebar"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); }
    h1, h2, h3 { color: #f5f6fa; font-weight: 700; }
    .main-content { margin-top: 2vh; }
    .citation-box { border-left: 5px solid #6dd5ed; background-color: #f1f2f6; padding: 1rem; margin: 1rem 0; color: #2d3436 !important; border-radius: 6px; }
    .centered-title { 
        text-align: center; 
        font-size: 3.2rem !important;
        font-weight: 800 !important; 
        margin-top: -80px; 
        margin-bottom: 10px; 
        color: #ffffff !important;
        letter-spacing: 1px;
    }
    .centered-subtitle { 
        text-align: center; 
        font-size: 1.4rem !important;
        font-weight: 400 !important; 
        margin-bottom: 30px; 
        color: #dcdde1 !important;
    }
    .quickstart { font-size: 1.2rem; line-height: 1.6; color: #f5f6fa; }
    .scrollable-table { overflow-x: auto; }
    .lowered-section { margin-top: 50px; }
    .custom-button {
        background: linear-gradient(135deg, #74ebd5, #ACB6E5) !important;
        color: #2c3e50 !important;
        font-weight: 600 !important;
        text-decoration: none !important;
        padding: 0.6rem 1.2rem !important;
        font-size: 1rem !important;
        border-radius: 10px !important;
        display: inline-block !important;
        margin: 0 !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        border: none !important;
        cursor: pointer !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    }
    .custom-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.35);
    }
    .citation-button {
        background: linear-gradient(135deg, #74ebd5, #ACB6E5) !important;
        color: #2c3e50 !important;
        font-weight: 600 !important;
        text-decoration: none !important;
        padding: 0.45rem 0.9rem !important;
        font-size: 0.75rem !important;
        border-radius: 10px !important;
        display: inline-block !important;
        margin: 0 !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        border: none !important;
        cursor: pointer !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    }
    .citation-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.35);
    }
    .top-padding-container { margin-top: 100px; }

    /* Navigation */
    .nav-container {
        position: absolute;
        top: -1rem;
        left: 0.5rem;
        display: flex;
        gap: 30px;
        padding: 0.3rem 0.5rem;
        background: rgba(255,255,255,0.05);
        z-index: 9999;
        border-radius: 8px;
        font-size: 1.2rem;
        font-weight: 500;
    }
    .nav-link {
        color: #74ebd5 !important;
        text-decoration: none !important;
        transition: color 0.3s !important;
    }
    .nav-link:hover {
        color: #ffffff !important;
    }
    
    /* Plot selection styling */
    .plot-selection-container {
        background-color: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
    }
    
    .plot-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 10px;
        margin-top: 15px;
    }
    
    .plot-checkbox {
        display: flex;
        align-items: center;
        padding: 8px;
        border-radius: 5px;
        background-color: rgba(255,255,255,0.05);
    }
    
    .plot-checkbox:hover {
        background-color: rgba(255,255,255,0.1);
    }
    
    .plot-checkbox label {
        margin-left: 8px;
        color: #f5f6fa;
        font-weight: 500;
    }
    
    /* Download buttons styling */
    .download-button-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 15px;
        margin-top: 20px;
    }
    
    .download-button-item {
        background-color: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    
    .download-button-item h4 {
        color: #f5f6fa;
        margin-top: 0;
        margin-bottom: 10px;
    }
    
    /* Plot container with download button */
    .plot-container {
        position: relative;
        margin-bottom: 2rem;
    }
    
    .plot-download-btn {
        position: absolute;
        bottom: 10px;
        right: 10px;
        background: linear-gradient(135deg, #74ebd5, #ACB6E5) !important;
        color: #2c3e50 !important;
        font-weight: 600 !important;
        padding: 0.4rem 0.8rem !important;
        font-size: 0.9rem !important;
        border-radius: 8px !important;
        border: none !important;
        cursor: pointer !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
        z-index: 10;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }
    
    .plot-download-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.35);
    }
    
    /* Format selector styling */
    .format-selector {
        margin-top: 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* Multiple download buttons styling */
    .download-buttons-container {
        position: absolute;
        bottom: 10px;
        right: 10px;
        display: flex;
        gap: 8px;
        z-index: 10;
    }
    
    .small-download-btn {
        background: linear-gradient(135deg, #74ebd5, #ACB6E5) !important;
        color: #2c3e50 !important;
        font-weight: 600 !important;
        padding: 0.3rem 0.6rem !important;
        font-size: 0.8rem !important;
        border-radius: 6px !important;
        border: none !important;
        cursor: pointer !important;
        box-shadow: 0 3px 10px rgba(0,0,0,0.2);
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }
    
    .small-download-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 12px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

def add_background_png(png_file):
    if os.path.exists(png_file):
        with open(png_file, "rb") as f:
            b64_img = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{b64_img}");
                background-size: cover;
                background-attachment: fixed;
                padding-top: 0px;
            }}
            </style>
        """, unsafe_allow_html=True)

add_background_png("./assets/background.png")

st.markdown('<div class="top-padding-container">', unsafe_allow_html=True)


gif_file = "assets/Chart.gif"
if os.path.exists(gif_file):
    with open(gif_file, "rb") as f:
        gif_b64 = base64.b64encode(f.read()).decode()
    gif_data_url = f"data:image/gif;base64,{gif_b64}"
    
    gif_html = f"""
    <div style="display: flex; justify-content: center; margin-bottom: 16px;">
        <img src="{gif_data_url}" style="width: 180px; height: 180px;">
    </div>
    """
    components.html(gif_html, height=180)

st.markdown('<div class="main-content">', unsafe_allow_html=True)
st.markdown('<h1 class="centered-title">NOS-TLPlot</h1>', unsafe_allow_html=True)
st.markdown('<p class="centered-subtitle">Risk-of-Bias Visualizations for Newcastle–Ottawa Scale (NOS) Studies.</p>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="lowered-section">', unsafe_allow_html=True)

# Quick Start
st.markdown('<div style="font-size: 1.5rem; font-weight: bold; margin-bottom: 10px; color: #f5f6fa;">🚀 Quick Start & Data Instructions</div>', unsafe_allow_html=True)
with st.expander("**Setting Up Your Data**", expanded=True):
    st.markdown('<div class="quickstart" style="margin-top:-1rem;">', unsafe_allow_html=True)
    st.write("""
  📈 **NOS-TLPlot** helps you visualize Newcastle–Ottawa Scale (NOS) assessments.
It generates:

*  **Traffic light plots** (domain-level judgements)
*  **Weighted bar plots** (summary distributions)
*  **Multiple specialized visualizations** (radar charts, heatmaps, etc.)

All figures are **publication-ready**.

---        

**Input Table Format:**
- First column → Study details (Author, Year)
- Domain columns → Each NOS domain
- Total Score → Sum of domain scores
- Overall RoB → Low / Moderate / High
    """)

    sample_csv_path = "sample.csv"
    if os.path.exists(sample_csv_path):
        st.markdown('<div class="scrollable-table">', unsafe_allow_html=True)
        st.dataframe(pd.read_csv(sample_csv_path), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Download buttons
    excel_file_path = "sample.xlsx"
    csv_file_path = "sample.csv"
    def file_to_b64(path):
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        return ""
    st.markdown(f"""
    <div style="display:flex; gap:10px; margin-bottom:10px;">
        <a download="sample.xlsx" href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{file_to_b64(excel_file_path)}" class="custom-button">Excel Template</a>
        <a download="sample.csv" href="data:text/csv;base64,{file_to_b64(csv_file_path)}" class="custom-button">CSV Template</a>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Upload
st.markdown("### 📂 Upload Your Data")
st.markdown('<p style="color: #f5f6fa; font-size: 1.1rem;">Upload a <b>CSV</b> or <b>Excel (.xlsx)</b> file.</p>', unsafe_allow_html=True)
theme = st.selectbox("Select Plot Theme", options=["traffic_light", "gray"])
uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv","xls","xlsx"])

if uploaded_file is not None:
    try:
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        df = pd.read_csv(uploaded_file) if ext==".csv" else pd.read_excel(uploaded_file)
        df = process_detailed_nos(df)
        st.success("✅ Data validated successfully!")
        
        # Force garbage collection to free memory
        gc.collect()
        
        # Create a temporary directory that will be cleaned up automatically
        with tempfile.TemporaryDirectory() as temp_dir:
            # Use a regular dictionary for plot files
            plot_files = {}
            
            # Generate professional plot
            output_files = {ext: os.path.join(temp_dir, f"NOS_TrafficLight{ext}") for ext in [".png",".pdf",".svg",".eps"]}
            for out_ext, path in output_files.items():
                professional_plot(df, path, theme=theme)
            plot_files["Professional Traffic-Light Plot"] = output_files
            gc.collect()  # Free memory after generating plots
            
            # Define plot functions
            plot_functions = [
                ("Radar Chart", plot_domain_radar, "radar"),
                ("Theme-based Radar Chart", plot_theme_radar, "theme_radar"),
                ("Domain Heatmap", plot_domain_heatmap, "heatmap"),
                ("Dot Profile Plot", plot_dot_profile, "dot_profile"),
                ("Score Table", plot_score_table, "table"),
                ("Donut Chart", plot_donut_domain_risk, "donut"),
                ("Line Plot of Domain Scores", plot_line_ordered_scores, "line_ordered"),
                ("Lollipop Chart", plot_lollipop_total, "lollipop"),
                ("Pie Chart", plot_pie_overall_rob, "pie"),
                ("Stacked Area Chart", plot_stacked_area_risk, "stacked_area")
            ]
            
            # Generate plots with memory optimization
            for name, func, base in plot_functions:
                format_files = {}
                for fmt in [".png", ".pdf", ".svg", ".eps"]:
                    output_path = os.path.join(temp_dir, f"NOS_{base}{fmt}")
                    func(df, output_path, theme=theme)
                    format_files[fmt] = output_path
                plot_files[name] = format_files
                gc.collect()  # Free memory after each plot
            
            st.markdown("### Visualization Preview")
            
            # Display only PNG previews to save memory
            tab1, tab2, tab3 = st.tabs(["Main Plot", "Radar Charts", "Other Visualizations"])
            
            with tab1:
                st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                st.image(output_files[".png"], use_container_width=True)
                st.caption("Professional Traffic-Light Bubble Chart")
                
                # Add download buttons for all formats
                st.markdown('<div class="download-buttons-container">', unsafe_allow_html=True)
                
                formats = [".png", ".pdf", ".svg", ".eps"]
                mime_types = {
                    ".png": "image/png",
                    ".pdf": "application/pdf",
                    ".svg": "image/svg+xml",
                    ".eps": "application/postscript"
                }
                
                for fmt in formats:
                    file_path = output_files[fmt]
                    with open(file_path, "rb") as f:
                        file_data = f.read()
                    
                    filename = f"NOS_TrafficLight{fmt}"
                    
                    st.download_button(
                        label=f"{fmt[1:].upper()}",
                        data=file_data,
                        file_name=filename,
                        mime=mime_types[fmt],
                        key=f"download_main_{fmt}",
                        help=f"Download this plot in {fmt[1:].upper()} format"
                    )
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with tab2:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                    st.image(plot_files["Radar Chart"][".png"], use_container_width=True)
                    st.caption("Domain Scores Radar Chart")
                    
                    # Add download buttons for all formats
                    st.markdown('<div class="download-buttons-container">', unsafe_allow_html=True)
                    
                    for fmt in formats:
                        file_path = plot_files["Radar Chart"][fmt]
                        with open(file_path, "rb") as f:
                            file_data = f.read()
                        
                        filename = f"NOS_Radar{fmt}"
                        
                        st.download_button(
                            label=f"{fmt[1:].upper()}",
                            data=file_data,
                            file_name=filename,
                            mime=mime_types[fmt],
                            key=f"download_radar_{fmt}",
                            help=f"Download this plot in {fmt[1:].upper()} format"
                        )
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                with col2:
                    st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                    st.image(plot_files["Theme-based Radar Chart"][".png"], use_container_width=True)
                    st.caption("Theme-based Domain Scores Radar Chart")
                    
                    # Add download buttons for all formats
                    st.markdown('<div class="download-buttons-container">', unsafe_allow_html=True)
                    
                    for fmt in formats:
                        file_path = plot_files["Theme-based Radar Chart"][fmt]
                        with open(file_path, "rb") as f:
                            file_data = f.read()
                        
                        filename = f"NOS_ThemeRadar{fmt}"
                        
                        st.download_button(
                            label=f"{fmt[1:].upper()}",
                            data=file_data,
                            file_name=filename,
                            mime=mime_types[fmt],
                            key=f"download_theme_radar_{fmt}",
                            help=f"Download this plot in {fmt[1:].upper()} format"
                        )
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            
            with tab3:
                cols = st.columns(3)
                plot_names = list(plot_files.keys())[2:]  
                
                for i, name in enumerate(plot_names):
                    with cols[i % 3]:
                        st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                        st.image(plot_files[name][".png"], use_container_width=True)
                        st.caption(name)
                        
                        # Add download buttons for all formats
                        st.markdown('<div class="download-buttons-container">', unsafe_allow_html=True)
                        
                        # Create filename based on plot name
                        clean_name = name.replace(' ', '_').replace('-', '_').replace(' ', '')
                        
                        for fmt in formats:
                            file_path = plot_files[name][fmt]
                            with open(file_path, "rb") as f:
                                file_data = f.read()
                            
                            filename = f"NOS_{clean_name}{fmt}"
                            
                            st.download_button(
                                label=f"{fmt[1:].upper()}",
                                data=file_data,
                                file_name=filename,
                                mime=mime_types[fmt],
                                key=f"download_{name}_{fmt}",
                                help=f"Download this plot in {fmt[1:].upper()} format"
                            )
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
            
            # Explicitly clear references and force garbage collection
            plot_files.clear()
            del plot_files
            del output_files
            gc.collect()
        
    except Exception as e:
        st.error(f"❌ Error: {e}")

# Citation 
st.markdown("---")
st.markdown("## 📖 Citation")

apa_citation = (
    "Sahu, V. (2025). NOS-TLPlot: Visualization Tool for Newcastle–Ottawa Scale in Meta-Analysis (v2.0.0). "
    "Zenodo. https://doi.org/10.5281/zenodo.17065214"
)

harvard_citation = (
    "Sahu, V., 2025. NOS-TLPlot: Visualization Tool for Newcastle–Ottawa Scale in Meta-Analysis (v2.0.0). "
    "Zenodo. Available at: https://doi.org/10.5281/zenodo.17065214"
)

mla_citation = (
    "Sahu, Vihaan. \"NOS-TLPlot: Visualization Tool for Newcastle–Ottawa Scale in Meta-Analysis (v2.0.0).\" "
    "2025, Zenodo, https://doi.org/10.5281/zenodo.17065214."
)

chicago_citation = (
    "Sahu, Vihaan. 2025. \"NOS-TLPlot: Visualization Tool for Newcastle–Ottawa Scale in Meta-Analysis (v2.0.0).\" "
    "Zenodo. https://doi.org/10.5281/zenodo.17065214."
)

ieee_citation = (
    "V. Sahu, \"NOS-TLPlot: Visualization Tool for Newcastle–Ottawa Scale in Meta-Analysis (v2.0.0),\" "
    "Zenodo, 2025. doi: 10.5281/zenodo.17065214."
)

vancouver_citation = (
    "Sahu V. NOS-TLPlot: Visualization Tool for Newcastle–Ottawa Scale in Meta-Analysis (v2.0.0). "
    "Zenodo. 2025. doi:10.5281/zenodo.17065214"
)

ris_data = """TY  - JOUR
AU  - Sahu, V
TI  - NOS-TLPlot: Visualization Tool for Newcastle–Ottawa Scale in Meta-Analysis (v2.0.0)
PY  - 2025
DO  - 10.5281/zenodo.17065214
ER  -"""

bib_data = """@misc{Sahu2025,
  author={Sahu, V.},
  title={NOS-TLPlot: Visualization Tool for Newcastle–Ottawa Scale in Meta-Analysis (v2.0.0)},
  year={2025},
  doi={10.5281/zenodo.17065214}
}"""

citation_style = st.selectbox("Select citation style", ["APA", "Harvard", "MLA", "Chicago", "IEEE", "Vancouver"])

if citation_style == "APA": 
    citation_text = apa_citation
elif citation_style == "Harvard": 
    citation_text = harvard_citation
elif citation_style == "MLA": 
    citation_text = mla_citation
elif citation_style == "Chicago": 
    citation_text = chicago_citation
elif citation_style == "IEEE": 
    citation_text = ieee_citation
elif citation_style == "Vancouver": 
    citation_text = vancouver_citation

st.markdown(f'<p style="margin:0; color:#f5f6fa; font-size:1.1rem;"><i>Please cite NOS-TLPlot if you use it in your study.</i></p>', unsafe_allow_html=True)
st.markdown(f'<div class="citation-box"><p style="margin:0;">{citation_text}</p></div>', unsafe_allow_html=True)

ris_data_encoded = base64.b64encode(ris_data.encode()).decode()
bib_data_encoded = base64.b64encode(bib_data.encode()).decode()

escaped_citation = citation_text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
components.html(f"""
    <button id="copyButton" style="background: linear-gradient(135deg, #74ebd5, #ACB6E5); color: #2c3e50; font-weight: 600; padding: 0.45rem 0.9rem; border-radius: 10px; border: none; cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.25); margin-top: 10px;">Copy Citation</button>
    <script>
        document.getElementById("copyButton").addEventListener("click", function() {{
            navigator.clipboard.writeText("{escaped_citation}").then(function() {{
                const button = document.getElementById("copyButton");
                const originalText = button.innerText;
                button.innerText = "Copied!";
                setTimeout(function() {{
                    button.innerText = originalText;
                }}, 2000);
            }}, function(err) {{
                console.error('Could not copy text: ', err);
            }});
        }});
    </script>
""", height=50)

st.markdown(f"""
<div style="display:flex; gap:10px; margin-top:10px; margin-bottom:10px;">
    <a download="NOS-TLPlot_citation.ris" href="data:application/x-research-info-systems;base64,{ris_data_encoded}" class="citation-button">RIS Format</a>
    <a download="NOS_TLPlot_citation.bib" href="data:application/x-bibtex;base64,{bib_data_encoded}" class="citation-button">BibTeX Format</a>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<style>
.footer-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #dcdde1;
    padding: 1rem;
    font-size: 1.05rem;
}
.footer-left { text-align:left; }
.footer-center { display:flex; gap:40px; justify-content:center; align-items:center; }
.footer-link { color:#74ebd5; text-decoration:none; transition:color 0.3s ease; }
.footer-link:hover { color:#ffffff; }
</style>

<div class="footer-container">
    <div class="footer-left">
        <div>© 2025 Vihaan Sahu</div>
        <div>Licensed under the Apache License, Version 2.0</div>
    </div>
    <div class="footer-center">
        <span>NOS-TLPlot</span>
        <span>Professional NOS Visualization Tool</span>
        <a href='https://github.com/aurumz-rgb/nos-tlplot' target='_blank' class='footer-link'>GitHub Repository</a>
    </div>
</div>
""", unsafe_allow_html=True)

# Close wrappers
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)