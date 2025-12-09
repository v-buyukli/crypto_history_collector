"""Streamlit UI for Crypto History Collector."""

from pathlib import Path

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


# Load custom CSS from external file
def load_css():
    """Load custom CSS from .streamlit/custom.css file."""
    css_file = Path(__file__).parent.parent.parent / ".streamlit" / "custom.css"
    if css_file.exists():
        css_content = css_file.read_text(encoding="utf-8")
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


load_css()


# Helper functions for rendering cards
def render_feature_card(icon: str, title: str, description: str) -> None:
    """Render a feature card with icon, title and description."""
    st.markdown(
        f"""
        <div class="feature-card">
            <div class="feature-icon">{icon}</div>
            <div class="feature-title">{title}</div>
            <div class="feature-desc">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_exchange_card(name: str, logo_url: str) -> None:
    """Render an exchange card with logo and name."""
    st.markdown(
        f"""
        <div class="exchange-card">
            <img src="{logo_url}" width="80" alt="{name}">
            <div class="exchange-name">{name}</div>
        </div>
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
        <div style='display:flex; align-items:center; gap:10px; justify-content:flex-end;
                    margin-top: 30px;'>
            <span style='width:10px; height:10px; background:#10b981;
                         border-radius:50%; display:inline-block;'></span>
            <span style='font-size: 16px; font-weight: 500;'>Online</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# Hero section
st.markdown("# Historical Cryptocurrency Exchange Data Collection")
st.markdown("#### Tool for collecting historical data from cryptocurrency exchanges")

st.write("")  # Spacer

# Features section with improved cards
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    render_feature_card(
        icon="📊",
        title="Historical OHLC Collection",
        description="Collect OHLC candlestick data with volume from cryptocurrency exchanges",
    )

with col2:
    render_feature_card(
        icon="⏱️",
        title="Multiple Timeframes",
        description="Support for various timeframes: 1h, 4h, 1d",
    )

with col3:
    render_feature_card(
        icon="🔌",
        title="RESTful API",
        description="Access collected historical data through a simple REST API",
    )

st.write("")
st.write("")  # Double spacer

# Exchanges section with improved cards
st.markdown("### Supported Exchanges")

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    render_exchange_card(
        name="Binance", logo_url=f"{FASTAPI_URL}/static/images/binance.svg"
    )

with col2:
    render_exchange_card(
        name="Bybit", logo_url=f"{FASTAPI_URL}/static/images/bybit.svg"
    )

with col3:
    render_exchange_card(name="OKX", logo_url=f"{FASTAPI_URL}/static/images/okx.svg")

st.write("")
st.write("")  # Double spacer

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center;'><p style='color: #94a3b8; margin-top: 10px;'>"
    "© 2025 Crypto History Collector v0.1.0</p></div>",
    unsafe_allow_html=True,
)
