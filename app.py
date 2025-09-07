import streamlit as st
import pandas as pd
from nos_tlplot import process_detailed_nos, professional_plot
import tempfile
import os
import shutil
from io import BytesIO
import base64
import streamlit.components.v1 as components




# Google verification meta tag
st.markdown("""
<meta name="google-site-verification" content="fz5FTsNecP2shM5Y9vcPOT48lMJveVHYQ8_DjlrOwTg" />
""", unsafe_allow_html=True)




st.set_page_config(
    page_title="NOS-TLPlot / Home",
    layout="wide",
    page_icon="./assets/icon.png"  
)



hide_streamlit_style = """
    <style>
    /* Hide hamburger menu */
    #MainMenu {visibility: hidden;}
    /* Hide footer */
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)



# Hide Streamlit default menu and sidebar

st.markdown(
    """
    <style>
    /* Hide Streamlit default sidebar */
    [data-testid="stSidebar"] {
        display: none;
    }
    /* Hide hamburger menu that toggles sidebar */
    button[title="Toggle sidebar"] {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)



# Custom CSS 
st.markdown("""
<style>
    .stApp { background-color: #111111; }
    h1, h2, h3 { color: #2c3e50; font-weight: 600; }
    .main-content { margin-top: 2vh; }
    .citation-box { border-left: 4px solid #3498db; background-color: #e9ecef; padding: 1rem; margin: 1rem 0; color: #000 !important; }
    .centered-title { 
        text-align: center; 
        font-size: 3.5rem !important;
        font-weight: 800 !important; 
        margin-top: -40px; 
        margin-bottom: 10px; 
        color: #ffffff !important;
    }
    .centered-subtitle { 
        text-align: center; 
        font-size: 1.5rem !important;
        font-weight: 500 !important; 
        margin-bottom: 30px; 
        color: #ffffff !important;
    }
    .quickstart { font-size: 1.4rem; line-height: 1.6; }
    .scrollable-table { overflow-x: auto; }
    .lowered-section { margin-top: 30px; }
    .custom-button {
        background-color: #3498db !important;
        color: white !important;
        text-decoration: none !important;
        padding: 0.5rem 1rem !important;
        font-size: 1rem !important;
        border-radius: 5px !important;
        display: inline-block !important;
        margin: 0 !important;
        transition: background-color 0.3s ease !important;
        border: none !important;
        cursor: pointer !important;
    }
    .custom-button:hover {
        background-color: #2980b9 !important;
    }
    .top-padding-container { margin-top: 100px; }
</style>
""", unsafe_allow_html=True)


# Hero navigation bar
active_page = "Home"

st.markdown(f"""
<div style="
    position: absolute;
    top: -1rem;
    left: 0.1rem;
    display: flex;
    gap: 30px;
    padding: 0.1rem 0.1rem;
    background-color: rgba(0,0,0,0);
    z-index: 9999;
    border-radius: 5px;
    font-size: 1.4rem;
    font-weight: 400;
">
    <a href="/" target="_self" style="color: {'#3498db' if active_page=='Home' else '#ffffff'}; text-decoration:none; transition: color 0.3s;" class="nav-link{' active' if active_page=='Home' else ''}">Home</a>
    <a href="/Info"  target="_self" style="color: {'#3498db' if active_page=='Info' else '#ffffff'}; text-decoration:none; transition: color 0.3s;" class="nav-link{' active' if active_page=='Info' else ''}">Info</a>
</div>

<style>
div[style*='position: absolute'] a.nav-link {{
    color: #ffffff !important;
}}
div[style*='position: absolute'] a.nav-link:hover:not(.active) {{
    color:#aaaaaa !important;
}}
div[style*='position: absolute'] a.nav-link.active {{
    color: #3498db !important;
}}
</style>
""", unsafe_allow_html=True)


# Background & logo
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

def display_logo_png_top_touch(png_file, height=180):
    if os.path.exists(png_file):
        with open(png_file, "rb") as f:
            b64_img = base64.b64encode(f.read()).decode()
        st.markdown(f'''
            <div style="text-align:center; margin-top:0px; padding-top:0px;">
                <img src="data:image/png;base64,{b64_img}" height="{height}px" style="display:block; margin:0 auto; padding:0;">
            </div>
        ''', unsafe_allow_html=True)

add_background_png("./assets/background.png")


# Content wrapper
st.markdown('<div class="top-padding-container">', unsafe_allow_html=True)
display_logo_png_top_touch("./assets/logo.png", height=180)
st.markdown('<div class="main-content">', unsafe_allow_html=True)
st.markdown('<h1 class="centered-title">NOS-TLPlot</h1>', unsafe_allow_html=True)
st.markdown('<p class="centered-subtitle">A Traffic light Plot Visualiser for NOS.</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="lowered-section">', unsafe_allow_html=True)


# Quick Start / Data Instructions
st.markdown('<div style="font-size: 1.6rem; font-weight: bold; margin-bottom: 10px;"> Quick Start & Data Instructions</div>', unsafe_allow_html=True)
with st.expander("**Setting Up Your Data**", expanded=True):
    st.markdown('<div class="quickstart" style="margin-top:-1rem;">', unsafe_allow_html=True)
    st.write("""
✨  **NOS-TLPlot** is a web app for visualizing Newcastle–Ottawa Scale (NOS) risk-of-bias assessments.
It generates:

* **Traffic light plots** showing domain-level judgements for each study.
* **Weighted bar plots** summarizing the distribution of judgements across domains.

All figures are **publication-ready** and formatted to match NOS assessment standards.

---        
             
To work correctly with **NOS-TLPlot**, your uploaded table should follow this structure:
    
- **First column:** Study details (Author, Year)
    - **Domain columns:** Each additional column corresponds to a specific NOS domain:
        - Representativeness
        - Non-exposed Selection
        - Exposure Ascertainment
        - Outcome Absent at Start
        - Comparability (Age/Gender)
        - Comparability (Other)
        - Outcome Assessment
        - Follow-up Length
        - Follow-up Adequacy
    - **Total Score:** Sum of the domain scores
    - **Overall RoB:** Overall risk-of-bias judgement for each study (Low, Moderate, High)
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
        <a download="sample.xlsx" href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{file_to_b64(excel_file_path)}" class="custom-button">
            Excel Template
        </a>
        <a download="sample.csv" href="data:text/csv;base64,{file_to_b64(csv_file_path)}" class="custom-button">
            CSV Template
        </a>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# Upload & process
st.markdown("### Upload Your Data")
st.markdown('<p style="color: #ffff; font-size: 1.1rem;">Please upload your file in <b>CSV</b> or <b>Excel (.xlsx)</b> format.</p>', unsafe_allow_html=True)
theme = st.selectbox("Select Plot Theme", options=["default", "blue", "gray"])
uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv","xls","xlsx"])

if uploaded_file is not None:
    try:
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        df = pd.read_csv(uploaded_file) if ext==".csv" else pd.read_excel(uploaded_file)
        df = process_detailed_nos(df)
        st.success(" Data validated successfully!")

        temp_dir = tempfile.mkdtemp()
        output_files = {ext: os.path.join(temp_dir, f"NOS_TrafficLight{ext}") for ext in [".png",".pdf",".svg",".eps"]}
        for out_ext, path in output_files.items():
            professional_plot(df, path, theme=theme)

        st.markdown("### Visualization Preview")
        st.image(output_files[".png"], use_container_width=True)

        # Download buttons
        st.markdown("###  Download Visualization")

        st.markdown('<p style="color: #ffff; font-size: 1.1rem;">Download your NOS-TLPlot visualisation in formats like:</p>', unsafe_allow_html=True)

        download_html = '<div style="display:flex; gap:10px; margin-bottom:10px;">'
        for out_ext, path in output_files.items():
            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            mime = {".png":"image/png",".pdf":"application/pdf",".svg":"image/svg+xml",".eps":"application/postscript"}[out_ext]
            download_html += f'<a download="NOS_TrafficLight{out_ext}" href="data:{mime};base64,{b64}" class="custom-button">{out_ext[1:].upper()}</a>'
        download_html += "</div>"
        st.markdown(download_html, unsafe_allow_html=True)
        shutil.rmtree(temp_dir)
    except Exception as e:
        st.error(f"❌ Error: {e}")

# --- Citation Section ---
st.markdown("---")
st.markdown("## Citation")

# Predefined citation formats
apa_citation = (
    "Sahu, V. (2025). NOS-TLPlot: Visualization Tool for Newcastle–Ottawa Scale in Meta-Analysis (v1.0.0). "
    "Zenodo. https://doi.org/10.5281/zenodo.17065215"
)

harvard_citation = (
    "Sahu, V., 2025. NOS-TLPlot: Visualization Tool for Newcastle–Ottawa Scale in Meta-Analysis (v1.0.0). "
    "Zenodo. Available at: https://doi.org/10.5281/zenodo.17065215"
)

mla_citation = (
    "Sahu, Vihaan. \"NOS-TLPlot: Visualization Tool for Newcastle–Ottawa Scale in Meta-Analysis (v1.0.0).\" "
    "2025, Zenodo, https://doi.org/10.5281/zenodo.17065215."
)

chicago_citation = (
    "Sahu, Vihaan. 2025. \"NOS-TLPlot: Visualization Tool for Newcastle–Ottawa Scale in Meta-Analysis (v1.0.0).\" "
    "Zenodo. https://doi.org/10.5281/zenodo.17065215."
)

ieee_citation = (
    "V. Sahu, \"NOS-TLPlot: Visualization Tool for Newcastle–Ottawa Scale in Meta-Analysis (v1.0.0),\" "
    "Zenodo, 2025. doi: 10.5281/zenodo.17065215."
)

vancouver_citation = (
    "Sahu V. NOS-TLPlot: Visualization Tool for Newcastle–Ottawa Scale in Meta-Analysis (v1.0.0). "
    "Zenodo. 2025. doi:10.5281/zenodo.17065215"
)

ris_data = """TY  - JOUR
AU  - Sahu, V
TI  - NOS-TLPlot: Visualization Tool for Newcastle–Ottawa Scale in Meta-Analysis (v1.0.0)
PY  - 2025
DO  - 10.5281/zenodo.17065215
ER  -"""

bib_data = """@misc{Sahu2025,
  author={Sahu, V.},
  title={NOS-TLPlot: Visualization Tool for Newcastle–Ottawa Scale in Meta-Analysis (v1.0.0)},
  year={2025},
  doi={10.5281/zenodo.17065215}
}"""

# Dropdown to select style
citation_style = st.selectbox(
    "Select citation style",
    ["APA", "Harvard", "MLA", "Chicago", "IEEE", "Vancouver"]
)

# Match style to text
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




st.markdown(f'<p style="margin:0; color:#ffff; font-size:1.1rem;"><i>If you use NOS-TLPlot to create risk-of-bias plots for your study, please remember to cite the tool.</i></p>', unsafe_allow_html=True)
st.markdown(f'<div class="citation-box"><p style="margin:0; color: #000;">{citation_text}</p></div>', unsafe_allow_html=True)

copy_button_html = f"""
<style>
.custom-button {{
    background-color: #3498db !important;
    color: white !important;
    text-decoration: none !important;
    padding: 0.5rem 1rem !important;
    font-size: 1rem !important;
    border-radius: 5px !important;
    display: inline-block !important;
    margin: 0 !important;
    transition: background-color 0.3s ease !important;
    border: none !important;
    cursor: pointer !important;
}}
.custom-button:hover {{
    background-color: #2980b9 !important;
}}
</style>

<div style="display:flex; gap:10px; margin-top:10px; margin-bottom:10px; position:relative;" id="button-container">
    <a id="copy-btn" class="custom-button">Copy Citation</a>
    <a download="NOS-TLPlot_citation.ris" href="data:application/x-research-info-systems;base64,{base64.b64encode(ris_data.encode()).decode()}" class="custom-button">RIS Format</a>
    <a download="NOS-TLPlot_citation.bib" href="data:application/x-bibtex;base64,{base64.b64encode(bib_data.encode()).decode()}" class="custom-button">BibTeX Format</a>
</div>

<script>
document.getElementById("copy-btn").onclick = function() {{
    const text = `{citation_text}`;
    const btn = document.getElementById("copy-btn");
    navigator.clipboard.writeText(text).then(() => {{
        const originalText = btn.innerText;
        btn.innerText = "Copied!";
        setTimeout(() => {{ btn.innerText = originalText; }}, 2000);
    }});
}};
</script>
"""
components.html(copy_button_html, height=100)

# Footer
st.markdown("---")
st.markdown("""
<style>
.footer-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #fff;
    padding: 1rem;
    font-size: 1.05rem;
}
.footer-left { text-align:left; }
.footer-center { display:flex; gap:40px; justify-content:center; align-items:center; }
.footer-link { color:#3498db; text-decoration:none; transition:color 0.3s ease; }
.footer-link:hover { color:#5682B1; }
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


