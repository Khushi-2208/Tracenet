# TRACENET: Multi-Source Cyber Intelligence Persona Correlation Platform

> **Proof-of-Concept for Human Investigator Assistance**  
> *TRACENET correlates multiple evidence sources—PGP public keys, crypto wallet IDs, onion domains, and transformer-based writing-style similarity—to identify potential relationships between online personas on dark-web and open forums and present evidence breakdowns to a human investigator for verification.*

---

## 🏗️ Project Architecture

```text
TRACENET/
│
├── app.py                      # Main Streamlit Investigator Dashboard
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable configuration template
├── .env                        # Active environment configuration
├── docker-compose.yml          # Neo4j Docker container setup
├── README.md                   # Complete documentation & Golden Demo guide
│
├── data/
│   └── sample_data.csv         # Synthetic threat intelligence dataset (40 records)
│
├── ingestion/
│   ├── __init__.py
│   └── csv_processor.py        # CSV validation, cleaning, normalization & metric extraction
│
├── graph/
│   ├── __init__.py
│   ├── neo4j_client.py         # Neo4j Cypher schema & graph connection driver
│   └── graph_builder.py        # Graph generator (Neo4j & NetworkX dual engine)
│
├── ai/
│   ├── __init__.py
│   ├── embeddings.py           # Pretrained BERT/RoBERTa dense text embedding extractor
│   └── stylometry.py           # Pairwise writing-style cosine similarity calculator
│
├── scoring/
│   ├── __init__.py
│   └── confidence.py           # Multi-factor evidence fusion & weighted confidence engine
│
├── dashboard/
│   ├── __init__.py
│   └── components.py           # Dark Cyber UI styling, metric cards & PyVis network graph
│
├── reports/
│   ├── __init__.py
│   └── exporter.py             # Downloadable JSON, CSV & printable HTML case report exporter
│
└── tests/
    ├── __init__.py
    └── test_pipeline.py        # Automated test suite
```

---

## ⚡ Quick Start & Installation

### A. Environment Setup

Ensure Python 3.9+ is installed.

```bash
# Navigate to project root
cd d:\SIH

# Install dependencies
pip install -r requirements.txt
```

### B. Starting Neo4j Database (Optional / Recommended)

TRACENET includes an automatic fallback to an in-memory NetworkX engine if Neo4j is offline. To use live Neo4j Cypher querying:

#### Option 1: Using Docker Compose
```bash
docker-compose up -d neo4j
```

#### Option 2: Using Neo4j Desktop / Enterprise
1. Download and start Neo4j Desktop.
2. Set credentials in `.env`:
   ```ini
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=tracenet_secure_pass
   ```

### C. Running Automated Test Suite

Verify that all ingestion, AI stylometry, graph, and confidence scoring functions work end-to-end:

```bash
python -m unittest discover -s tests
```

---

## 🚀 Running the TRACENET Application

### 1. Start the Backend API Server

```bash
uvicorn backend.main:app --reload --port 8000
```

The FastAPI backend will be available at `http://localhost:8000`.

### 2. Start the Frontend Dev Server

```bash
cd frontend
npm run dev
```

The web dashboard will be available at `http://localhost:5173`.

---

## 🎯 Golden Demo Guide for Judges

Follow these exact steps for a complete live demonstration:

1. **Step 1: Load Ingestion Data**
   - Click **"🚀 Load Sample CSV"** on the sidebar or upload `data/sample_data.csv`.
2. **Step 2: Inspect Statistics**
   - In the **📊 Data Overview** tab, review the top metric cards (40 Total Records, 20 Unique Users, 18 PGP Keys, 18 Wallets, 13 Domains).
3. **Step 3: Investigator Search & Profile**
   - Open **🔍 Investigator Search**.
   - Select `ShadowX` from the persona dropdown.
   - View associated PGP key (`PGP_KEY_001_ALPHA`), Wallet (`WALLET_BTC_9901_SEC`), Domains, and authored post snippets.
4. **Step 4: Explore Characteristic Graph**
   - Open **🕸️ Characteristic Graph**.
   - Observe connected star nodes representing usernames (`ShadowX` ↔ `DarkWolf`) connected through diamond PGP nodes and square Wallet nodes.
5. **Step 5: Stylometric Writing Similarity & Evidence Scoring**
   - Open **🔗 Persona Relationships & Review**.
   - Observe top-ranked relationship pair: **`ShadowX ↔ DarkWolf` (Confidence: 87.0% - High Potential Link)**.
   - Select `ShadowX ↔ DarkWolf` in the Inspector to view the weighted multi-factor breakdown:
     - **PGP Score (30%)**: 100% (Shared `PGP_KEY_001_ALPHA`)
     - **Wallet Score (25%)**: 100% (Shared `WALLET_BTC_9901_SEC`)
     - **Domain Score (20%)**: 100% (Shared `darkmarket-x.onion`)
     - **Writing Style Similarity (25%)**: ~85-90% (Dense BERT/RoBERTa sentence-transformer embedding cosine similarity)
6. **Step 6: Human-in-the-Loop Review**
   - Update verification radio status to **`Marked as Verified Link`**.
   - Enter case notes and click **"💾 Save Investigator Assessment"**.
7. **Step 7: Intelligence Report Export**
   - Open **📄 Export Intelligence Report**.
   - Click **Download JSON Report**, **Download CSV Summary**, or **Download HTML Report** to generate printable intelligence files.

---

## 🧮 Multi-Factor Evidence Confidence Formula

```text
Confidence Score = 
    (0.30 × PGP Key Match) +
    (0.25 × Wallet Address Match) +
    (0.20 × Domain Overlap Match) +
    (0.25 × Writing Style Similarity)
```

- **PGP Match**: 1.0 if identical shared PGP public key, else 0.0.
- **Wallet Match**: 1.0 if identical shared cryptocurrency wallet address, else 0.0.
- **Domain Match**: 1.0 for exact domain set match, 0.5 for partial overlap, 0.0 for none.
- **Writing Style Similarity**: Cosine similarity (0.0 to 1.0) derived from dense transformer embeddings.

---

## ⚠️ Disclaimer & Future Enhancements

- **Proof-of-Concept Notice**: TRACENET stylometry embedding signals serve as an evidence correlation aid for human investigators and do not constitute legal proof of authorship.
- **Synthetic Data**: The demonstration dataset uses realistic synthetic dark-web forum posts.
- **Future Roadmap**:
  - Integration with live dark-web onion crawlers and automated scraper pipelines.
  - Multi-language stylometric embedding fine-tuning (e.g. mBERT / XLM-RoBERTa).
  - Graph Neural Network (GNN) link prediction models for advanced persona discovery.
