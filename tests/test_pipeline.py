import unittest
import os
import pandas as pd
from ingestion.csv_processor import load_and_preprocess_csv
from graph.graph_builder import CharacteristicGraph
from ai.stylometry import StylometryAnalyzer
from scoring.confidence import ConfidenceScorer
from reports.exporter import ReportExporter

class TestTracenetPipeline(unittest.TestCase):
    """
    Automated Integration Test Suite for TRACENET.
    Tests CSV ingestion, NetworkX graph construction, AI stylometry similarity, score calculation, and report export.
    """
    
    @classmethod
    def setUpClass(cls):
        cls.sample_csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_data.csv")

    def test_01_csv_ingestion(self):
        self.assertTrue(os.path.exists(self.sample_csv_path), "Sample CSV file does not exist!")
        df, stats = load_and_preprocess_csv(self.sample_csv_path)
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(stats["records_processed"], 0)
        self.assertGreater(stats["unique_usernames"], 1)
        self.assertIn("cleaned_text", df.columns)
        print(f"\n[PASS] CSV Ingestion Stats: {stats}")

    def test_02_characteristic_graph(self):
        df, _ = load_and_preprocess_csv(self.sample_csv_path)
        cgraph = CharacteristicGraph()
        cgraph.build_graph(df)
        
        self.assertGreater(len(cgraph.nx_graph.nodes), 0)
        profile = cgraph.get_username_profile("ShadowX", df)
        self.assertEqual(profile["username"], "ShadowX")
        self.assertIn("PGP_KEY_001", profile["pgp_keys"])
        self.assertIn("WALLET_BTC_001", profile["wallets"])
        self.assertIn("DarkWolf", profile["related_usernames"])
        print("\n[PASS] Characteristic Graph profile query for ShadowX verified!")

    def test_03_ai_stylometry_matrix(self):
        df, _ = load_and_preprocess_csv(self.sample_csv_path)
        stylometer = StylometryAnalyzer()
        sim_matrix, meta = stylometer.analyze_usernames(df)
        
        self.assertIn("engine", meta)
        shadow_dark = sim_matrix.get(("ShadowX", "DarkWolf"))
        self.assertIsNotNone(shadow_dark)
        self.assertGreaterEqual(shadow_dark, 0.70, f"Expected high writing similarity between ShadowX and DarkWolf, got {shadow_dark}")
        print(f"\n[PASS] Stylometry Engine ({meta['engine']}): ShadowX <-> DarkWolf Similarity = {shadow_dark}")

    def test_04_confidence_scoring(self):
        df, _ = load_and_preprocess_csv(self.sample_csv_path)
        stylometer = StylometryAnalyzer()
        scorer = ConfidenceScorer(stylometer)
        relationships = scorer.compute_all_pair_scores(df)
        
        self.assertGreater(len(relationships), 0)
        top_rel = relationships[0]
        
        # ShadowX and DarkWolf should be top ranked pair
        self.assertIn(top_rel["username_a"], ["ShadowX", "DarkWolf"])
        self.assertIn(top_rel["username_b"], ["ShadowX", "DarkWolf"])
        self.assertGreaterEqual(top_rel["confidence_score"], 0.80)
        self.assertEqual(top_rel["pgp_score"], 1.0)
        self.assertEqual(top_rel["wallet_score"], 1.0)
        print(f"\n[PASS] Top Confidence Match: {top_rel['username_a']} <-> {top_rel['username_b']} = {top_rel['confidence_percentage']}")

    def test_05_report_exports(self):
        df, stats = load_and_preprocess_csv(self.sample_csv_path)
        stylometer = StylometryAnalyzer()
        scorer = ConfidenceScorer(stylometer)
        relationships = scorer.compute_all_pair_scores(df)
        
        json_out = ReportExporter.to_json(relationships, stats)
        csv_out = ReportExporter.to_csv(relationships)
        html_out = ReportExporter.to_html_report(relationships[0])
        
        self.assertIn("TRACENET", json_out)
        self.assertIn("Username_A", csv_out)
        self.assertIn("<html", html_out)
        print("\n[PASS] Report Export Formats (JSON, CSV, HTML) verified!")

if __name__ == '__main__':
    unittest.main()
