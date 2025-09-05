#!/bin/bash
# Start Streamlit in background
streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true &

# Start NGINX in foreground
nginx -g 'daemon off;'
