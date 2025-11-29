import argparse
import os
import sys
from dotenv import load_dotenv
from src.extractor import extract_data_from_file
from src.llm_client import analyze_and_curate
from src.analyzer import aggregate_and_analyze
from tabulate import tabulate

# Load environment variables
load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Technical Report Analyzer")
    parser.add_argument("--input", default="./data/input", help="Directory containing input PDF/DOCX files")
    parser.add_argument("--output", default="./data/output", help="Directory to save output results")
    args = parser.parse_args()

    input_dir = args.input
    output_dir = args.output

    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Scanning '{input_dir}' for technical reports...")
    
    extracted_data = []
    
    for filename in os.listdir(input_dir):
        filepath = os.path.join(input_dir, filename)
        if filename.lower().endswith(('.pdf', '.docx')):
            print(f"Processing: {filename}")
            try:
                # 1. Extraction
                raw_tables = extract_data_from_file(filepath)
                
                if not raw_tables:
                    print(f"  - No tables found in {filename}")
                    continue
                
                # 2. LLM Curation & Summarization
                curated_info = analyze_and_curate(raw_tables, filename)
                extracted_data.append(curated_info)
                print(f"  - Successfully analyzed {filename}")
                
            except Exception as e:
                print(f"  - Failed to process {filename}: {e}")

    if not extracted_data:
        print("No data extracted from any files.")
        return

    # 3. Trend Analysis
    print("\nPerforming trend analysis...")
    analysis_report = aggregate_and_analyze(extracted_data)
    
    # Output results
    print("\n" + "="*40)
    print("ANALYSIS REPORT")
    print("="*40)
    print(analysis_report)
    
    # Save to file
    output_file = os.path.join(output_dir, "analysis_report.txt")
    with open(output_file, "w") as f:
        f.write(analysis_report)
    print(f"\nReport saved to: {output_file}")

if __name__ == "__main__":
    main()
