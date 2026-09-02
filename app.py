import streamlit as st
import pandas as pd
import numpy as np
import os
import json
from typing import Dict, List, Any

from ingestion.csv_processor import load_and_preprocess_csv
from graph.graph_builder import CharacteristicGraph
from ai.stylometry import StylometryAnalyzer
from scoring.confidence import ConfidenceScorer
from reports.exporter import ReportExporter
from dashboard.components import inject_cyber_theme, render_metric_cards, render_network_graph

# Configure Streamlit Page Settings
st.set_page_config(
    page_title="TRACENET - Cyber Intelligence Persona Correlation",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize global styling
inject_cyber_theme()

# Page Header
st.markdown("""
    <div class="tracenet-header">
        <div class="tracenet-title">TRACENET &bull; Cyber Intelligence Platform</div>
        <div class="tracenet-subtitle">
            Multi-Source Persona Correlation & Stylometric Intelligence Fusion Engine for Cyber Investigations
        </div>
    </div>
""", unsafe_allow_html=True)

# Important Human-in-the-loop Banner Notice
st.info("⚠️ **Human-in-the-Loop Decision Support Notice**: TRACENET correlates PGP keys, wallet IDs, domains, and stylometric similarity signals to assist human investigators. It does NOT automatically label individuals or guarantee real-world identity.")

# Initialize Session States
if "df" not in st.session_state:
    st.session_state.df = None
if "stats" not in st.session_state:
    st.session_state.stats = {}
if "graph" not in st.session_state:
    st.session_state.graph = None
if "relationships" not in st.session_state:
    st.session_state.relationships = []
if "stylometry_meta" not in st.session_state:
    st.session_state.stylometry_meta = {}

# Sidebar File Ingestion Controls
with st.sidebar:
    st.header("📂 Intelligence Ingestion")
    st.markdown("Upload dark-web forum dump CSV or load synthetic proof-of-concept dataset.")
    
    uploaded_file = st.file_uploader("Upload CSV Dataset", type=["csv"])
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        use_sample = st.button("🚀 Load Sample CSV", use_container_width=True)
    with col_btn2:
        reset_app = st.button("🔄 Reset", use_container_width=True)

    if reset_app:
        st.session_state.df = None
        st.session_state.stats = {}
        st.session_state.graph = None
        st.session_state.relationships = []
        st.rerun()

    st.markdown("---")
    st.header("⚙️ Engine Status")
    
    # Check Neo4j status dynamically if graph exists
    neo4j_status = "Not Initialized"
    if st.session_state.graph:
        if st.session_state.graph.neo4j_active:
            neo4j_status = "🟢 Connected (Bolt Protocol)"
        else:
            neo4j_status = "🟡 Offline (NetworkX Fallback Active)"
            
    st.markdown(f"**Neo4j Database**: {neo4j_status}")
    if st.session_state.stylometry_meta:
        st.markdown(f"**AI Stylometry Engine**: {st.session_state.stylometry_meta.get('engine', 'Transformer')}")
    st.markdown("---")
    st.markdown("Developed for **SIH Proof-of-Concept Demonstration**")


# Function to Process Dataset
def run_ingestion_and_analysis(data_input):
    with st.spinner("Executing TRACENET Ingestion & Analysis Pipeline..."):
        # 1. Ingestion & Preprocessing
        df, stats = load_and_preprocess_csv(data_input)
        st.session_state.df = df
        st.session_state.stats = stats
        
        # 2. Build Characteristic Graph
        cgraph = CharacteristicGraph()
        cgraph.build_graph(df)
        st.session_state.graph = cgraph
        
        # 3. AI Stylometry & Confidence Scoring
        stylometer = StylometryAnalyzer()
        scorer = ConfidenceScorer(stylometer)
        
        relationships = scorer.compute_all_pair_scores(df)
        st.session_state.relationships = relationships
        st.session_state.stylometry_meta = {
            "engine": stylometer.embedding_engine.engine_type,
            "usernames_analyzed": stats["unique_usernames"]
        }


# Handle Load Triggers
if use_sample or (st.session_state.df is None and not uploaded_file):
    sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_data.csv")
    if os.path.exists(sample_path):
        run_ingestion_and_analysis(sample_path)
    else:
        st.error(f"Sample data file not found at {sample_path}")

elif uploaded_file is not None and st.session_state.df is None:
    run_ingestion_and_analysis(uploaded_file)


# Render Main Application Views if Data Loaded
if st.session_state.df is not None:
    df = st.session_state.df
    stats = st.session_state.stats
    cgraph = st.session_state.graph
    relationships = st.session_state.relationships

    # Top Metric Overview
    high_links = len([r for r in relationships if r["confidence_score"] >= 0.75])
    render_metric_cards(stats, high_links_count=high_links)
    st.markdown("<br>", unsafe_allow_html=True)

    # Main Navigation Tabs
    tab_overview, tab_search, tab_graph, tab_matrix, tab_export = st.tabs([
        "📊 Data Overview",
        "🔍 Investigator Search",
        "🕸️ Characteristic Graph",
        "🔗 Persona Relationships & Review",
        "📄 Export Intelligence Report"
    ])

    # ==========================================
    # TAB 1: DATA OVERVIEW & PREPROCESSING
    # ==========================================
    with tab_overview:
        st.subheader("Data Extraction & Preprocessing Summary")
        st.markdown("Cleaned dataset containing extracted PGP keys, wallet IDs, onion domains, and forum post snippets.")
        
        col_left, col_right = st.columns([1, 2])
        with col_left:
            st.markdown("### Preprocessing Pipeline Stats")
            st.json({
                "Total Records Ingested": stats.get("records_processed"),
                "Unique Usernames Extracted": stats.get("unique_usernames"),
                "Unique PGP Public Keys": stats.get("unique_pgp_keys"),
                "Unique Crypto Wallet Addresses": stats.get("unique_wallets"),
                "Unique Onion/Web Domains": stats.get("unique_domains"),
                "Sources Identified": stats.get("unique_sources")
            })
            
        with col_right:
            st.markdown("### Normalized Ingested Threat Intelligence Dataset")
            st.dataframe(
                df[['username', 'pgp_key', 'wallet_id', 'domain', 'source', 'cleaned_text', 'timestamp']],
                use_container_width=True,
                height=320
            )

    # ==========================================
    # TAB 2: INVESTIGATOR SEARCH & PROFILE
    # ==========================================
    with tab_search:
        st.subheader("Investigator Entity Search & Profile Drill-Down")
        
        all_usernames = sorted(df['username'].unique().tolist())
        search_query = st.selectbox("Select or Search Username Persona:", options=all_usernames, index=0)

        if search_query:
            profile = cgraph.get_username_profile(search_query, df)
            
            if profile:
                st.markdown(f"### Persona Intelligence Profile: `< {profile['username']} >`", unsafe_allow_html=True)
                
                pcol1, pcol2, pcol3 = st.columns(3)
                with pcol1:
                    st.markdown("#### 🔑 Associated PGP Keys")
                    if profile['pgp_keys']:
                        for k in profile['pgp_keys']:
                            st.code(k, language="text")
                    else:
                        st.write("None detected")

                with pcol2:
                    st.markdown("#### 💳 Associated Crypto Wallets")
                    if profile['wallets']:
                        for w in profile['wallets']:
                            st.code(w, language="text")
                    else:
                        st.write("None detected")

                with pcol3:
                    st.markdown("#### 🌐 Associated Domains")
                    if profile['domains']:
                        for d in profile['domains']:
                            st.markdown(f"- `{d}`")
                    else:
                        st.write("None detected")

                st.markdown("---")
                col_post, col_link = st.columns([2, 1])
                
                with col_post:
                    st.markdown(f"#### 📝 Authored Forum Posts ({profile['post_count']} total)")
                    for idx, post in enumerate(profile.get('posts', [])):
                        st.text_area(f"Post #{idx+1}", value=post, height=80, disabled=True, key=f"post_{search_query}_{idx}")

                with col_link:
                    st.markdown("#### 👥 Graph Connected Personas")
                    related = profile.get('related_usernames', [])
                    if related:
                        for ruser in related:
                            st.markdown(f"👉 **{ruser}** (Shared Infrastructure)")
                    else:
                        st.write("No direct entity graph overlap found")

    # ==========================================
    # TAB 3: CHARACTERISTIC GRAPH VISUALIZATION
    # ==========================================
    with tab_graph:
        st.subheader("Neo4j Characteristic & Relationship Network Graph")
        st.markdown("""
        Visual representation of extracted nodes (`Username`, `PGPKey`, `Wallet`, `Domain`, `Post`, `Source`) and edge connections (`USES`, `ASSOCIATED_WITH`, `AUTHORED`).
        """)

        # Legend Bar
        l1, l2, l3, l4, l5, l6 = st.columns(6)
        l1.markdown("🔴 **Username**")
        l2.markdown("🟣 **PGP Key**")
        l3.markdown("🟢 **Wallet**")
        l4.markdown("🔵 **Domain**")
        l5.markdown("🟡 **Post**")
        l6.markdown("⚪ **Source**")

        st.markdown("<br>", unsafe_allow_html=True)
        
        if cgraph and cgraph.nx_graph:
            render_network_graph(cgraph.nx_graph, height=580)
        else:
            st.warning("Graph data is not initialized.")

    # ==========================================
    # TAB 4: PERSONA RELATIONSHIPS & REVIEW
    # ==========================================
    with tab_matrix:
        st.subheader("Multi-Source Persona Relationship Matrix & Human-in-the-Loop Review")
        st.markdown("""
        Pairwise evidence fusion combining **30% PGP Key Match**, **25% Wallet Address Match**, **20% Domain Overlap**, and **25% Transformer Writing Style Similarity**.
        """)

        # Overview Table
        rel_records = []
        for rel in relationships:
            rel_records.append({
                "Username A": rel["username_a"],
                "Username B": rel["username_b"],
                "Confidence Score": rel["confidence_percentage"],
                "AI Assessment": rel["ai_assessment"],
                "Review Status": rel["investigator_review_status"],
                "PGP Match": rel["pgp_match_pct"],
                "Wallet Match": rel["wallet_match_pct"],
                "Domain Match": rel["domain_match_pct"],
                "Writing Similarity": rel["writing_match_pct"]
            })
        
        rel_df = pd.DataFrame(rel_records)
        st.dataframe(rel_df, use_container_width=True, height=280)

        st.markdown("---")
        st.subheader("🕵️ Deep Evidence Inspector & Investigator Review")

        # Select pair to drill down
        pair_options = [f"{r['username_a']} ↔ {r['username_b']} ({r['confidence_percentage']})" for r in relationships]
        selected_pair_str = st.selectbox("Select Persona Relationship Pair to Inspect:", options=pair_options, index=0)

        if selected_pair_str:
            selected_idx = pair_options.index(selected_pair_str)
            target_rel = relationships[selected_idx]

            col_detail_left, col_detail_right = st.columns([1, 1])

            with col_detail_left:
                st.markdown(f"### Evidence Scorecard: **{target_rel['username_a']} ↔ {target_rel['username_b']}**")
                
                # Confidence Score Large Display
                score_color = "#ef4444" if target_rel['confidence_score'] >= 0.75 else ("#f59e0b" if target_rel['confidence_score'] >= 0.50 else "#3b82f6")
                st.markdown(f"""
                    <div style="background: #1e293b; padding: 20px; border-radius: 8px; border-left: 6px solid {score_color}; margin-bottom: 20px;">
                        <div style="font-size: 14px; color: #94a3b8;">COMPOSITE EVIDENCE CONFIDENCE</div>
                        <div style="font-size: 42px; font-weight: 800; color: {score_color};">{target_rel['confidence_percentage']}</div>
                        <div style="font-size: 14px; color: #e2e8f0; margin-top: 4px;">AI Signal: <strong>{target_rel['ai_assessment']}</strong></div>
                    </div>
                """, unsafe_allow_html=True)

                st.markdown("#### Signal Weight Breakdown")
                bcol1, bcol2, bcol3, bcol4 = st.columns(4)
                bcol1.metric("PGP (30%)", target_rel['pgp_match_pct'])
                bcol2.metric("Wallet (25%)", target_rel['wallet_match_pct'])
                bcol3.metric("Domain (20%)", target_rel['domain_match_pct'])
                bcol4.metric("Writing (25%)", target_rel['writing_match_pct'])

            with col_detail_right:
                st.markdown("### 🔍 Human-Readable Evidence Reasoning")
                for point in target_rel['evidence_explanation']:
                    if point.startswith("✓"):
                        st.success(point)
                    else:
                        st.write(point)

                st.markdown("---")
                st.markdown("### ⚖️ Investigator Review & Verification")
                
                current_status = target_rel['investigator_review_status']
                new_status = st.radio(
                    "Review Verification Status:",
                    options=["Pending Review", "Marked as Verified Link", "Dismissed / Unrelated"],
                    index=0 if current_status == "Pending Review" else (1 if current_status == "Marked as Verified Link" else 2),
                    key=f"status_radio_{selected_idx}"
                )
                
                user_notes = st.text_area(
                    "Investigator Case Notes & Findings:",
                    value=target_rel['review_notes'],
                    placeholder="Enter analytical observation or verification reference...",
                    key=f"notes_input_{selected_idx}"
                )

                if st.button("💾 Save Investigator Assessment", key=f"save_btn_{selected_idx}"):
                    target_rel['investigator_review_status'] = new_status
                    target_rel['review_notes'] = user_notes
                    st.success("Investigator verification saved to active session!")
                    st.rerun()

    # ==========================================
    # TAB 5: EXPORT INTELLIGENCE REPORT
    # ==========================================
    with tab_export:
        st.subheader("Export Cyber Intelligence Reports")
        st.markdown("Download intelligence correlation data in standard JSON, CSV, or formatted HTML case report formats.")

        ex1, ex2, ex3 = st.columns(3)

        with ex1:
            st.markdown("#### 📄 JSON Intelligence Export")
            json_str = ReportExporter.to_json(relationships, stats)
            st.download_button(
                label="📥 Download JSON Report",
                data=json_str,
                file_name="TRACENET_Intelligence_Report.json",
                mime="application/json",
                use_container_width=True
            )

        with ex2:
            st.markdown("#### 📊 CSV Summary Export")
            csv_str = ReportExporter.to_csv(relationships)
            st.download_button(
                label="📥 Download CSV Summary",
                data=csv_str,
                file_name="TRACENET_Persona_Relationships.csv",
                mime="text/csv",
                use_container_width=True
            )

        with ex3:
            st.markdown("#### 🖨️ Printable HTML Case Report")
            if relationships:
                top_rel = relationships[0] # Top target pair
                html_report = ReportExporter.to_html_report(top_rel)
                st.download_button(
                    label="📥 Download HTML Report",
                    data=html_report,
                    file_name=f"TRACENET_Case_Report_{top_rel['username_a']}_{top_rel['username_b']}.html",
                    mime="text/html",
                    use_container_width=True
                )
