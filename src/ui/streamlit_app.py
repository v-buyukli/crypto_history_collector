"""Streamlit UI for Crypto History Collector."""

import streamlit as st

from src.config import settings

# Get FastAPI URL from settings
FASTAPI_URL = settings.fastapi_url

# Page configuration
st.set_page_config(
    page_title="Crypto History Collector",
    page_icon="📊",
    layout="wide",
)

# Custom CSS for improved styling
st.markdown(
    """
    <style>
    /* Hide Streamlit header and footer */
    header[data-testid="stHeader"] {
        display: none;
    }
    footer {
        display: none;
    }
    #MainMenu {
        display: none;
    }
    .stDeployButton {
        display: none;
    }

    /* Remove ALL bottom spacing - comprehensive approach */
    .main .block-container {
        padding-bottom: 0 !important;
        padding-top: 2rem !important;
        margin-bottom: 0 !important;
    }

    .main {
        padding-bottom: 0 !important;
        margin-bottom: 0 !important;
    }

    /* Target Streamlit's vertical block containers */
    section[data-testid="stVerticalBlock"] {
        padding-bottom: 0 !important;
        margin-bottom: 0 !important;
    }

    section[data-testid="stVerticalBlock"] > div:last-child {
        padding-bottom: 0 !important;
        margin-bottom: 0 !important;
    }

    /* Remove spacing from last element */
    .element-container:last-child {
        margin-bottom: 0 !important;
    }

    /* Reduce remaining space moderately */
    .stMarkdown:last-of-type {
        margin-bottom: 0 !important;
    }

    /* Feature card styling */
    .feature-card {
        padding: 30px 20px;
        border: 1px solid #334155;
        border-radius: 12px;
        text-align: center;
        min-height: 260px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        background: rgba(30, 41, 59, 0.3);
    }
    .feature-icon {
        font-size: 48px;
        margin-bottom: 16px;
    }
    .feature-title {
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 12px;
        color: #f8fafc;
    }
    .feature-desc {
        font-size: 14px;
        color: #94a3b8;
        line-height: 1.6;
    }

    /* Exchange card styling */
    .exchange-card {
        padding: 24px;
        border: 1px solid #334155;
        border-radius: 12px;
        text-align: center;
        background: rgba(30, 41, 59, 0.3);
    }
    .exchange-card img {
        margin-bottom: 12px;
    }
    .exchange-name {
        font-size: 16px;
        font-weight: 600;
        color: #f8fafc;
    }

    /* Logo styling */
    .logo-container {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .logo-icon {
        width: 40px;
        height: 40px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header: Logo + Title + Status badge
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown(
        """
        <div class="logo-container">
            <svg class="logo-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">
                <circle cx="20" cy="20" r="18" fill="#667eea"/>
                <line x1="12" y1="14" x2="12" y2="17" stroke="white" stroke-width="1.5"/>
                <rect x="10" y="17" width="4" height="8" fill="white" rx="0.5"/>
                <line x1="12" y1="25" x2="12" y2="28" stroke="white" stroke-width="1.5"/>
                <line x1="20" y1="10" x2="20" y2="14" stroke="white" stroke-width="1.5"/>
                <rect x="18" y="14" width="4" height="12" fill="white" rx="0.5"/>
                <line x1="20" y1="26" x2="20" y2="30" stroke="white" stroke-width="1.5"/>
                <line x1="28" y1="16" x2="28" y2="19" stroke="white" stroke-width="1.5"/>
                <rect x="26" y="19" width="4" height="6" fill="white" rx="0.5"/>
                <line x1="28" y1="25" x2="28" y2="27" stroke="white" stroke-width="1.5"/>
            </svg>
            <h2 style="margin: 0;">Crypto History Collector</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        """
        <div style='display:flex; align-items:center; gap:8px; justify-content:flex-end;'>
            <span style='width:8px; height:8px; background:#10b981;
                         border-radius:50%; display:inline-block;'></span>
            <span>Online</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# Hero section
st.markdown("# Historical Cryptocurrency Exchange Data Collection")
st.markdown("#### Tool for collecting historical data from cryptocurrency exchanges")

st.markdown("<br>", unsafe_allow_html=True)

# Features section with improved cards
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Historical OHLC Collection</div>
            <div class="feature-desc">
                Collect OHLC candlestick data with volume from cryptocurrency exchanges
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">⏱️</div>
            <div class="feature-title">Multiple Timeframes</div>
            <div class="feature-desc">
                Support for various timeframes: 1h, 4h, 1d
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">🔌</div>
            <div class="feature-title">RESTful API</div>
            <div class="feature-desc">
                Access collected historical data through a simple REST API
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br><br>", unsafe_allow_html=True)

# Exchanges section with improved cards
st.markdown("### Supported Exchanges")

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown(
        f"""
        <div class="exchange-card">
            <img src="{FASTAPI_URL}/static/images/binance.svg" width="80" alt="Binance">
            <div class="exchange-name">Binance</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="exchange-card">
            <img src="{FASTAPI_URL}/static/images/bybit.svg" width="80" alt="Bybit">
            <div class="exchange-name">Bybit</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="exchange-card">
            <img src="{FASTAPI_URL}/static/images/okx.svg" width="80" alt="OKX">
            <div class="exchange-name">OKX</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br><br>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#94a3b8; margin-top: 10pxJr; margin-bottom: -100px; padding-bottom: 0;'>"  # noqa: E501
    "&copy; 2025 Crypto History Collector v0.1.0</div>",
    unsafe_allow_html=True,
)
