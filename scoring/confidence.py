import pandas as pd
from typing import Dict, List, Any, Tuple
from ai.stylometry import StylometryAnalyzer

# Exact requested weight coefficients
WEIGHT_PGP = 0.30
WEIGHT_WALLET = 0.25
WEIGHT_DOMAIN = 0.20
WEIGHT_WRITING_STYLE = 0.25

class ConfidenceScorer:
    """
    Evidence Fusion & Weighted Confidence Score Engine for TRACENET.
    Correlates PGP, Wallet, Domain, and Stylometry evidence signals into explainable confidence scores.
    """
    def __init__(self, stylometry_analyzer: StylometryAnalyzer):
        self.stylometry_analyzer = stylometry_analyzer

    def compute_all_pair_scores(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Computes pairwise evidence signals and confidence scores for all unique username pairs.
        Returns sorted list of relationship evidence dictionaries (highest confidence first).
        """
        # 1. Extract per-user entity sets
        user_pgps = df.groupby('username')['pgp_key'].apply(lambda s: set(s.dropna())).to_dict()
        user_wallets = df.groupby('username')['wallet_id'].apply(lambda s: set(s.dropna())).to_dict()
        user_domains = df.groupby('username')['domain'].apply(lambda s: set(s.dropna())).to_dict()
        
        usernames = sorted(list(user_pgps.keys()))
        
        # 2. Run stylometric similarity analysis
        stylometry_matrix, meta = self.stylometry_analyzer.analyze_usernames(df)

        relationships = []

        # 3. Pairwise evidence extraction
        for i in range(len(usernames)):
            for j in range(i + 1, len(usernames)):
                u_a = usernames[i]
                u_b = usernames[j]

                # PGP Evidence Signal (1.0 or 0.0)
                shared_pgps = user_pgps[u_a].intersection(user_pgps[u_b])
                # Ignore placeholder UNKNOWN_PGP if both are unknown
                shared_pgps = {p for p in shared_pgps if p != 'UNKNOWN_PGP'}
                pgp_score = 1.0 if len(shared_pgps) > 0 else 0.0

                # Wallet Evidence Signal (1.0 or 0.0)
                shared_wallets = user_wallets[u_a].intersection(user_wallets[u_b])
                shared_wallets = {w for w in shared_wallets if w != 'UNKNOWN_WALLET'}
                wallet_score = 1.0 if len(shared_wallets) > 0 else 0.0

                # Domain Evidence Signal (1.0 for exact, 0.5 for overlap, 0.0 for none)
                domains_a = user_domains[u_a]
                domains_b = user_domains[u_b]
                shared_domains = domains_a.intersection(domains_b)
                
                if domains_a and domains_b and domains_a == domains_b:
                    domain_score = 1.0
                elif len(shared_domains) > 0:
                    domain_score = 0.5
                else:
                    domain_score = 0.0

                # Writing Style Score from transformer embeddings
                writing_score = stylometry_matrix.get((u_a, u_b), 0.0)

                # Weighted Confidence Formula
                confidence = (
                    (WEIGHT_PGP * pgp_score) +
                    (WEIGHT_WALLET * wallet_score) +
                    (WEIGHT_DOMAIN * domain_score) +
                    (WEIGHT_WRITING_STYLE * writing_score)
                )
                confidence = min(max(confidence, 0.0), 1.0) # Clamp 0.0 to 1.0

                # Explanation Generator
                explanations = []
                if shared_pgps:
                    explanations.append(f"✓ Both usernames use shared PGP key: {', '.join(shared_pgps)}")
                else:
                    explanations.append("✗ No shared PGP key found")

                if shared_wallets:
                    explanations.append(f"✓ Both usernames are associated with wallet: {', '.join(shared_wallets)}")
                else:
                    explanations.append("✗ No shared wallet address found")

                if shared_domains:
                    explanations.append(f"✓ Shared domain association: {', '.join(shared_domains)}")
                else:
                    explanations.append("✗ No overlapping dark-web domains")

                explanations.append(f"✓ Writing-style similarity: {writing_score * 100:.1f}%")

                # AI Assessment Level
                if confidence >= 0.75:
                    assessment = "High Potential Link"
                elif confidence >= 0.50:
                    assessment = "Moderate Potential Link"
                else:
                    assessment = "Low / Weak Link"

                relationships.append({
                    "username_a": u_a,
                    "username_b": u_b,
                    "confidence_score": round(confidence, 4),
                    "confidence_percentage": f"{confidence * 100:.1f}%",
                    "pgp_score": pgp_score,
                    "wallet_score": wallet_score,
                    "domain_score": domain_score,
                    "writing_style_score": writing_score,
                    "pgp_match_pct": f"{pgp_score * 100:.0f}%",
                    "wallet_match_pct": f"{wallet_score * 100:.0f}%",
                    "domain_match_pct": f"{domain_score * 100:.0f}%",
                    "writing_match_pct": f"{writing_score * 100:.1f}%",
                    "shared_pgps": list(shared_pgps),
                    "shared_wallets": list(shared_wallets),
                    "shared_domains": list(shared_domains),
                    "evidence_explanation": explanations,
                    "ai_assessment": assessment,
                    "investigator_review_status": "Pending Review",
                    "review_notes": ""
                })

        # Sort by confidence score descending
        relationships.sort(key=lambda x: x["confidence_score"], reverse=True)
        return relationships
