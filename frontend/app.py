"""
FinLens 2.0 — AI Bank Statement Intelligence
Team Ignite | 100% Offline | Llama 3 + Moondream
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinLens 2.0 — AI Financial Intelligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── SESSION STATE ──────────────────────────────────────────────────────────────
_defaults = {
    "analyzed": False,
    "theme": "Light",          # ← Opens in Light Mode by default
    "transactions": None,
    "summary": {},
    "narrative": "",
    "history": [],
    "chat_messages": [],
    "lang": "English",
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ── TRANSLATIONS ───────────────────────────────────────────────────────────────
LANG = {
    "English": {
        "hero_sub":   "Bank Statement Intelligence Platform",
        "hero_desc":  "Upload any bank statement—PDF, Excel, or CSV—and get instant AI-powered analysis: categorized transactions, spending patterns, anomaly detection, tax summaries, and a smart AI assistant.",
        "stat_banks": "BANKS SUPPORTED",
        "stat_acc":   "PARSE ACCURACY",
        "stat_ai":    "AI ANOMALY DETECTION",
        "upload_lbl": "UPLOAD STATEMENT",
        "analyze":    "🚀 Analyze My Statement",
        "clear":      "🗑️ Clear",
        "lang_lbl":   "CHOOSE LANGUAGE",
        "new":        "➕ New Analysis",
        "no_hist":    "No statements analyzed yet.",
        "no_chat":    "No chat yet. Ask AI something!",
        "tab_dash":   "📊 Dashboard",
        "tab_txn":    "📋 Transactions",
        "tab_alert":  "🚨 Alerts",
        "tab_tax":    "📑 Tax & GST",
        "tab_ai":     "💬 Ask AI",
        "tab_loan":   "🏦 Loan Check",
    },
    "తెలుగు": {
        "hero_sub":   "బ్యాంక్ స్టేట్మెంట్ ఇంటెలిజెన్స్",
        "hero_desc":  "మీ బ్యాంక్ స్టేట్మెంట్లను అప్లోడ్ చేయండి మరియు తక్షణ AI విశ్లేషణ పొందండి.",
        "stat_banks": "బ్యాంకులు",
        "stat_acc":   "ఖచ్చితత్వం",
        "stat_ai":    "AI అనోమలీ",
        "upload_lbl": "స్టేట్మెంట్ అప్లోడ్",
        "analyze":    "🚀 విశ్లేషించు",
        "clear":      "🗑️ తొలగించు",
        "lang_lbl":   "భాష ఎంచుకోండి",
        "new":        "➕ కొత్త విశ్లేషణ",
        "no_hist":    "స్టేట్మెంట్లు లేవు.",
        "no_chat":    "చాట్ లేదు.",
        "tab_dash":   "📊 డ్యాష్బోర్డ్",
        "tab_txn":    "📋 లావాదేవీలు",
        "tab_alert":  "🚨 హెచ్చరికలు",
        "tab_tax":    "📑 పన్ను & GST",
        "tab_ai":     "💬 AI అడగండి",
        "tab_loan":   "🏦 లోన్ చెక్",
    },
    "हिंदी": {
        "hero_sub":   "बैंक स्टेटमेंट इंटेलिजेंस प्लेटफॉर्म",
        "hero_desc":  "कोई भी बैंक स्टेटमेंट अपलोड करें और तुरंत AI विश्लेषण प्राप्त करें।",
        "stat_banks": "बैंक",
        "stat_acc":   "सटीकता",
        "stat_ai":    "AI अनोमली",
        "upload_lbl": "स्टेटमेंट अपलोड",
        "analyze":    "🚀 विश्लेषण करें",
        "clear":      "🗑️ साफ़ करें",
        "lang_lbl":   "भाषा चुनें",
        "new":        "➕ नया विश्लेषण",
        "no_hist":    "कोई स्टेटमेंट नहीं।",
        "no_chat":    "कोई चैट नहीं।",
        "tab_dash":   "📊 सारांश",
        "tab_txn":    "📋 लेनदेन",
        "tab_alert":  "🚨 अलर्ट",
        "tab_tax":    "📑 कर & GST",
        "tab_ai":     "💬 AI से पूछें",
        "tab_loan":   "🏦 लोन चेक",
    },
}

# ── THEME PALETTES ─────────────────────────────────────────────────────────────
_DARK = {
    "bg_base":    "#0B0E1A",
    "bg_card":    "#13162A",
    "bg_sidebar": "#1A1D2E",
    "border":     "#2A2150",
    "text_pri":   "#EBE4FF",
    "text_muted": "#A094CC",
    "purple":     "#7353F6",
}
_LIGHT = {
    "bg_base":    "#F3F1FF",
    "bg_card":    "#FFFFFF",
    "bg_sidebar": "#EAE6FF",
    "border":     "#D4CDF5",
    "text_pri":   "#1A1060",
    "text_muted": "#6650B4",
    "purple":     "#5B3FD9",
}

IS_DARK = st.session_state.theme == "Dark"
TH = _DARK if IS_DARK else _LIGHT
T  = LANG[st.session_state.lang]

# Chart palette (vivid, works in both themes)
CHART_PALETTE = ["#7353F6", "#22C55E", "#F43F5E", "#FFB800",
                 "#38BDF8", "#A855F7", "#FB923C", "#6EE7B7"]
CHART_BG   = "rgba(0,0,0,0)"
AXIS_COLOR = "#A094CC" if IS_DARK else "#6650B4"
GRID_COLOR = "rgba(255,255,255,0.06)" if IS_DARK else "rgba(0,0,0,0.05)"
FONT_COLOR = TH["text_pri"]

# ── MASTER CSS ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Montserrat:wght@300;400;500;600;700;800&display=swap');

:root {{
  --bg-base:    {TH['bg_base']};
  --bg-card:    {TH['bg_card']};
  --bg-sidebar: {TH['bg_sidebar']};
  --border:     {TH['border']};
  --text-pri:   {TH['text_pri']};
  --text-muted: {TH['text_muted']};
  --purple:     {TH['purple']};
  --sh-sm: {"0 2px 10px rgba(0,0,0,0.30)" if IS_DARK else "0 2px 12px rgba(91,63,217,0.10)"};
  --sh-md: {"0 8px 32px rgba(0,0,0,0.40)" if IS_DARK else "0 8px 28px rgba(91,63,217,0.15)"};
  --sh-lg: {"0 16px 48px rgba(0,0,0,0.50)" if IS_DARK else "0 16px 48px rgba(91,63,217,0.18)"};
}}

/* ── Reset & Base ── */
*, *::before, *::after {{ box-sizing: border-box; }}
html, body {{ margin:0; padding:0; }}
.stApp {{
  background: {"#0B0E1A" if IS_DARK else "linear-gradient(150deg,#F3F1FF 0%,#EAE6FF 45%,#F0EEFF 100%)"} !important;
  font-family: 'Montserrat', sans-serif !important;
  color: var(--text-pri) !important;
}}

/* Force contrast in light mode */
h1,h2,h3,h4,h5,h6 {{
  color: var(--text-pri) !important;
  font-family: 'Montserrat', sans-serif !important;
  font-weight: 700 !important;
}}
p, li, span {{ color: var(--text-pri) !important; }}
label {{ color: var(--text-pri) !important; }}
.stMarkdown p, .stMarkdown div, .stMarkdown span {{ color: var(--text-pri) !important; }}
[data-testid="stMain"] > div {{ background: transparent !important; }}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
  background: {"linear-gradient(180deg,#1A1D2E,#0F1120)" if IS_DARK else "linear-gradient(180deg,#EAE6FF,#DDD7FF)"} !important;
  border-right: 2px solid var(--purple) !important;
}}
[data-testid="stSidebar"] * {{ color: var(--text-pri) !important; }}
[data-testid="stSidebar"] .stButton > button {{
  background: {"rgba(115,83,246,0.15)" if IS_DARK else "rgba(91,63,217,0.12)"} !important;
  color: var(--purple) !important;
  border: 1px solid var(--purple) !important;
  box-shadow: none !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
  background: var(--purple) !important;
  color: #fff !important;
}}

.sidebar-logo {{
  font-family: 'Bebas Neue', sans-serif !important;
  font-size: 2.4rem; color: var(--purple) !important;
  letter-spacing: 0.08em; line-height: 1; margin-bottom: 2px;
}}
.sidebar-tag {{
  font-size: 0.6rem; font-weight: 800; color: var(--text-muted) !important;
  text-transform: uppercase; letter-spacing: 0.2em;
  padding-bottom: 14px; border-bottom: 1px solid var(--border); margin-bottom: 16px;
}}
.sidebar-sec {{
  font-size: 0.62rem; font-weight: 800; color: var(--text-muted) !important;
  text-transform: uppercase; letter-spacing: 0.18em;
  padding-bottom: 6px; border-bottom: 1px solid var(--border); margin: 14px 0 10px;
}}
.hist-card {{
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 12px; padding: 11px 13px; margin-bottom: 8px;
  box-shadow: var(--sh-sm); transition: all 0.2s;
}}
.hist-card:hover {{ border-color: var(--purple); transform: translateX(3px); }}
.hist-bank {{ font-size: 0.82rem; font-weight: 700; color: var(--text-pri) !important; }}
.hist-badge {{
  display: inline-block;
  background: {"rgba(115,83,246,0.18)" if IS_DARK else "rgba(91,63,217,0.10)"};
  border-radius: 6px; padding: 2px 8px; margin-top: 5px;
  font-size: 0.63rem; font-weight: 700; color: var(--purple) !important;
}}

/* ── Hero ── */
.hero-title {{
  font-family: 'Bebas Neue', sans-serif !important;
  font-size: 5.5rem; color: var(--text-pri) !important;
  line-height: 0.87; letter-spacing: -1px; margin-bottom: 14px;
  {"text-shadow: 0 0 60px rgba(115,83,246,0.4);" if IS_DARK else ""}
}}
.hero-sub {{
  font-size: 0.95rem; font-weight: 700;
  color: var(--purple) !important; margin-bottom: 12px; letter-spacing: 0.02em;
}}
.hero-desc {{
  font-size: 0.87rem; color: var(--text-muted) !important;
  line-height: 1.8; margin-bottom: 28px; max-width: 96%;
}}
.stat-row {{ display: flex; gap: 12px; }}
.stat-box {{
  flex: 1; background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 16px; padding: 16px 12px; text-align: center;
  box-shadow: var(--sh-sm); transition: all 0.25s;
  {"" if IS_DARK else "border-top: 3px solid var(--purple);"}
}}
.stat-box:hover {{ box-shadow: var(--sh-md); transform: translateY(-4px); }}
.stat-num {{
  font-family: 'Bebas Neue', sans-serif !important;
  font-size: 2.1rem; line-height:1;
  color: {"var(--text-pri)" if IS_DARK else "var(--purple)"} !important;
}}
.stat-lbl {{
  font-size: 0.56rem; font-weight: 800; letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--text-muted) !important; margin-top: 5px;
}}

/* ── Control Panel ── */
.ctrl-panel {{
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 24px; padding: 26px 22px; box-shadow: var(--sh-lg);
  {"" if IS_DARK else "border-left: 4px solid var(--purple);"}
}}
.panel-lbl {{
  font-size: 0.64rem; font-weight: 800; color: var(--purple) !important;
  text-transform: uppercase; letter-spacing: 0.18em; margin-bottom: 10px;
}}
.fmt-row {{ display: flex; gap: 6px; margin-bottom: 12px; flex-wrap: wrap; }}
.fmt-tag {{
  background: {"rgba(115,83,246,0.14)" if IS_DARK else "rgba(91,63,217,0.08)"};
  border: 1px solid {"rgba(115,83,246,0.3)" if IS_DARK else "rgba(91,63,217,0.2)"};
  border-radius: 8px; padding: 4px 10px;
  font-size: 0.67rem; font-weight: 700; color: var(--purple) !important;
}}

/* ── File Uploader — Full override ── */
[data-testid="stFileUploadDropzone"],
[data-testid="stFileUploadDropzone"] > div,
section[data-testid="stFileUploadDropzone"] {{
  background: {"rgba(115,83,246,0.05)" if IS_DARK else "#FFFFFF"} !important;
  border: 2px dashed var(--purple) !important;
  border-radius: 16px !important;
}}
[data-testid="stFileUploadDropzone"] * {{
  color: var(--text-pri) !important;
  background: transparent !important;
}}
[data-testid="stFileUploadDropzone"] small {{
  color: var(--text-muted) !important;
}}
/* Browse Files button inside uploader */
[data-testid="stFileUploadDropzone"] button {{
  background: var(--purple) !important;
  color: #ffffff !important;
  border: none !important;
  border-radius: 8px !important;
  font-weight: 700 !important;
}}
[data-testid="stFileUploaderFile"],
[data-testid="stFileUploaderFile"] > div {{
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
}}
[data-testid="stFileUploaderFile"] * {{ color: var(--text-pri) !important; }}


/* ── Buttons ── */
.stButton > button {{
  background: linear-gradient(135deg,#5B3FD9,#7353F6,#9B7AFF) !important;
  color: #fff !important; border: none !important;
  border-radius: 12px !important; font-weight: 700 !important;
  font-size: 0.87rem !important; cursor: pointer !important;
  box-shadow: 0 4px 14px rgba(91,63,217,0.38) !important;
  transition: all 0.22s ease !important;
}}
.stButton > button:hover {{
  transform: translateY(-2px) !important;
  box-shadow: 0 10px 28px rgba(91,63,217,0.5) !important;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
  gap: 3px; border-bottom: 2px solid var(--border);
  background: transparent !important;
}}
.stTabs [data-baseweb="tab"] {{
  background: transparent !important; color: var(--text-muted) !important;
  font-weight: 600; font-size: 0.81rem; padding: 11px 18px;
  border-radius: 10px 10px 0 0;
}}
.stTabs [aria-selected="true"] {{
  color: var(--purple) !important; font-weight: 800 !important;
  background: {"rgba(115,83,246,0.12)" if IS_DARK else "rgba(91,63,217,0.07)"} !important;
  border-bottom: 3px solid var(--purple) !important;
}}

/* ── KPI Cards ── */
.kpi-card {{
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 20px; padding: 20px 18px;
  box-shadow: var(--sh-sm); transition: all 0.25s;
  {"" if IS_DARK else "border-top: 3px solid var(--border);"}
}}
.kpi-card:hover {{
  transform: translateY(-5px); border-color: var(--purple);
  box-shadow: var(--sh-md);
  {"" if IS_DARK else "border-top-color: var(--purple);"}
}}
.kpi-lbl {{
  font-size: 0.63rem; font-weight: 800; color: var(--text-muted) !important;
  text-transform: uppercase; letter-spacing: 0.14em; margin-bottom: 9px;
}}
.kpi-val {{
  font-family: 'Bebas Neue', sans-serif !important;
  font-size: 2.4rem; color: var(--text-pri) !important; line-height: 1;
}}

/* ── Section header strip ── */
.sec-hdr {{
  display: flex; align-items: center; gap: 10px;
  margin: 24px 0 16px; padding-left: 14px;
  border-left: 3px solid var(--purple);
  font-size: 0.7rem; font-weight: 800;
  color: var(--text-muted) !important;
  text-transform: uppercase; letter-spacing: 0.16em;
}}

/* ── Dataframe ── */
.stDataFrame {{ border-radius: 14px !important; overflow: hidden; box-shadow: var(--sh-sm); }}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: var(--purple); border-radius: 10px; }}

/* ── Footer ── */
.app-footer {{
  text-align: center; font-size: 0.72rem; color: var(--text-muted) !important;
  margin-top: 60px; padding: 18px 0 10px;
  border-top: 1px solid var(--border);
}}
</style>
""", unsafe_allow_html=True)


# ── HELPERS ───────────────────────────────────────────────────────────────────
def normalize_data(df):
    if df is None: return None
    df = df.copy()
    if "Withdrawal" in df.columns and "Deposit" in df.columns:
        df["Withdrawal"] = pd.to_numeric(df["Withdrawal"], errors="coerce").fillna(0)
        df["Deposit"]    = pd.to_numeric(df["Deposit"],    errors="coerce").fillna(0)
        df["Amount"]     = df["Withdrawal"].where(df["Withdrawal"] > 0, df["Deposit"])
        df["Type"]       = ["DR" if x > 0 else "CR" for x in df["Withdrawal"]]
    return df

def ai_answer(q, ctx):
    try:
        r = requests.post("http://127.0.0.1:8002/chat",
                          json={"prompt": q, "context": ctx}, timeout=90)
        return r.json().get("response", "I'm ready to help with your finances!")
    except requests.exceptions.Timeout:
        return "⏳ Llama 3 is taking too long to respond. It may be busy — please try again in a moment."
    except Exception as e:
        return f"🔌 AI engine is offline. Make sure Ollama is running. Error: {str(e)[:80]}"

def make_chart_layout(height=420, legend_h=True):
    leg = dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
               font=dict(color=FONT_COLOR), bgcolor="rgba(0,0,0,0)") if legend_h else \
          dict(orientation="v", x=1.01, y=0.5,
               font=dict(size=11, color=FONT_COLOR), bgcolor="rgba(0,0,0,0)")
    return dict(
        height=height, margin=dict(t=10, b=20, l=0, r=0),
        paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
        legend=leg, font=dict(color=FONT_COLOR),
        xaxis=dict(color=AXIS_COLOR, gridcolor=GRID_COLOR,
                   tickfont=dict(color=AXIS_COLOR), showgrid=True),
        yaxis=dict(color=AXIS_COLOR, gridcolor=GRID_COLOR,
                   tickfont=dict(color=AXIS_COLOR), showgrid=True),
    )


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="sidebar-logo">FinLens</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-tag">AI Financial Intelligence · v2.0</div>', unsafe_allow_html=True)

    if st.button(T["new"], width='stretch'):
        st.session_state.analyzed = False; st.rerun()

    # Statement History
    st.markdown('<div class="sidebar-sec">📁 Statement History</div>', unsafe_allow_html=True)
    if st.session_state.history:
        for h in reversed(st.session_state.history):
            st.markdown(f"""
            <div class="hist-card">
              <div class="hist-bank">🏦 {h['bank']}</div>
              <span class="hist-badge">📊 {h['txn_count']} txns</span>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="font-size:0.78rem;color:var(--text-muted);padding:8px 0;">{T["no_hist"]}</div>',
                    unsafe_allow_html=True)

    # Chat History
    st.markdown('<div class="sidebar-sec">💬 Chat History</div>', unsafe_allow_html=True)
    if st.session_state.chat_messages:
        for m in st.session_state.chat_messages[-3:]:
            ico = "👤" if m["role"] == "user" else "🤖"
            st.markdown(
                f'<div style="font-size:0.74rem;color:var(--text-muted);padding:3px 0;">'
                f'{ico} {m["content"][:55]}…</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="font-size:0.78rem;color:var(--text-muted);padding:8px 0;">{T["no_chat"]}</div>',
                    unsafe_allow_html=True)

    # Theme toggle
    st.markdown('<div class="sidebar-sec">🎨 Theme</div>', unsafe_allow_html=True)
    tc1, tc2 = st.columns(2)
    if tc1.button("🌑 Dark",  width='stretch'):
        st.session_state.theme = "Dark";  st.rerun()
    if tc2.button("☀️ Light", width='stretch'):
        st.session_state.theme = "Light"; st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# HERO + CONTROL PANEL
# ══════════════════════════════════════════════════════════════════════════════
h1c, h2c = st.columns([1.55, 1], gap="large")

with h1c:
    st.markdown('<div class="hero-title">FINLENS<br>AI EXTRACTOR</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-sub">{T["hero_sub"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-desc">{T["hero_desc"]}</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="stat-row">
      <div class="stat-box"><div class="stat-num">50+</div><div class="stat-lbl">{T["stat_banks"]}</div></div>
      <div class="stat-box"><div class="stat-num">95%</div><div class="stat-lbl">{T["stat_acc"]}</div></div>
      <div class="stat-box"><div class="stat-num">AI</div><div class="stat-lbl">{T["stat_ai"]}</div></div>
    </div>""", unsafe_allow_html=True)

with h2c:
    st.markdown('<div class="ctrl-panel">', unsafe_allow_html=True)
    st.markdown(f'<div class="panel-lbl">📤 {T["upload_lbl"]}</div>', unsafe_allow_html=True)
    st.markdown('<div class="fmt-row"><span class="fmt-tag">📄 PDF</span><span class="fmt-tag">📊 Excel</span>'
                '<span class="fmt-tag">📋 CSV</span><span class="fmt-tag">🖼️ Image</span></div>',
                unsafe_allow_html=True)

    uploaded = st.file_uploader("Drop your bank statement here",
                                type=["pdf", "png", "jpg", "jpeg", "xlsx", "csv"],
                                label_visibility="collapsed")

    st.markdown(f'<div class="panel-lbl" style="margin-top:18px;">🌐 {T["lang_lbl"]}</div>',
                unsafe_allow_html=True)
    lc = st.columns(3)
    for i, (lbl, key) in enumerate([("English","English"),("తెలుగు","తెలుగు"),("हिंदी","हिंदी")]):
        if lc[i].button(lbl, width='stretch',
                        type="primary" if st.session_state.lang == key else "secondary"):
            st.session_state.lang = key; st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    a1, a2 = st.columns(2)
    with a1:
        if st.button(T["analyze"], width='stretch'):
            if not uploaded:
                st.error("Please upload a file first."); st.stop()
            try:
                with st.status("🧠 Analyzing with local AI…", expanded=True) as status:
                    st.write("🔍 Extracting via Llama 3 + Moondream…")
                    files = {"file": (uploaded.name, uploaded.getvalue(), "application/octet-stream")}
                    resp  = requests.post("http://127.0.0.1:8002/extract", files=files, timeout=90)
                    if resp.status_code == 200:
                        r = resp.json()
                        if "error" in r:
                            status.update(label="❌ Analysis Failed!", state="error")
                            st.error(r["error"])
                            if "hint" in r:
                                st.info(r["hint"])
                        else:
                            st.session_state.transactions = normalize_data(pd.DataFrame(r["transactions"]))
                            st.session_state.summary      = r["summary"]
                            st.session_state.narrative    = r.get("narrative", "Analysis complete.")
                            st.session_state.analyzed     = True
                            st.session_state.history.append({
                                "bank":      r.get("summary", {}).get("bank", "Bank"),
                                "txn_count": len(r["transactions"]),
                            })
                            status.update(label="✅ Analysis Complete!", state="complete")
                            st.rerun()
                    else:
                        st.error(f"Backend error {resp.status_code}")
            except Exception as e:
                st.error(f"Engine unreachable. Run api.py on Port 8002.\n{e}")
    with a2:
        if st.button(T["clear"], width='stretch'):
            st.session_state.analyzed = False; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# RESULTS DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.analyzed:
    df = st.session_state.transactions
    s  = st.session_state.summary

    # ── SECTION 1: KPI ROW ────────────────────────────────────────────────────
    st.markdown('<div class="sec-hdr">📌 Section 1 · Financial Summary</div>', unsafe_allow_html=True)

    a_count = int(len(df[df["Anomaly"] == "Yes"])) if "Anomaly" in df.columns else 0
    tot_cr  = s.get("total_credit", 0)
    tot_dr  = s.get("total_debit",  0)
    net     = s.get("net_balance",  0)

    kc = st.columns(5)
    kpi_data = [
        ("💰 Total Income",   f"₹{tot_cr:,.0f}",    "#22C55E"),
        ("📉 Total Expenses", f"₹{tot_dr:,.0f}",    "#F43F5E"),
        ("🏦 Savings",        f"₹{net:,.0f}",  TH["text_pri"]),
        ("🚨 Anomalies",      str(a_count),           "#FFB800"),
        ("📋 Transactions",   str(len(df)),   TH["text_pri"]),
    ]
    for col, (lbl, val, color) in zip(kc, kpi_data):
        col.markdown(
            f'<div class="kpi-card">'
            f'<div class="kpi-lbl">{lbl}</div>'
            f'<div class="kpi-val" style="color:{color};">{val}</div>'
            f'</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── TABS ──────────────────────────────────────────────────────────────────
    tabs = st.tabs([T["tab_dash"], T["tab_txn"], T["tab_alert"],
                    T["tab_tax"], T["tab_ai"], T["tab_loan"]])

    # ── TAB 1: DASHBOARD ──────────────────────────────────────────────────────
    with tabs[0]:
        st.markdown('<div class="sec-hdr">🍩 Section 2 · Spending Charts</div>', unsafe_allow_html=True)

        df_dr   = df[df["Type"] == "DR"] if "Type" in df.columns else df
        cat_col = "CoA" if "CoA" in df_dr.columns else "Description"

        if not df_dr.empty:
            cat_sums = (df_dr.groupby(cat_col)["Amount"]
                        .sum().sort_values(ascending=False).reset_index())
            if len(cat_sums) > 7:
                top  = cat_sums.iloc[:6].copy()
                rest = pd.DataFrame([{cat_col: "Others", "Amount": cat_sums.iloc[6:]["Amount"].sum()}])
                cat_sums = pd.concat([top, rest], ignore_index=True)

            g1, g2 = st.columns([1, 1.3])

            with g1:
                st.markdown("##### 🍩 SPEND BY CATEGORY")
                fig_pie = px.pie(cat_sums, values="Amount", names=cat_col,
                                 hole=0.52, color_discrete_sequence=CHART_PALETTE)
                fig_pie.update_traces(
                    textinfo="percent+label", textfont_size=12,
                    textfont_color="#ffffff" if IS_DARK else "#1A1060",
                    pull=[0.04] * len(cat_sums),
                    marker=dict(line=dict(color=TH["bg_base"], width=2)),
                )
                fig_pie.update_layout(
                    height=430, margin=dict(t=10, b=10, l=0, r=110),
                    paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
                    showlegend=True,
                    legend=dict(orientation="v", x=1.01, y=0.5,
                                font=dict(size=11, color=FONT_COLOR),
                                bgcolor="rgba(0,0,0,0)"),
                    font=dict(color=FONT_COLOR),
                )
                st.plotly_chart(fig_pie, width='stretch')

            with g2:
                st.markdown("##### 📈 MONTHLY SPENDING TREND")
                if "Date" in df.columns and "Type" in df.columns:
                    try:
                        tr = df.copy()
                        tr["Date"]  = pd.to_datetime(tr["Date"], errors="coerce")
                        tr          = tr.dropna(subset=["Date"])
                        tr["Month"] = tr["Date"].dt.to_period("M").astype(str)
                        tr_df = tr.groupby(["Month", "Type"])["Amount"].sum().reset_index()

                        fig_line = px.line(tr_df, x="Month", y="Amount", color="Type",
                                           line_shape="spline", markers=True,
                                           color_discrete_map={"CR": "#22C55E", "DR": "#7353F6"})
                        fig_line.update_traces(line=dict(width=3), marker=dict(size=7))
                        layout = make_chart_layout(height=430, legend_h=True)
                        layout["xaxis"]["tickangle"] = -30
                        fig_line.update_layout(**layout)
                        st.plotly_chart(fig_line, width='stretch')
                    except Exception as e:
                        st.warning(f"Trend chart error: {e}")
                else:
                    st.info("Date/Type columns not available for trend chart.")

            # AI Narrative
            if st.session_state.narrative:
                st.markdown(
                    f'<div style="background:{"rgba(115,83,246,0.10)" if IS_DARK else "rgba(91,63,217,0.06)"}; '
                    f'padding:20px 24px;border-radius:16px;border:1px solid var(--border);'
                    f'margin-top:20px;font-size:0.87rem;line-height:1.8;color:var(--text-pri);">'
                    f'🤖 <strong>AI Analyst:</strong> {st.session_state.narrative}</div>',
                    unsafe_allow_html=True)
        else:
            st.info("No debit transactions found to chart.")

    # ── TAB 2: TRANSACTIONS ───────────────────────────────────────────────────
    with tabs[1]:
        st.markdown("#### 📋 All Transactions")
        st.dataframe(df, width='stretch', height=560)

    # ── TAB 3: ALERTS ─────────────────────────────────────────────────────────
    with tabs[2]:
        st.markdown("#### 🚨 Anomaly & Alert Report")
        if "Anomaly" in df.columns:
            flagged = df[df["Anomaly"] == "Yes"]
            if flagged.empty:
                st.success("✅ No anomalies detected. Your statement looks clean!")
            else:
                st.error(f"⚠️ {len(flagged)} suspicious transaction(s) flagged by AI.")
                show_cols = [c for c in ["Date","Description","Amount","Reason"] if c in flagged.columns]
                st.dataframe(flagged[show_cols], width='stretch')
        else:
            st.info("Anomaly column not found. Ensure backend pipeline ran completely.")

    # ── TAB 4: TAX & GST ─────────────────────────────────────────────────────
    with tabs[3]:
        st.markdown("#### 📑 Tax & GST Estimate")
        c1, c2, c3 = st.columns(3)
        c1.metric("GST on Income (18%)",     f"₹{tot_cr * 0.18:,.2f}")
        c2.metric("Deductible Expenses (30%)",f"₹{tot_dr * 0.30:,.2f}")
        c3.metric("Net Tax Liability (Est.)", f"₹{max(0, tot_cr*0.18 - tot_dr*0.30):,.2f}")
        st.info("💡 These are estimates. Consult a CA for official filing.")

    # ── TAB 5: ASK AI ─────────────────────────────────────────────────────────
    with tabs[4]:
        st.markdown("#### 💬 Ask Your AI Financial Analyst")
        for m in st.session_state.chat_messages:
            st.chat_message(m["role"]).write(m["content"])
        if q := st.chat_input("Ask anything about your bank statement…"):
            st.session_state.chat_messages.append({"role": "user", "content": q})
            st.chat_message("user").write(q)
            ctx = (f"Income: ₹{tot_cr:,.0f}, Expenses: ₹{tot_dr:,.0f}, "
                   f"Net Balance: ₹{net:,.0f}, Transactions: {len(df)}")
            with st.chat_message("assistant"):
                with st.spinner("🤖 Llama 3 is thinking…"):
                    ans = ai_answer(q, ctx)
                st.write(ans)
            st.session_state.chat_messages.append({"role": "assistant", "content": ans})

    # ── TAB 6: LOAN CHECK ─────────────────────────────────────────────────────
    with tabs[5]:
        st.markdown("#### 🏦 Loan Eligibility Check")
        credit_limit = tot_cr / 3
        score = min(0.92, max(0.15, net / tot_cr)) if tot_cr > 0 else 0.15
        l1, l2, l3 = st.columns(3)
        l1.metric("Estimated Credit Limit",   f"₹{credit_limit:,.0f}")
        l2.metric("Financial Health Score",   f"{score*100:.0f} / 100")
        l3.metric("Monthly Avg Expense",      f"₹{tot_dr / max(len(df), 1) * 30:,.0f}")
        st.progress(float(score))
        if score > 0.5:
            st.success("✅ Strong profile — likely eligible for personal/business loan.")
        else:
            st.warning("⚠️ Low savings ratio — reduce expenses before applying.")

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="app-footer">🏦 FinLens 2.0 · AI-Powered · 100% Private · Built by Team Ignite for SriCity Hackathon</div>',
    unsafe_allow_html=True)
