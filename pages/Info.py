import streamlit as st
import os
import base64

st.set_page_config(page_title="NOS-TLPlot / Info", page_icon="./assets/icon.png", layout="wide")


hide_streamlit_style = """
    <style>
    /* Hide hamburger menu */
    #MainMenu {visibility: hidden;}
    /* Hide footer */
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# Hide Streamlit menu and sidebar
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        display: none;
    }
    button[title="Toggle sidebar"] {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Hero navigation bar
active_page = "Info"

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
    <a href="/Info" target="_self" style="color: {'#3498db' if active_page=='Info' else '#ffffff'}; text-decoration:none; transition: color 0.3s;" class="nav-link{' active' if active_page=='Info' else ''}">Info</a>
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


# Background function
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


# Page Content
st.markdown('<div style="margin-top: 120px; text-align:center;">', unsafe_allow_html=True)
st.markdown('<h1 style="font-size:3rem; font-weight:800; color:#ffffff;">NOS-TLPlot — Information & Support</h1>', unsafe_allow_html=True)


# General Information Section 
st.markdown("""
## General Information

**NOS-TLPlot** is a reproducible, professional web application for visualizing Newcastle–Ottawa Scale (NOS) risk-of-bias assessments.

It allows researchers to generate:

- Traffic light plots showing study-level judgements for each NOS domain.
- Weighted bar plots summarizing distribution of judgements across domains.

This tool is built on **Python** and complements evidence synthesis workflows. It is designed for reproducibility, enabling users to consistently visualize NOS assessments for their datasets.

**NOS-TLPlot**, like **robvis**, is inspired by the **Evidence Synthesis Hackathon philosophy**: creating open, reproducible, and publication-ready visualizations. The underlying methodology ensures that your results can be shared and reproduced with minimal effort.
""", unsafe_allow_html=True)

# Example image from folder
if os.path.exists("./example/result.png"):
    st.markdown('<div style="text-align:center; margin-top:20px;">', unsafe_allow_html=True)
    st.image("./example/result.png", caption="Example NOS-TLPlot Result", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# Support Section
st.markdown("---")
st.markdown("""
## Support & Contact

If you encounter any issues or need support, you can:

- Open a GitHub Issue: [GitHub](https://github.com/aurumz-rgb/nos-tlplot)
- Send me an email: [Mail](mailto:pteroisvolitans12@gmail.com)

Feel free to reach out via either method.
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="display:flex; justify-content:space-between; align-items:center; color:#fff; padding:1rem; font-size:1.05rem;">
    <div>
        <div>© 2025 Vihaan Sahu</div>
        <div>Licensed under the Apache License, Version 2.0</div>
    </div>
    <div style="display:flex; gap:40px; justify-content:center; align-items:center;">
        <span>NOS-TLPlot</span>
        <span>Professional NOS Visualization Tool</span>
        <a href='https://github.com/aurumz-rgb/nos-tlplot' target='_blank' style='color:#3498db; text-decoration:none;'>GitHub Repository</a>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
