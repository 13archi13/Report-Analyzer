import streamlit as st
import os
import tempfile
import pandas as pd
from dotenv import load_dotenv
from src.extractor import extract_data_from_file
from src.llm_client import analyze_and_curate
from src.analyzer import aggregate_and_analyze

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Technical Report Analyzer", layout="wide")

st.title("Technical Report Analyzer")
st.markdown("""
Upload technical reports (PDF or DOCX) to extract chemical data and analyze trends.
""")

# check for API key
if not os.getenv("GEMINI_API_KEY"):
    st.error("GEMINI_API_KEY not found in environment variables. Please check your .env file.")
    st.stop()

uploaded_files = st.file_uploader("Upload Reports", type=['pdf', 'docx'], accept_multiple_files=True)

if uploaded_files:
    if st.button("Analyze Reports"):
        
        extracted_data = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Processing {uploaded_file.name}...")
            
            # Save uploaded file to a temporary file
            suffix = os.path.splitext(uploaded_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            try:
                # 1. Extraction
                raw_tables = extract_data_from_file(tmp_path)
                
                if raw_tables:
                    # 2. LLM Curation
                    curated_info = analyze_and_curate(raw_tables, uploaded_file.name)
                    extracted_data.append(curated_info)
                else:
                    st.warning(f"No tables found in {uploaded_file.name}")
                    
            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {e}")
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            
            progress_bar.progress((i + 1) / len(uploaded_files))
            
        status_text.text("Analysis Complete!")
        
        if extracted_data:
            st.divider()
            st.header("Extracted Data")
            
            # Display individual file results
            for item in extracted_data:
                with st.expander(f"Results for {item['filename']}"):
                    st.json(item)
            
            st.divider()
            st.header("Trend Analysis")
            
            # 3. Trend Analysis
            # We need to capture the printed output of aggregate_and_analyze or modify it to return structured data
            # For now, let's just display the text report
            analysis_report = aggregate_and_analyze(extracted_data)
            st.text(analysis_report)
            
        else:
            st.info("No data extracted from the uploaded files.")
