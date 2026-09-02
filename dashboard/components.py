import streamlit as st
import networkx as nx
import streamlit.components.v1 as components
import json
from typing import Dict, List, Any

# Node aesthetic palette
NODE_COLORS = {
    "Username": "#e63946",   # Vibrant Crimson
    "PGPKey": "#9d4edd",     # Neon Purple
    "Wallet": "#00f5d4",     # Bright Cyan/Teal
    "Domain": "#3a86ff",     # Royal Blue
    "Post": "#ffb703",       # Gold
    "Source": "#8d99ae"      # Slate Gray
}

def inject_cyber_theme():
    """Injects high-end dark cyber intelligence CSS styling into Streamlit."""
    st.markdown("""
        <style>
            /* Global Page Styling */
            .main {
                background-color: #0b0f19;
                color: #e2e8f0;
            }
            .stApp {
                background-color: #0b0f19;
            }
            
            /* Top Banner Styling */
            .tracenet-header {
                background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                padding: 24px;
                border-radius: 12px;
                border: 1px solid #334155;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
                margin-bottom: 24px;
            }
            .tracenet-title {
                font-family: 'Inter', sans-serif;
                font-weight: 800;
                font-size: 32px;
                background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin: 0;
            }
            .tracenet-subtitle {
                color: #94a3b8;
                font-size: 14px;
                margin-top: 4px;
            }

            /* Metric Cards */
            .metric-card {
                background: #1e293b;
                border: 1px solid #334155;
                border-radius: 10px;
                padding: 16px;
                text-align: center;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            }
            .metric-val {
                font-size: 28px;
                font-weight: 700;
                color: #38bdf8;
            }
            .metric-lbl {
                font-size: 12px;
                color: #94a3b8;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-top: 4px;
            }

            /* Badges */
            .badge-high {
                background-color: rgba(239, 68, 68, 0.2);
                color: #ef4444;
                border: 1px solid #ef4444;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: 600;
            }
            .badge-med {
                background-color: rgba(245, 158, 11, 0.2);
                color: #f59e0b;
                border: 1px solid #f59e0b;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: 600;
            }
            .badge-low {
                background-color: rgba(59, 130, 246, 0.2);
                color: #3b82f6;
                border: 1px solid #3b82f6;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: 600;
            }
        </style>
    """, unsafe_allow_html=True)


def render_metric_cards(stats: Dict[str, int], high_links_count: int = 0):
    """Renders sleek top metric summary cards."""
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val">{stats.get('records_processed', 0)}</div>
                <div class="metric-lbl">Total Records</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val" style="color: #e63946;">{stats.get('unique_usernames', 0)}</div>
                <div class="metric-lbl">Unique Users</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val" style="color: #9d4edd;">{stats.get('unique_pgp_keys', 0)}</div>
                <div class="metric-lbl">PGP Keys</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val" style="color: #00f5d4;">{stats.get('unique_wallets', 0)}</div>
                <div class="metric-lbl">Wallets</div>
            </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val" style="color: #3a86ff;">{stats.get('unique_domains', 0)}</div>
                <div class="metric-lbl">Domains</div>
            </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val" style="color: #ffb703;">{high_links_count}</div>
                <div class="metric-lbl">High Links</div>
            </div>
        """, unsafe_allow_html=True)


def render_network_graph(nx_graph: nx.Graph, height: int = 550):
    """
    Renders an interactive HTML network graph in Streamlit using PyVis or fallback HTML canvas.
    """
    try:
        from pyvis.network import Network
        
        net = Network(height=f"{height}px", width="100%", bgcolor="#0b0f19", font_color="#e2e8f0", directed=False)
        
        # Configure physics for smooth layout
        net.barcode = False
        net.toggle_physics(True)
        
        # Add nodes with distinct colors and shapes
        for node, data in nx_graph.nodes(data=True):
            ntype = data.get("node_type", "Unknown")
            color = NODE_COLORS.get(ntype, "#8d99ae")
            shape = "dot"
            size = 18
            
            if ntype == "Username":
                shape = "star"
                size = 28
            elif ntype == "PGPKey":
                shape = "diamond"
                size = 22
            elif ntype == "Wallet":
                shape = "square"
                size = 22
            elif ntype == "Domain":
                shape = "triangle"
                size = 20
            elif ntype == "Post":
                shape = "dot"
                size = 10

            title_text = f"<b>{ntype}</b>: {node}"
            if "title" in data:
                title_text += f"<br>{data['title']}"

            net.add_node(str(node), label=str(node), title=title_text, color=color, shape=shape, size=size)

        # Add edges
        for u, v, data in nx_graph.edges(data=True):
            rel = data.get("rel_type", "CONNECTED")
            net.add_edge(str(u), str(v), title=f"Relationship: {rel}", color="#334155")

        # Set physics options for graph stability
        net.set_options("""
        var options = {
          "physics": {
            "barnesHut": {
              "gravitationalConstant": -4000,
              "centralGravity": 0.3,
              "springLength": 95
            },
            "minVelocity": 0.75
          }
        }
        """)

        # Export HTML to string and render directly
        html_content = net.generate_html()
        components.html(html_content, height=height + 20, scrolling=False)

    except Exception as e:
        st.warning(f"Interactive PyVis graph rendering fallback: {e}")
        st.info("Displaying node adjacency table summary:")
        summary_data = []
        for node, data in nx_graph.nodes(data=True):
            neighbors = list(nx_graph.neighbors(node))
            summary_data.append({
                "Entity": node,
                "Type": data.get("node_type", "Unknown"),
                "Degree": len(neighbors),
                "Connected Entities": ", ".join([str(n) for n in neighbors[:5]])
            })
        st.dataframe(summary_data, use_container_width=True)
