"""
styles.py
=========
CSS compartilhado entre todas as paginas do app Streamlit.
"""

import streamlit as st


SHARED_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="main"] {
        font-family: 'Inter', sans-serif !important;
    }

    /* ======== Sidebar nav links ======== */
    [data-testid="stSidebarNav"] a span {
        color: #D1D5DB !important;
    }

    /* Page header */
    .page-header {
        background: #1E2030;
        border: 1px solid rgba(167,139,250,0.2);
        padding: 1.8rem 2rem;
        border-radius: 14px;
        margin-bottom: 1.5rem;
    }
    .page-header h1 {
        font-size: 1.8rem;
        font-weight: 700;
        color: #FFFFFF !important;
        margin: 0 0 0.3rem 0;
    }
    .page-header p {
        font-size: 0.95rem;
        color: #C0C0C0 !important;
        margin: 0;
    }

    /* Section headers */
    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #5B21B6 !important;
        margin: 1.8rem 0 0.6rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(91,33,182,0.2);
        letter-spacing: -0.3px;
    }

    /* Insight cards */
    .insight-card {
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-left: 4px solid #22C55E;
        padding: 1rem 1.2rem;
        border-radius: 0 10px 10px 0;
        font-size: 0.92rem;
        line-height: 1.7;
        margin: 0.8rem 0 1.5rem;
        color: #1F2937 !important;
    }
    .insight-card strong {
        color: #15803D !important;
    }

    /* Question card */
    .question-card {
        background: #EDE9FE;
        border: 1px solid #C4B5FD;
        padding: 0.7rem 1.1rem;
        border-radius: 8px;
        font-size: 0.9rem;
        color: #3B0764 !important;
        margin-bottom: 1rem;
        font-style: italic;
    }

    /* ======== FIX: Sidebar & filter boxes ======== */
    section[data-testid="stSidebar"] {
        background: #12141D !important;
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #C4B5FD !important;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
    }
    /* Dark filter input boxes */
    section[data-testid="stSidebar"] .stSelectbox > div > div,
    section[data-testid="stSidebar"] .stMultiSelect > div > div,
    section[data-testid="stSidebar"] [data-baseweb="select"] > div,
    section[data-testid="stSidebar"] [data-baseweb="input"] > div {
        background-color: #1A1D29 !important;
        border-color: rgba(167,139,250,0.2) !important;
        color: #E5E7EB !important;
    }
    /* Dark dropdown menus */
    [data-baseweb="popover"] {
        background-color: #1A1D29 !important;
    }
    [data-baseweb="popover"] li {
        color: #E5E7EB !important;
    }
    [data-baseweb="popover"] li:hover {
        background-color: rgba(102,126,234,0.2) !important;
    }
    /* Multiselect tags */
    section[data-testid="stSidebar"] [data-baseweb="tag"] {
        background-color: rgba(108,99,255,0.3) !important;
        color: #E5E7EB !important;
        border: 1px solid rgba(108,99,255,0.4) !important;
    }
    section[data-testid="stSidebar"] [data-baseweb="tag"] span {
        color: #E5E7EB !important;
    }
    /* Filter labels */
    section[data-testid="stSidebar"] label {
        color: #D1D5DB !important;
    }

    /* ======== General input styling ======== */
    .stSlider label, .stSelectbox label, .stMultiSelect label,
    .stRadio label, .stNumberInput label {
        color: #1F2937 !important;
        font-weight: 500;
    }
    .stSelectbox > div > div, .stMultiSelect > div > div {
        background-color: #FAFAFA !important;
        border-color: rgba(108,99,255,0.3) !important;
        color: #1F2937 !important;
    }
    div[data-baseweb="popover"] ul li,
    ul[role="listbox"] li, 
    ul[role="listbox"] li span,
    [data-testid="stVirtualDropdown"] li,
    div[role="listbox"] span {
        color: #1F2937 !important;
    }
    div[role="listbox"] {
        background-color: #FAFAFA !important;
    }

    /* Metric cards */
    .metric-highlight {
        background: #1E2030;
        border: 1px solid rgba(102,126,234,0.2);
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
    }
    .metric-highlight .value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #A78BFA;
    }
    .metric-highlight .label {
        font-size: 0.75rem;
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-top: 0.2rem;
    }

    /* Dividers */
    hr {
        border: none;
        border-top: 1px solid rgba(255,255,255,0.08);
        margin: 1.5rem 0;
    }

    /* Expander */
    .streamlit-expanderHeader {
        color: #E5E7EB !important;
        font-weight: 600;
    }

    /* Glossary table */
    .glossary-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 10px;
        overflow: hidden;
        font-size: 0.88rem;
        background: #FAFAFA;
    }
    .glossary-table th {
        background: #EDE9FE;
        color: #5B21B6;
        padding: 0.7rem 1rem;
        text-align: left;
        font-weight: 600;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .glossary-table td {
        padding: 0.6rem 1rem;
        border-bottom: 1px solid #E5E7EB;
        color: #1F2937;
    }
    .glossary-table tr:last-child td {
        border-bottom: none;
    }
    .glossary-table .sigla {
        font-weight: 700;
        color: #6D28D9;
        white-space: nowrap;
    }

</style>
"""

# Plotly template defaults for dark theme
PLOTLY_LAYOUT = dict(
    template="plotly_white",
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter'),
)

PLOTLY_COLORS = ["#6C63FF", "#A78BFA", "#F093FB", "#F472B6", "#38BDF8", "#34D399"]


def inject_css():
    """Injeta o CSS compartilhado na pagina."""
    st.markdown(SHARED_CSS, unsafe_allow_html=True)


def page_header(title, description=""):
    """Renderiza um header estilizado para a pagina."""
    desc_html = f'<p>{description}</p>' if description else ''
    st.markdown(f"""
    <div class="page-header">
        <h1>{title}</h1>
        {desc_html}
    </div>
    """, unsafe_allow_html=True)


def section_title(text):
    """Renderiza um titulo de secao estilizado."""
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)


def insight_card(text):
    """Renderiza um card de insight estilizado."""
    st.markdown(f'<div class="insight-card">{text}</div>', unsafe_allow_html=True)


def question_card(text):
    """Renderiza a pergunta em formato estilizado."""
    st.markdown(f'<div class="question-card">{text}</div>', unsafe_allow_html=True)
