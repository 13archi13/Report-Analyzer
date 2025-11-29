import unittest
from unittest.mock import MagicMock, patch
import os
import sys
import json

# Add src to path
sys.path.append(os.getcwd())

from src.extractor import extract_data_from_file
from src.llm_client import analyze_and_curate
from src.analyzer import aggregate_and_analyze

class TestPipeline(unittest.TestCase):
    
    def test_full_flow(self):
        print("Testing full flow with mocked LLM...")
        
        # 1. Test Extraction
        filepath = "./data/input/dummy_report.docx"
        if not os.path.exists(filepath):
            self.fail("Dummy report not found. Run create_dummy_data.py first.")
            
        tables = extract_data_from_file(filepath)
        self.assertTrue(len(tables) > 0, "Should extract at least one table")
        print(f"Extracted {len(tables)} tables.")
        
        # 2. Test LLM Curation (Mocked)
        mock_response_json = {
            "filename": "dummy_report.docx",
            "chemicals": [
                {"name": "Methane", "properties": {"Boiling Point": -161.5, "Melting Point": -182}},
                {"name": "Ethane", "properties": {"Boiling Point": -89, "Melting Point": -183}},
                {"name": "Propane", "properties": {"Boiling Point": -42, "Melting Point": -188}},
                {"name": "Butane", "properties": {"Boiling Point": -0.5, "Melting Point": -138}},
                {"name": "Pentane", "properties": {"Boiling Point": 36.1, "Melting Point": -130}}
            ],
            "summary": "Mocked summary of alkanes."
        }
        
        with patch('src.llm_client.genai') as mock_genai:
            # Mock the model and generate_content
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            
            mock_content = MagicMock()
            mock_content.text = json.dumps(mock_response_json)
            mock_model.generate_content.return_value = mock_content
            
            # We also need to mock os.getenv to return a fake key so configure_llm doesn't fail
            with patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"}):
                curated_data = analyze_and_curate(tables, "dummy_report.docx")
                
        self.assertEqual(curated_data['filename'], "dummy_report.docx")
        self.assertEqual(len(curated_data['chemicals']), 5)
        print("LLM curation (mocked) successful.")
        
        # 3. Test Analysis
        report = aggregate_and_analyze([curated_data])
        print("Analysis Report Generated:")
        print(report)
        
        self.assertIn("AGGREGATED DATA SUMMARY", report)
        self.assertIn("Methane", report)
        self.assertIn("Statistics for Boiling Point", report)

if __name__ == '__main__':
    unittest.main()
