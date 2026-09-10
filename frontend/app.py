"""Main Streamlit application entry point."""

import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from frontend.pages import (
    home,
    executive_overview,
    customer_360,
    profitability,
    risk,
    segmentation,
    churn,
    transactions,
    products,
    decision_intelligence,
    model_monitoring,
    data_quality,
    live_monitor,
)

# Page configuration
st.set_page_config(
    page_title="Banking Analytics Platform",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Advanced Neon CSS Styling - Based on E-Commerce Platform
st.markdown("""
<style>
    /* Enterprise Professional Color Palette - Exact from E-Commerce Platform */
    :root {
        --primary-dark: #000000;
        --primary-slate: #1a1a1a;
        --primary-indigo: #4f46e5;
        --primary-violet: #7c3aed;
        --accent-blue: #3b82f6;
        --accent-emerald: #059669;
        --accent-teal: #14b8a6;
        --neon-pink: #ff00ff;
        --neon-cyan: #00ffff;
        --neon-green: #00ff00;
        --neon-yellow: #ffff00;
        --neon-orange: #ff6600;
        --neon-purple: #9900ff;
        --neon-blue: #0066ff;
        --neon-red: #ff0066;
        --bg-gradient-start: #0a0a0a;
        --bg-gradient-end: #1a1a1a;
        --card-bg: #141414;
        --card-hover: #1e1e1e;
        --text-primary: #ffffff;
        --text-secondary: #e0e0e0;
        --text-muted: #b0b0b0;
    }

    /* Global Styles - Exact from E-Commerce Platform */
    .stApp {
        background: linear-gradient(135deg, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%);
        color: #ffffff;
    }

    /* Enhanced Animated Background - Live Dynamic Effects */
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    @keyframes colorShift {
        0% { filter: hue-rotate(0deg); }
        50% { filter: hue-rotate(180deg); }
        100% { filter: hue-rotate(360deg); }
    }

    @keyframes pulse {
        0%, 100% { opacity: 0.3; transform: scale(1); }
        50% { opacity: 0.6; transform: scale(1.1); }
    }

    @keyframes float {
        0%, 100% { transform: translateY(0px) translateX(0px); }
        25% { transform: translateY(-20px) translateX(10px); }
        50% { transform: translateY(0px) translateX(20px); }
        75% { transform: translateY(20px) translateX(10px); }
    }

    @keyframes scan {
        0% { top: -10%; }
        100% { top: 110%; }
    }

    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #0a0a0a 100%);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite, colorShift 30s linear infinite;
    }

    /* Dynamic Neon Orbs */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background:
            radial-gradient(circle at 10% 20%, rgba(0, 255, 255, 0.15) 0%, transparent 40%),
            radial-gradient(circle at 90% 80%, rgba(255, 0, 255, 0.15) 0%, transparent 40%),
            radial-gradient(circle at 50% 50%, rgba(0, 255, 100, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 30% 70%, rgba(255, 100, 0, 0.1) 0%, transparent 40%);
        pointer-events: none;
        z-index: -2;
        animation: pulse 8s ease-in-out infinite;
    }

    /* Floating Particles */
    .stApp::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image:
            radial-gradient(2px 2px at 20px 30px, rgba(0, 255, 255, 0.3), transparent),
            radial-gradient(2px 2px at 40px 70px, rgba(255, 0, 255, 0.3), transparent),
            radial-gradient(2px 2px at 50px 50px, rgba(0, 255, 100, 0.3), transparent),
            radial-gradient(2px 2px at 90px 10px, rgba(255, 100, 0, 0.3), transparent),
            radial-gradient(2px 2px at 130px 80px, rgba(0, 255, 255, 0.3), transparent),
            radial-gradient(2px 2px at 160px 30px, rgba(255, 0, 255, 0.3), transparent);
        background-size: 200px 200px;
        animation: float 20s ease-in-out infinite;
        pointer-events: none;
        z-index: -1;
    }

    /* Scanning Beam Effect */
    .stApp .main::before {
        content: '';
        position: fixed;
        top: -10%;
        left: 0;
        width: 100%;
        height: 20%;
        background: linear-gradient(180deg, transparent, rgba(0, 255, 255, 0.1), transparent);
        animation: scan 8s linear infinite;
        pointer-events: none;
        z-index: -1;
    }

    /* Grid Pattern Overlay */
    .stApp .main::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image:
            linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 50px 50px;
        pointer-events: none;
        z-index: -1;
    }

    /* Sidebar Background - Exact from E-Commerce Platform */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0a0a 0%, #1a1a1a 100%);
        border-right: 2px solid var(--neon-cyan);
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);
    }

    [data-testid="stSidebar"] > div:first-child {
        background: transparent;
    }

    /* Card Background - Exact from E-Commerce Platform */
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
        border: 2px solid var(--neon-cyan);
        border-radius: 20px;
        color: #ffffff;
        margin: 0.6rem 0;
        padding: 1.2rem;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6), 0 0 20px var(--neon-cyan);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        animation: slideInUp 0.8s ease-out;
    }

    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 60px var(--neon-cyan), 0 0 40px var(--neon-pink);
        border-color: var(--neon-pink);
    }

    /* Headers */
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 2rem;
        text-align: center;
        animation: fadeInDown 1s ease-out;
        color: #ffffff;
        text-shadow: 0 0 40px rgba(0, 255, 255, 0.5);
        filter: drop-shadow(0 0 10px rgba(0, 255, 255, 0.3));
    }

    /* Apply neon glow to entire header including emoji - matching sidebar */
    .main-header {
        animation: fadeInDown 1s ease-out, iconPulse 2s ease-in-out infinite;
    }

    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-40px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Subheaders */
    h2, h3 {
        color: #ffffff;
        font-weight: 700;
        margin-top: 1.8rem;
        letter-spacing: 0.5px;
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
        filter: drop-shadow(0 0 5px rgba(255, 0, 255, 0.3));
    }

    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
        border: 2px solid var(--neon-cyan);
        border-radius: 20px;
        color: #ffffff;
        margin: 0.6rem 0;
        padding: 1.2rem;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6), 0 0 20px var(--neon-cyan);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        animation: slideInUp 0.8s ease-out;
    }

    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 60px var(--neon-cyan), 0 0 40px var(--neon-pink);
        border-color: var(--neon-pink);
    }

    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(40px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Streamlit Metrics Enhancement */
    div[data-testid="stMetricValue"] {
        background: linear-gradient(135deg, var(--neon-cyan), var(--neon-pink), var(--neon-green));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        text-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
        filter: drop-shadow(0 0 10px rgba(255, 0, 255, 0.3));
    }

    div[data-testid="stMetricDelta"] {
        font-weight: 700;
        font-size: 1.1rem;
        color: #ffffff;
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
    }

    div[data-testid="stMetricLabel"] {
        color: #e0e0e0;
        font-weight: 600;
        text-shadow: 0 0 5px rgba(0, 255, 255, 0.3);
    }

    /* Alert Boxes */
    .alert-box {
        padding: 1.8rem;
        border-radius: 16px;
        margin: 1rem 0;
        border: 2px solid;
        animation: fadeIn 0.6s ease-out;
    }

    .alert-success {
        background: #0a2a1a;
        border-color: var(--neon-green);
        color: #ffffff;
        box-shadow: 0 0 20px var(--neon-green);
        text-shadow: 0 0 5px rgba(0, 255, 0, 0.5);
    }

    .alert-warning {
        background: #2a1a0a;
        border-color: var(--neon-orange);
        color: #ffffff;
        box-shadow: 0 0 20px var(--neon-orange);
        text-shadow: 0 0 5px rgba(255, 102, 0, 0.5);
    }

    .alert-error {
        background: #2a0a0a;
        border-color: var(--neon-red);
        color: #ffffff;
        box-shadow: 0 0 20px var(--neon-red);
        text-shadow: 0 0 5px rgba(255, 0, 102, 0.5);
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    @keyframes fadeInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    /* DataFrames */
    .stDataFrame {
        background: var(--card-bg);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid rgba(79, 70, 229, 0.3);
        animation: fadeIn 0.8s ease-out;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }

    /* Plotly Charts */
    .js-plotly-plot {
        border-radius: 16px;
        overflow: hidden;
        animation: zoomIn 0.8s ease-out;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
    }

    @keyframes zoomIn {
        from {
            opacity: 0;
            transform: scale(0.92);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0a0a 0%, #1a1a1a 100%);
        border-right: 2px solid var(--neon-cyan);
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);
    }

    [data-testid="stSidebar"] > div:first-child {
        background: transparent;
    }

    /* Sidebar Navigation */
    .sidebar-nav-item {
        padding: 0.8rem 1rem;
        margin: 0.3rem 0;
        border-radius: 10px;
        transition: all 0.3s ease;
        border: 1px solid transparent;
    }

    .sidebar-nav-item:hover {
        background: linear-gradient(90deg, rgba(0, 255, 255, 0.1), rgba(255, 0, 255, 0.1));
        border-color: var(--neon-cyan);
        transform: translateX(5px);
    }

    /* Charts */
    .js-plotly-plot {
        background: rgba(26, 26, 46, 0.8);
        border-radius: 15px;
        border: 1px solid var(--neon-cyan);
        box-shadow: 0 0 30px rgba(0, 255, 255, 0.2);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--neon-cyan), var(--neon-purple));
        border: none;
        border-radius: 10px;
        color: #ffffff;
        font-weight: 700;
        transition: all 0.3s ease;
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 30px rgba(0, 255, 255, 0.5);
    }

    /* Selectbox and Multiselect */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: rgba(26, 26, 46, 0.8);
        border: 1px solid var(--neon-cyan);
        border-radius: 10px;
    }

    /* Date Input */
    .stDateInput > div > div > input {
        background: rgba(26, 26, 46, 0.8);
        border: 1px solid var(--neon-cyan);
        border-radius: 10px;
        color: #ffffff;
    }

    /* Slider */
    .stSlider > div > div > div {
        background: var(--neon-cyan);
    }

    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--neon-cyan), var(--neon-pink));
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(26, 26, 46, 0.8);
        border: 1px solid var(--neon-cyan);
        border-radius: 10px;
        color: #ffffff;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(26, 26, 46, 0.8);
        border: 1px solid var(--neon-cyan);
        border-radius: 10px 10px 0 0;
        color: #ffffff;
    }

    /* Info and Success Messages */
    .stAlert {
        background: rgba(26, 26, 46, 0.8);
        border: 1px solid var(--neon-cyan);
        border-radius: 15px;
        color: #ffffff;
    }

    /* Icon Pulse Animation */
    @keyframes iconPulse {
        0%, 100% {
            filter: drop-shadow(0 0 5px rgba(0, 255, 255, 0.5));
        }
        50% {
            filter: drop-shadow(0 0 20px rgba(0, 255, 255, 0.8));
        }
    }

    /* Sidebar Navigation Icons */
    .stSidebar [role="navigation"] > div > div > div > div {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
        border-radius: 12px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin: 4px 0;
        background: #141414;
        border: 2px solid var(--neon-cyan);
    }

    .stSidebar [role="navigation"] > div > div > div > div:hover {
        background: linear-gradient(135deg, #003333, #330033);
        transform: translateX(8px);
        box-shadow: 0 0 20px var(--neon-cyan), 0 0 40px var(--neon-pink);
        border-color: var(--neon-pink);
    }

    .stSidebar [role="navigation"] > div > div > div > div > div > span {
        font-size: 1.8rem;
        animation: iconPulse 2s ease-in-out infinite;
        filter: drop-shadow(0 0 8px var(--neon-cyan));
    }

    /* Icon-specific animations with neon colors */
    .stSidebar [role="navigation"] > div > div > div:nth-child(1) > div > div > span {
        animation-delay: 0s;
        filter: drop-shadow(0 0 10px var(--neon-pink));
    }

    .stSidebar [role="navigation"] > div > div > div:nth-child(2) > div > div > span {
        animation-delay: 0.2s;
        filter: drop-shadow(0 0 10px var(--neon-cyan));
    }

    .stSidebar [role="navigation"] > div > div > div:nth-child(3) > div > div > span {
        animation-delay: 0.4s;
        filter: drop-shadow(0 0 10px var(--neon-green));
    }

    .stSidebar [role="navigation"] > div > div > div:nth-child(4) > div > div > span {
        animation-delay: 0.6s;
        filter: drop-shadow(0 0 10px var(--neon-yellow));
    }

    .stSidebar [role="navigation"] > div > div > div:nth-child(5) > div > div > span {
        animation-delay: 0.8s;
        filter: drop-shadow(0 0 10px var(--neon-orange));
    }

    .stSidebar [role="navigation"] > div > div > div:nth-child(6) > div > div > span {
        animation-delay: 1.0s;
        filter: drop-shadow(0 0 10px var(--neon-purple));
    }

    .stSidebar [role="navigation"] > div > div > div:nth-child(7) > div > div > span {
        animation-delay: 1.2s;
        filter: drop-shadow(0 0 10px var(--neon-blue));
    }

    .stSidebar [role="navigation"] > div > div > div:nth-child(8) > div > div > span {
        animation-delay: 1.4s;
        filter: drop-shadow(0 0 10px var(--neon-red));
    }

    @keyframes iconPulse {
        0%, 100% {
            transform: scale(1);
            filter: drop-shadow(0 0 8px var(--neon-cyan));
        }
        50% {
            transform: scale(1.15);
            filter: drop-shadow(0 0 15px var(--neon-pink));
        }
    }

    /* Active navigation item */
    .stSidebar [role="navigation"] > div > div > div > div[aria-selected="true"] {
        background: linear-gradient(135deg, #004d4d, #4d004d);
        border: 3px solid var(--neon-pink);
        box-shadow: 0 0 30px var(--neon-cyan), 0 0 60px var(--neon-pink);
    }

    .stSidebar [role="navigation"] > div > div > div > div[aria-selected="true"] > div > div > span {
        animation: iconGlow 1.5s ease-in-out infinite;
    }

    @keyframes iconGlow {
        0%, 100% {
            transform: scale(1.1) rotate(0deg);
            filter: drop-shadow(0 0 15px var(--neon-pink));
        }
        25% {
            transform: scale(1.2) rotate(5deg);
            filter: drop-shadow(0 0 25px var(--neon-cyan));
        }
        75% {
            transform: scale(1.2) rotate(-5deg);
            filter: drop-shadow(0 0 25px var(--neon-green));
        }
    }

    /* Sidebar header enhancement */
    .stSidebar > div:first-child {
        background: linear-gradient(180deg, #141414, #1e1e1e);
        padding: 20px;
        border-bottom: 3px solid var(--neon-cyan);
        box-shadow: 0 0 20px var(--neon-cyan);
    }

    /* Sidebar sections */
    .stSidebar > div > div > div > div {
        background: linear-gradient(180deg, #141414, #1e1e1e);
        border-radius: 16px;
        padding: 16px;
        margin: 12px 0;
        border: 2px solid var(--neon-purple);
        transition: all 0.3s ease;
        box-shadow: 0 0 15px rgba(153, 0, 255, 0.3);
    }

    .stSidebar > div > div > div > div:hover {
        border-color: var(--neon-cyan);
        box-shadow: 0 0 30px var(--neon-cyan), 0 0 60px var(--neon-pink);
    }

    /* Advanced Table Styling - Original Styling */
    .stDataFrame {
        background: linear-gradient(135deg, #141414, #1e1e1e);
        border-radius: 20px;
        padding: 20px;
        border: 3px solid var(--neon-cyan);
        animation: tableFadeIn 0.8s ease-out;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5), 0 0 30px var(--neon-cyan);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .stDataFrame:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 60px var(--neon-cyan), 0 0 50px var(--neon-pink);
        border-color: var(--neon-pink);
    }

    @keyframes tableFadeIn {
        from {
            opacity: 0;
            transform: translateY(20px) scale(0.95);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    /* Table Header Styling - Original Styling */
    .stDataFrame thead th {
        background: linear-gradient(135deg, #003333, #004444);
        color: #ffffff;
        font-weight: 700;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 15px;
        border-bottom: 2px solid var(--neon-cyan);
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
        position: sticky;
        top: 0;
        z-index: 10;
    }

    /* Table Cell Styling - Original Styling */
    .stDataFrame tbody td {
        background: rgba(20, 20, 20, 0.8);
        color: #e0e0e0;
        padding: 12px 15px;
        border-bottom: 1px solid rgba(0, 255, 255, 0.1);
        transition: all 0.3s ease;
    }

    .stDataFrame tbody tr:hover td {
        background: linear-gradient(90deg, rgba(0, 255, 255, 0.1), rgba(255, 0, 255, 0.1));
        color: #ffffff;
        transform: scale(1.01);
    }

    /* Table Row Hover Effect - Original Styling */
    .stDataFrame tbody tr {
        transition: all 0.3s ease;
    }

    .stDataFrame tbody tr:hover {
        background: linear-gradient(90deg, rgba(0, 255, 255, 0.15), rgba(255, 0, 255, 0.15));
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);
    }

    /* Numeric Column Styling */
    .stDataFrame tbody td.numeric {
        color: var(--neon-cyan);
        font-weight: 600;
        text-shadow: 0 0 5px rgba(0, 255, 255, 0.3);
    }

    /* Positive Value Styling */
    .stDataFrame tbody td.positive {
        color: var(--neon-green);
        font-weight: 600;
        text-shadow: 0 0 5px rgba(0, 255, 0, 0.3);
    }

    /* Negative Value Styling */
    .stDataFrame tbody td.negative {
        color: var(--neon-red);
        font-weight: 600;
        text-shadow: 0 0 5px rgba(255, 0, 102, 0.3);
    }

    /* Table Scrollbar */
    .stDataFrame::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }

    .stDataFrame::-webkit-scrollbar-track {
        background: #0a0a0a;
        border-radius: 10px;
    }

    .stDataFrame::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--neon-cyan), var(--neon-pink));
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
    }

    .stDataFrame::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, var(--neon-pink), var(--neon-purple));
        box-shadow: 0 0 15px rgba(255, 0, 255, 0.7);
    }

    /* Table Empty State */
    .stDataFrame:empty::before {
        content: "No data available";
        color: var(--text-muted);
        font-style: italic;
        text-align: center;
        padding: 2rem;
    }

    /* Table Pagination */
    .stDataFrame [data-testid="stHorizontalBlock"] {
        border-top: 2px solid var(--neon-cyan);
        padding-top: 1rem;
        margin-top: 1rem;
    }

    .stDataFrame button {
        background: linear-gradient(135deg, var(--neon-cyan), var(--neon-purple));
        border: none;
        border-radius: 8px;
        color: #ffffff;
        font-weight: 600;
        padding: 8px 16px;
        transition: all 0.3s ease;
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
    }

    .stDataFrame button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
    }

    /* Table Search Input */
    .stDataFrame input {
        background: rgba(20, 20, 20, 0.8);
        border: 1px solid var(--neon-cyan);
        border-radius: 8px;
        color: #ffffff;
        padding: 8px 12px;
        transition: all 0.3s ease;
    }

    .stDataFrame input:focus {
        outline: none;
        border-color: var(--neon-pink);
        box-shadow: 0 0 15px rgba(255, 0, 255, 0.4);
    }

    /* Table Selection */
    .stDataFrame [role="checkbox"] {
        accent-color: var(--neon-cyan);
    }

    /* Table Sort Icons */
    .stDataFrame .sort-icon {
        color: var(--neon-cyan);
        filter: drop-shadow(0 0 5px rgba(0, 255, 255, 0.5));
    }

    /* Table Filter Icons */
    .stDataFrame .filter-icon {
        color: var(--neon-purple);
        filter: drop-shadow(0 0 5px rgba(153, 0, 255, 0.5));
    }

    /* Advanced Table Animations */
    @keyframes tableRowGlow {
        0%, 100% {
            background: rgba(20, 20, 20, 0.8);
        }
        50% {
            background: linear-gradient(90deg, rgba(0, 255, 255, 0.1), rgba(255, 0, 255, 0.1));
        }
    }

    .stDataFrame tbody tr:nth-child(even) {
        animation: tableRowGlow 4s ease-in-out infinite;
    }

    .stDataFrame tbody tr:nth-child(odd) {
        animation: tableRowGlow 4s ease-in-out infinite 2s;
    }

    /* Table Status Indicators */
    .table-status {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .table-status-success {
        background: rgba(0, 255, 0, 0.1);
        color: var(--neon-green);
        border: 1px solid var(--neon-green);
        box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
    }

    .table-status-warning {
        background: rgba(255, 102, 0, 0.1);
        color: var(--neon-orange);
        border: 1px solid var(--neon-orange);
        box-shadow: 0 0 10px rgba(255, 102, 0, 0.3);
    }

    .table-status-error {
        background: rgba(255, 0, 102, 0.1);
        color: var(--neon-red);
        border: 1px solid var(--neon-red);
        box-shadow: 0 0 10px rgba(255, 0, 102, 0.3);
    }

    .table-status-info {
        background: rgba(0, 102, 255, 0.1);
        color: var(--neon-blue);
        border: 1px solid var(--neon-blue);
        box-shadow: 0 0 10px rgba(0, 102, 255, 0.3);
    }

    /* Neon Table Container - Original Styling */
    .neon-table-container {
        background: linear-gradient(135deg, #141414, #1e1e1e);
        border-radius: 20px;
        padding: 20px;
        border: 3px solid var(--neon-cyan);
        animation: tableFadeIn 0.8s ease-out;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5), 0 0 30px var(--neon-cyan);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .neon-table-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 60px var(--neon-cyan), 0 0 50px var(--neon-pink);
        border-color: var(--neon-pink);
    }

    /* Table Cell Highlight */
    .stDataFrame tbody td.highlight {
        background: linear-gradient(90deg, rgba(0, 255, 255, 0.2), rgba(255, 0, 255, 0.2));
        color: #ffffff;
        font-weight: 700;
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.4);
    }

    /* Table Frozen Rows - Original Styling */
    .stDataFrame tbody tr.frozen td {
        background: linear-gradient(135deg, #003333, #004444);
        position: sticky;
        top: 0;
        z-index: 5;
        border-bottom: 2px solid var(--neon-cyan);
    }

    /* Table Conditional Formatting */
    .stDataFrame tbody td.high-value {
        color: var(--neon-green);
        font-weight: 700;
        text-shadow: 0 0 8px rgba(0, 255, 0, 0.5);
        animation: valuePulse 2s ease-in-out infinite;
    }

    .stDataFrame tbody td.low-value {
        color: var(--neon-red);
        font-weight: 700;
        text-shadow: 0 0 8px rgba(255, 0, 102, 0.5);
        animation: valuePulse 2s ease-in-out infinite;
    }

    @keyframes valuePulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.7;
        }
    }

    /* Table Progress Bars */
    .table-progress {
        width: 100%;
        height: 8px;
        background: rgba(20, 20, 20, 0.8);
        border-radius: 4px;
        overflow: hidden;
    }

    .table-progress-bar {
        height: 100%;
        background: linear-gradient(90deg, var(--neon-cyan), var(--neon-pink));
        border-radius: 4px;
        animation: progressGlow 2s ease-in-out infinite;
    }

    @keyframes progressGlow {
        0%, 100% {
            box-shadow: 0 0 5px rgba(0, 255, 255, 0.5);
        }
        50% {
            box-shadow: 0 0 15px rgba(255, 0, 255, 0.7);
        }
    }

    /* Table Sparklines */
    .table-sparkline {
        width: 100px;
        height: 30px;
        background: linear-gradient(90deg, rgba(0, 255, 255, 0.1), rgba(255, 0, 255, 0.1));
        border-radius: 4px;
        border: 1px solid var(--neon-cyan);
    }

    /* Table Tooltip */
    .stDataFrame [title] {
        position: relative;
        cursor: help;
    }

    .stDataFrame [title]:hover::after {
        content: attr(title);
        position: absolute;
        background: rgba(20, 20, 20, 0.95);
        color: #ffffff;
        padding: 8px 12px;
        border-radius: 8px;
        border: 1px solid var(--neon-cyan);
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.4);
        font-size: 0.85rem;
        z-index: 1000;
        white-space: nowrap;
    }

    /* Table Export Options */
    .table-export {
        display: flex;
        gap: 10px;
        margin-top: 1rem;
    }

    .table-export button {
        background: linear-gradient(135deg, var(--neon-cyan), var(--neon-purple));
        border: none;
        border-radius: 8px;
        color: #ffffff;
        font-weight: 600;
        padding: 8px 16px;
        transition: all 0.3s ease;
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
    }

    .table-export button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
    }

    /* Table Loading State */
    .table-loading {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        color: var(--text-muted);
    }

    .table-loading::before {
        content: '';
        width: 30px;
        height: 30px;
        border: 3px solid var(--neon-cyan);
        border-top-color: transparent;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-right: 10px;
    }

    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }

    /* Table Empty State */
    .table-empty {
        text-align: center;
        padding: 3rem;
        color: var(--text-muted);
    }

    .table-empty::before {
        content: '📊';
        font-size: 3rem;
        display: block;
        margin-bottom: 1rem;
        animation: iconPulse 2s ease-in-out infinite;
    }

    /* Main content area - Enhanced with live glow */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background: linear-gradient(135deg, rgba(10, 10, 10, 0.95), rgba(26, 26, 26, 0.95));
        backdrop-filter: blur(25px);
        border-radius: 20px;
        border: 2px solid rgba(0, 255, 255, 0.3);
        box-shadow: 0 0 40px rgba(0, 0, 0, 0.8), 0 0 20px rgba(0, 255, 255, 0.2);
        animation: containerGlow 5s ease-in-out infinite;
    }

    @keyframes containerGlow {
        0%, 100% {
            border-color: rgba(0, 255, 255, 0.3);
            box-shadow: 0 0 40px rgba(0, 0, 0, 0.8), 0 0 20px rgba(0, 255, 255, 0.2);
        }
        50% {
            border-color: rgba(0, 255, 255, 0.5);
            box-shadow: 0 0 40px rgba(0, 0, 0, 0.8), 0 0 30px rgba(0, 255, 255, 0.3);
        }
    }

    /* Content Sections Background */
    .stMarkdown, .stColumns, .stExpander {
        background: transparent;
    }

    /* Section Dividers */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--neon-cyan), transparent);
        margin: 2rem 0;
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
    }

    /* Form Elements Background - Exact from E-Commerce Platform */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stDateInput > div > div > input {
        background: var(--card-bg);
        border: 1px solid rgba(79, 70, 229, 0.4);
        border-radius: 12px;
        color: var(--text-primary);
    }

    /* Expander Background - Exact from E-Commerce Platform */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.15), rgba(124, 58, 237, 0.1));
        border: 1px solid rgba(79, 70, 229, 0.4);
        border-radius: 12px;
        padding: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-weight: 700;
    }

    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.25), rgba(124, 58, 237, 0.2));
        transform: translateX(5px);
        box-shadow: 0 0 20px rgba(79, 70, 229, 0.3);
    }

    /* Info Box Background - Exact from E-Commerce Platform */
    .stAlert {
        background: rgba(79, 70, 229, 0.1);
        border: 1px solid rgba(79, 70, 229, 0.3);
        border-radius: 16px;
        backdrop-filter: blur(15px);
    }

    /* Progress Bar Background - Exact from E-Commerce Platform */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--primary-indigo), var(--primary-violet), var(--accent-blue));
        border-radius: 10px;
    }

    /* Chart Background - Exact from E-Commerce Platform */
    .js-plotly-plot {
        background: rgba(26, 26, 46, 0.8);
        border-radius: 16px;
        border: 1px solid var(--neon-cyan);
        box-shadow: 0 0 30px rgba(0, 255, 255, 0.2);
    }

    /* DataFrame Background - Original Styling */
    .stDataFrame {
        background: var(--card-bg);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid rgba(79, 70, 229, 0.3);
        animation: fadeIn 0.8s ease-out;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }

    .stDataFrame table tbody tr:hover td {
        background: linear-gradient(90deg, rgba(0, 255, 255, 0.1), rgba(255, 0, 255, 0.1));
        color: #ffffff;
        transform: scale(1.01);
    }

    /* Keep neon borders with original styling */
    .stDataFrame {
        border: 1px solid rgba(79, 70, 229, 0.3);
    }

    .stDataFrame table thead tr th {
        border-bottom: 2px solid var(--neon-cyan);
    }

    .stDataFrame table tbody tr td {
        border-bottom: 1px solid rgba(0, 255, 255, 0.1);
    }

    /* Force all text elements to be white */
    .stDataFrame table thead tr th span,
    .stDataFrame table tbody tr td span,
    .stDataFrame table thead tr th div,
    .stDataFrame table tbody tr td div,
    .stDataFrame table thead tr th p,
    .stDataFrame table tbody tr td p,
    .stDataFrame table thead tr th a,
    .stDataFrame table tbody tr td a {
        color: #ffffff !important;
    }

    /* Ensure all text content is white */
    .stDataFrame {
        color: #ffffff !important;
    }

    .stDataFrame table {
        color: #ffffff !important;
    }

    .stDataFrame table thead {
        color: #ffffff !important;
    }

    .stDataFrame table tbody {
        color: #ffffff !important;
    }

    .stDataFrame table thead tr {
        color: #ffffff !important;
    }

    .stDataFrame table tbody tr {
        color: #ffffff !important;
    }

    .stDataFrame table thead tr th {
        color: #ffffff !important;
    }

    .stDataFrame table tbody tr td {
        color: #ffffff !important;
    }

    /* Force text color for all child elements */
    .stDataFrame thead th,
    .stDataFrame tbody td,
    .stDataFrame thead th *,
    .stDataFrame tbody td * {
        color: #ffffff !important;
    }

    /* Additional text color enforcement */
    .stDataFrame span,
    .stDataFrame div,
    .stDataFrame p,
    .stDataFrame a,
    .stDataFrame strong,
    .stDataFrame em,
    .stDataFrame code,
    .stDataFrame pre,
    .stDataFrame mark,
    .stDataFrame small,
    .stDataFrame sub,
    .stDataFrame sup {
        color: #ffffff !important;
    }

    /* Table data styling overrides */
    .stDataFrame .dataframe,
    .stDataFrame .dataframe *,
    .stDataFrame .dataframe tbody,
    .stDataFrame .dataframe tbody *,
    .stDataFrame .dataframe thead,
    /* Remove all forced black background and white text CSS - Restore original styling */
    .stDataFrame .dataframe,
    .stDataFrame .dataframe thead,
    .stDataFrame .dataframe tbody,
    .stDataFrame .dataframe tr,
    .stDataFrame .dataframe td,
    .stDataFrame .dataframe th {
        background-color: var(--card-bg);
        color: #e0e0e0;
    }

    /* Streamlit table overrides - Original styling */
    [data-testid="stDataFrame"] table,
    [data-testid="stDataFrame"] table tbody,
    [data-testid="stDataFrame"] table thead,
    [data-testid="stDataFrame"] table tr,
    [data-testid="stDataFrame"] table td,
    [data-testid="stDataFrame"] table th {
        background-color: var(--card-bg);
        color: #e0e0e0;
    }

    /* Remove visibility and opacity overrides */
    [data-testid="stDataFrame"] * {
        visibility: visible;
        opacity: 1;
    }

    [data-testid="stDataFrame"] {
        visibility: visible;
        opacity: 1;
    }

    [data-testid="stDataFrame"] table {
        color: #ffffff !important;
    }

    [data-testid="stDataFrame"] tbody {
        color: #ffffff !important;
    }

    [data-testid="stDataFrame"] thead {
        color: #ffffff !important;
    }

    [data-testid="stDataFrame"] tr {
        color: #ffffff !important;
    }

    [data-testid="stDataFrame"] td {
        color: #ffffff !important;
    }

    [data-testid="stDataFrame"] th {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# Navigation title
st.sidebar.markdown("""
<div style="text-align: center; margin-bottom: 1rem;">
    <h1 style="font-size: 2.8rem; font-weight: 800; color: #ffffff; text-shadow: 0 0 40px rgba(0, 255, 255, 0.5);">🏦 Banking Analytics</h1>
    <h2 style="font-size: 0.9rem; color: #82909D; font-weight: 500; text-align: center; margin-bottom: 1.5rem; text-transform: uppercase; letter-spacing: 1px;">Navigation</h2>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("### Select Analytics Page")

# Navigation items with icons
navigation_options = [
    ("🏠 Home"),
    ("📊 Executive Overview"),
    ("👤 Customer 360"),
    ("💰 Profitability"),
    ("🔒 Risk"),
    ("👥 Segmentation"),
    ("🔄 Churn"),
    ("💳 Transactions"),
    ("📦 Products"),
    ("🧠 Decision Intelligence"),
    ("🤖 Model Monitoring"),
    ("✅ Data Quality"),
    ("📡 Live Monitor"),
]

# Create custom radio button with icons
page = st.sidebar.radio(
    "Select Analytics Page",
    navigation_options,
    label_visibility="collapsed",
    key="navigation_radio"
)

# Remove icons from page name for routing
page_clean = page.split(" ", 1)[1] if " " in page else page

# Data Status Section with advanced styling
st.sidebar.markdown("""
<div style="background: linear-gradient(135deg, rgba(0, 255, 156, 0.05) 0%, rgba(15, 23, 42, 0.8) 100%); border: 1px solid rgba(0, 255, 156, 0.2); border-radius: 0.75rem; padding: 1rem; margin-top: 1.5rem; animation: pulse-glow 2s ease-in-out infinite;">
    <div style="color: #00FF9C; font-weight: 600; font-size: 0.9rem; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 1px;">Data Status</div>
    <div style="display: flex; align-items: center; gap: 0.5rem; color: #82909D; font-size: 0.85rem;">
        <div style="width: 8px; height: 8px; background: #00FF9C; border-radius: 50%; box-shadow: 0 0 10px rgba(0, 255, 156, 0.5); animation: pulse 2s ease-in-out infinite;"></div>
        <span>Loaded 8 datasets</span>
    </div>
    <div style="margin-top: 0.5rem; font-size: 0.75rem; color: #64748B;">
        <div>• Customers (1,000)</div>
        <div>• Transactions (10,000)</div>
        <div>• Customer Metrics (1,000)</div>
        <div>• Risk Data (1,000)</div>
        <div>• Product Data (5)</div>
        <div>• Churn Predictions (1,000)</div>
        <div>• Segmentation Data (1,000)</div>
        <div>• Executive Metrics</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Page routing
if page_clean == "Home":
    home.render()
elif page_clean == "Executive Overview":
    executive_overview.render()
elif page_clean == "Customer 360":
    customer_360.render()
elif page_clean == "Profitability":
    profitability.render()
elif page_clean == "Risk":
    risk.render()
elif page_clean == "Segmentation":
    segmentation.render()
elif page_clean == "Churn":
    churn.render()
elif page_clean == "Transactions":
    transactions.render()
elif page_clean == "Products":
    products.render()
elif page_clean == "Decision Intelligence":
    decision_intelligence.render()
elif page_clean == "Model Monitoring":
    model_monitoring.render()
elif page_clean == "Data Quality":
    data_quality.render()
elif page_clean == "Live Monitor":
    live_monitor.render()
