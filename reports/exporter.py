import json
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime

class ReportExporter:
    """
    Intelligence Exporter for TRACENET.
    Generates downloadable JSON, CSV, and HTML/PDF intelligence correlation reports for investigators.
    """
    
    @staticmethod
    def to_json(relationships: List[Dict[str, Any]], stats: Dict[str, Any]) -> str:
        """Exports dataset stats and relationship scores as formatted JSON string."""
        report_payload = {
            "title": "TRACENET Cyber Intelligence Persona Correlation Report",
            "generated_at": datetime.now().isoformat(),
            "summary_statistics": stats,
            "persona_relationships": relationships
        }
        return json.dumps(report_payload, indent=2)

    @staticmethod
    def to_csv(relationships: List[Dict[str, Any]]) -> str:
        """Exports persona relationships as CSV text."""
        records = []
        for rel in relationships:
            records.append({
                "Username_A": rel["username_a"],
                "Username_B": rel["username_b"],
                "Overall_Confidence": rel["confidence_percentage"],
                "Confidence_Score": rel["confidence_score"],
                "PGP_Score": rel["pgp_match_pct"],
                "Wallet_Score": rel["wallet_match_pct"],
                "Domain_Score": rel["domain_match_pct"],
                "Writing_Similarity": rel["writing_match_pct"],
                "AI_Assessment": rel["ai_assessment"],
                "Review_Status": rel["investigator_review_status"],
                "Shared_PGPs": "; ".join(rel["shared_pgps"]),
                "Shared_Wallets": "; ".join(rel["shared_wallets"]),
                "Shared_Domains": "; ".join(rel["shared_domains"])
            })
        df = pd.DataFrame(records)
        return df.to_csv(index=False)

    @staticmethod
    def to_html_report(rel: Dict[str, Any], case_id: str = "TRACENET-2026-001") -> str:
        """
        Generates printable HTML Intelligence Case Report for a specific persona link.
        """
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>TRACENET Intelligence Report - {rel['username_a']} vs {rel['username_b']}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    background-color: #0d1117;
                    color: #c9d1d9;
                    margin: 0;
                    padding: 40px;
                }}
                .container {{
                    max-width: 850px;
                    margin: 0 auto;
                    background: #161b22;
                    border: 1px solid #30363d;
                    border-radius: 8px;
                    padding: 30px;
                    box-shadow: 0 8px 24px rgba(0,0,0,0.5);
                }}
                .header {{
                    border-bottom: 2px solid #58a6ff;
                    padding-bottom: 15px;
                    margin-bottom: 25px;
                }}
                .header h1 {{
                    color: #58a6ff;
                    margin: 0 0 8px 0;
                    font-size: 24px;
                    letter-spacing: 1px;
                }}
                .header .meta {{
                    font-size: 13px;
                    color: #8b949e;
                }}
                .badge {{
                    display: inline-block;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 14px;
                }}
                .high {{ background: rgba(248, 81, 73, 0.2); color: #f85149; border: 1px solid #f85149; }}
                .medium {{ background: rgba(210, 153, 34, 0.2); color: #d29922; border: 1px solid #d29922; }}
                .low {{ background: rgba(56, 139, 253, 0.2); color: #388bfd; border: 1px solid #388bfd; }}
                
                .score-box {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    background: #21262d;
                    padding: 20px;
                    border-radius: 6px;
                    margin-bottom: 25px;
                }}
                .score-num {{
                    font-size: 36px;
                    font-weight: bold;
                    color: #58a6ff;
                }}
                .grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 15px;
                    margin-bottom: 25px;
                }}
                .card {{
                    background: #21262d;
                    padding: 15px;
                    border-radius: 6px;
                    border-left: 3px solid #58a6ff;
                }}
                .card label {{
                    font-size: 12px;
                    color: #8b949e;
                    text-transform: uppercase;
                }}
                .card .val {{
                    font-size: 18px;
                    font-weight: bold;
                    color: #f0f6fc;
                    margin-top: 5px;
                }}
                .explanation {{
                    background: #0d1117;
                    padding: 15px;
                    border-radius: 6px;
                    border: 1px solid #30363d;
                    margin-bottom: 25px;
                }}
                .explanation ul {{
                    margin: 8px 0 0 20px;
                    padding: 0;
                }}
                .explanation li {{
                    margin-bottom: 6px;
                    color: #e6edf3;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 15px;
                    border-top: 1px solid #30363d;
                    font-size: 11px;
                    color: #8b949e;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>TRACENET CYBER INTELLIGENCE CORRELATION REPORT</h1>
                    <div class="meta">Case Reference: <strong>{case_id}</strong> | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</div>
                </div>

                <div class="score-box">
                    <div>
                        <div style="font-size: 14px; color: #8b949e;">TARGET PERSONAS</div>
                        <div style="font-size: 20px; font-weight: bold; color: #ffffff;">{rel['username_a']} &harr; {rel['username_b']}</div>
                        <div style="margin-top: 8px;">AI Assessment: <span class="badge high">{rel['ai_assessment']}</span></div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 12px; color: #8b949e;">OVERALL CONFIDENCE</div>
                        <div class="score-num">{rel['confidence_percentage']}</div>
                    </div>
                </div>

                <h3 style="color: #58a6ff; border-bottom: 1px solid #30363d; padding-bottom: 5px;">EVIDENCE FACTOR BREAKDOWN</h3>
                <div class="grid">
                    <div class="card">
                        <label>PGP Key Match (Weight: 30%)</label>
                        <div class="val">{rel['pgp_match_pct']}</div>
                    </div>
                    <div class="card">
                        <label>Wallet Address Match (Weight: 25%)</label>
                        <div class="val">{rel['wallet_match_pct']}</div>
                    </div>
                    <div class="card">
                        <label>Domain Association Match (Weight: 20%)</label>
                        <div class="val">{rel['domain_match_pct']}</div>
                    </div>
                    <div class="card">
                        <label>Stylometric Writing Similarity (Weight: 25%)</label>
                        <div class="val">{rel['writing_match_pct']}</div>
                    </div>
                </div>

                <h3 style="color: #58a6ff; border-bottom: 1px solid #30363d; padding-bottom: 5px;">EVIDENCE CORRELATION REASONING</h3>
                <div class="explanation">
                    <ul>
                        {"".join(f"<li>{item}</li>" for item in rel['evidence_explanation'])}
                    </ul>
                </div>

                <h3 style="color: #58a6ff; border-bottom: 1px solid #30363d; padding-bottom: 5px;">HUMAN INVESTIGATOR REVIEW</h3>
                <div style="background: #21262d; padding: 15px; border-radius: 6px;">
                    <div><strong>Review Status:</strong> {rel['investigator_review_status']}</div>
                    <div style="margin-top: 8px;"><strong>Investigator Notes:</strong> {rel['review_notes'] if rel['review_notes'] else 'No notes added.'}</div>
                </div>

                <div class="footer">
                    CONFIDENTIAL CYBER INTELLIGENCE REPORT &bull; GENERATED BY TRACENET PROTOTYPE SYSTEM &bull; FOR AUTHORIZED LAW ENFORCEMENT & INVESTIGATOR USE ONLY
                </div>
            </div>
        </body>
        </html>
        """
        return html
