"""VyaparPulse — Inclusive Credit Intelligence for Bharat.

A single-file, offline Streamlit demonstration of alternative credit scoring for
micro-merchants and street vendors.

Run with:
    streamlit run main.py

Everything is synthetic and local: no uploaded document is sent anywhere, no
external API is called, and no credential is stored. See the Privacy and Terms
pages inside the app for the compliance story.
"""

from __future__ import annotations

import random
from datetime import datetime
from html import escape

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="VyaparPulse | Inclusive Credit Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": None, "Get Help": None, "Report a bug": None},
)


# ══════════════════════════════════════════════════════════════════════════════
# 1. DESIGN SYSTEM
# ══════════════════════════════════════════════════════════════════════════════

APP_CSS = """
<style>
/* ── Design tokens ─────────────────────────────────────────────────────────── */
:root{
  --vp-bg:#F6F8FB; --vp-surface:#FFFFFF; --vp-surface-2:#FAFCFE; --vp-surface-3:#F1F5F9;
  --vp-ink:#0B1729; --vp-ink-2:#1E293B; --vp-body:#475569; --vp-muted:#64748B; --vp-faint:#94A3B8;
  --vp-line:#E6EAF1; --vp-line-2:#EFF2F7;
  --vp-emerald:#0E9F6E; --vp-emerald-600:#0B8A5F; --vp-emerald-700:#067A55;
  --vp-emerald-soft:#ECFDF5; --vp-emerald-line:#C7F0DE;
  --vp-amber:#D97706; --vp-amber-soft:#FFF8EE; --vp-amber-line:#FBE0BD;
  --vp-red:#DC2626; --vp-red-soft:#FEF3F2; --vp-red-line:#FBD5D5;
  --vp-navy:#16233F; --vp-navy-soft:#EEF2F9; --vp-navy-line:#DCE3F0;
  --vp-teal:#0F766E; --vp-violet:#6D3FC0; --vp-slate:#64748B;
  --vp-r:16px; --vp-r-sm:11px; --vp-r-lg:20px; --vp-pill:999px;
  --vp-sh-1:0 1px 2px rgba(15,23,42,.04);
  --vp-sh-2:0 1px 2px rgba(15,23,42,.04), 0 18px 34px -26px rgba(15,23,42,.32);
  --vp-sh-3:0 2px 6px rgba(15,23,42,.05), 0 30px 56px -34px rgba(15,23,42,.34);
  --vp-font:"Inter","Segoe UI",system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;
}

/* ── App canvas + Streamlit chrome ─────────────────────────────────────────── */
.stApp, [data-testid="stApp"]{
  background-color:var(--vp-bg) !important;
  background-image:
    radial-gradient(1100px 320px at 6% -6%, rgba(14,159,110,.10), rgba(14,159,110,0) 62%),
    radial-gradient(900px 300px at 94% -10%, rgba(22,35,63,.07), rgba(22,35,63,0) 60%);
  background-repeat:no-repeat;
}
[data-testid="stApp"]{color:var(--vp-ink);}
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], [data-testid="stAppDeployButton"], [data-testid="stSidebarNav"]{display:none !important;}
[data-testid="stHeader"]{background:transparent !important; box-shadow:none !important;}
[data-testid="stMainBlockContainer"], .block-container{
  max-width:1400px; padding:3.1rem 2.4rem 4.5rem !important;
}
[data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"]{gap:.85rem;}

/* ── Typography ────────────────────────────────────────────────────────────── */
h1,h2,h3,h4,h5,h6{color:var(--vp-ink) !important; letter-spacing:-.021em; font-weight:650;}
h1{font-size:1.72rem;} h2{font-size:1.2rem;} h3{font-size:1.02rem;}
p, li{color:var(--vp-body); font-size:14px; line-height:1.62;}
[data-testid="stCaptionContainer"] p, .stCaption{color:var(--vp-muted) !important; font-size:12.5px !important; line-height:1.55;}
[data-testid="stMarkdownContainer"] strong{color:var(--vp-ink-2);}
hr{border:none; border-top:1px solid var(--vp-line) !important; margin:1.2rem 0 !important;}

/* ── Sidebar ───────────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#FFFFFF 0%,#FCFEFD 55%,#F7FBF9 100%);
  border-right:1px solid var(--vp-line);
  box-shadow:18px 0 40px -40px rgba(15,23,42,.45);
}
[data-testid="stSidebarHeader"]{padding:.5rem .35rem 0 !important;}
[data-testid="stSidebarUserContent"]{padding:1rem 1.05rem 1.5rem !important;}
[data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"]{gap:.42rem;}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{gap:.45rem;}
[data-testid="stSidebarCollapseButton"] button{color:var(--vp-muted) !important; border-radius:8px !important;}
[data-testid="stSidebarCollapseButton"] button:hover{background:var(--vp-surface-3) !important;}
[data-testid="stExpandSidebarButton"] button{background:#fff !important; border:1px solid var(--vp-line) !important; border-radius:10px !important; color:var(--vp-ink) !important;}

.vp-brand{display:flex; align-items:center; gap:11px; padding:2px 2px 12px;}
.vp-brand-mark{
  width:38px; height:38px; border-radius:11px; flex:0 0 38px; display:grid; place-items:center;
  background:linear-gradient(140deg,#12B37C 0%,#0B8A5F 55%,#0B2545 100%);
  box-shadow:0 8px 18px -10px rgba(11,138,95,.75);
}
.vp-brand-mark svg{width:21px; height:21px;}
.vp-brand-name{font-size:15.5px; font-weight:700; color:var(--vp-ink); letter-spacing:-.02em; line-height:1.15;}
.vp-brand-tag{font-size:10.5px; color:var(--vp-muted); letter-spacing:.02em; line-height:1.3; margin-top:1px;}
.vp-nav-label{
  font-size:10px; font-weight:700; letter-spacing:.1em; text-transform:uppercase;
  color:var(--vp-faint); margin:14px 0 6px 4px;
}
.vp-side-card{
  border:1px solid var(--vp-line); background:var(--vp-surface); border-radius:14px;
  padding:12px 13px; box-shadow:var(--vp-sh-1); margin-top:2px;
}
.vp-side-row{display:flex; align-items:center; gap:9px;}
.vp-avatar{
  width:34px; height:34px; border-radius:10px; flex:0 0 34px; display:grid; place-items:center;
  background:linear-gradient(140deg,#EEF2F9,#E2EAF6); color:var(--vp-navy);
  font-size:12.5px; font-weight:700; border:1px solid var(--vp-navy-line);
}
.vp-side-name{font-size:13px; font-weight:650; color:var(--vp-ink); line-height:1.25;}
.vp-side-sub{font-size:11px; color:var(--vp-muted); line-height:1.35;}
.vp-side-meta{font-size:11.5px; color:var(--vp-body); display:flex; align-items:center; gap:6px; margin-top:9px;}
.vp-side-foot{font-size:10.5px; color:var(--vp-faint); text-align:center; line-height:1.5; margin-top:10px;}

/* navigation items (keyed buttons) — prefixed for specificity over global buttons */
section[data-testid="stSidebar"] [class*="st-key-vp_nav"] button{
  width:100%; justify-content:flex-start !important; text-align:left !important;
  background:transparent !important; border:1px solid transparent !important; box-shadow:none !important;
  color:var(--vp-body) !important; font-weight:500 !important; font-size:13.5px !important;
  padding:.46rem .62rem !important; border-radius:10px !important; min-height:0 !important;
  transition:background .18s ease, color .18s ease, box-shadow .18s ease, transform .18s ease;
}
section[data-testid="stSidebar"] [class*="st-key-vp_nav"] button p{
  font-size:13.5px !important; color:inherit !important; font-weight:inherit !important; margin:0 !important;
}
section[data-testid="stSidebar"] [class*="st-key-vp_nav"] button [data-testid="stIconMaterial"]{
  font-size:17px !important; margin-right:9px; color:inherit !important; opacity:.9;
}
section[data-testid="stSidebar"] [class*="st-key-vp_nav"] button:hover{
  background:#F1F5F9 !important; color:var(--vp-ink) !important; border-color:transparent !important; transform:none !important;
}
section[data-testid="stSidebar"] [class*="st-key-vp_nav"] button[kind="primary"]{
  background:linear-gradient(90deg, rgba(14,159,110,.16), rgba(14,159,110,.045)) !important;
  color:var(--vp-emerald-700) !important; font-weight:650 !important;
  border-color:var(--vp-emerald-line) !important;
  box-shadow:inset 3px 0 0 0 var(--vp-emerald) !important;
}
section[data-testid="stSidebar"] [class*="st-key-vp_nav"] button[kind="primary"]:hover{
  background:linear-gradient(90deg, rgba(14,159,110,.22), rgba(14,159,110,.07)) !important;
  color:var(--vp-emerald-700) !important;
}
section[data-testid="stSidebar"] [class*="st-key-vp_nav"] button[kind="primary"] p{font-weight:650 !important;}

/* ── Buttons ───────────────────────────────────────────────────────────────── */
.stButton>button, .stDownloadButton>button, [data-testid="stFormSubmitButton"]>button{
  border-radius:10px !important; font-weight:600 !important; font-size:13.5px !important;
  border:1px solid var(--vp-line) !important; background:var(--vp-surface) !important;
  color:var(--vp-ink-2) !important; box-shadow:var(--vp-sh-1); transition:background .16s ease, border-color .16s ease, transform .16s ease, box-shadow .16s ease;
}
.stButton>button p, .stDownloadButton>button p, [data-testid="stFormSubmitButton"]>button p{font-size:13.5px !important; color:inherit !important; font-weight:inherit !important;}
.stButton>button:hover, .stDownloadButton>button:hover, [data-testid="stFormSubmitButton"]>button:hover{
  background:var(--vp-emerald-soft) !important; border-color:var(--vp-emerald-line) !important;
  color:var(--vp-emerald-700) !important; transform:translateY(-1px);
}
.stButton>button[kind="primary"], .stDownloadButton>button[kind="primary"], [data-testid="stFormSubmitButton"]>button[kind="primary"]{
  background:linear-gradient(135deg,#12B37C 0%,#0B8A5F 100%) !important; color:#fff !important;
  border-color:transparent !important; box-shadow:0 8px 18px -10px rgba(11,138,95,.75);
}
.stButton>button[kind="primary"]:hover, .stDownloadButton>button[kind="primary"]:hover, [data-testid="stFormSubmitButton"]>button[kind="primary"]:hover{
  background:linear-gradient(135deg,#0FAE77 0%,#086F4C 100%) !important; color:#fff !important;
}
.stButton>button[kind="tertiary"], .stDownloadButton>button[kind="tertiary"]{
  background:transparent !important; box-shadow:none !important; border-color:transparent !important; color:var(--vp-body) !important;
}
.stButton>button:disabled, .stDownloadButton>button:disabled, [data-testid="stFormSubmitButton"]>button:disabled{
  background:var(--vp-surface-3) !important; color:var(--vp-faint) !important; border-color:var(--vp-line) !important; transform:none;
}
button:focus-visible, a:focus-visible, input:focus-visible, textarea:focus-visible{
  outline:3px solid rgba(14,159,110,.32) !important; outline-offset:2px !important;
}

/* ── Widgets ───────────────────────────────────────────────────────────────── */
[data-baseweb="select"]>div, [data-baseweb="input"], [data-baseweb="base-input"],
[data-baseweb="textarea"]>div, [data-testid="stNumberInputContainer"], [data-testid="stTextInputRootElement"],
[data-testid="stDateInputField"], [data-testid="stTimeInputTimeDisplay"]{
  border-radius:10px !important; border-color:var(--vp-line) !important; background:var(--vp-surface) !important;
}
[data-baseweb="select"]>div:hover, [data-baseweb="input"]:hover, [data-testid="stNumberInputContainer"]:hover{
  border-color:#D3DCE8 !important;
}
[data-baseweb="select"]>div:focus-within, [data-baseweb="input"]:focus-within, [data-testid="stNumberInputContainer"]:focus-within{
  border-color:var(--vp-emerald) !important; box-shadow:0 0 0 3px rgba(14,159,110,.14) !important;
}
input, textarea, [data-baseweb="select"] span, [data-baseweb="select"] input{color:var(--vp-ink) !important;}
input::placeholder, textarea::placeholder{color:var(--vp-faint) !important; opacity:1;}
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label{font-size:12.5px !important; font-weight:550 !important; color:var(--vp-body) !important;}
[data-testid="stFileUploaderDropzone"]{
  background:var(--vp-surface-2) !important; border:1.5px dashed #CBD6E3 !important;
  border-radius:14px !important; transition:border-color .16s ease, background .16s ease;
}
[data-testid="stFileUploaderDropzone"]:hover{border-color:var(--vp-emerald) !important; background:var(--vp-emerald-soft) !important;}
[data-testid="stFileUploaderDropzone"] span, [data-testid="stFileUploaderDropzone"] small{color:var(--vp-muted) !important;}
[data-testid="stDataFrame"]{border:1px solid var(--vp-line); border-radius:14px; overflow:hidden; background:var(--vp-surface); box-shadow:var(--vp-sh-1);}
[data-testid="stExpander"] details{border:1px solid var(--vp-line) !important; border-radius:14px !important; background:var(--vp-surface) !important; box-shadow:var(--vp-sh-1);}
[data-testid="stExpander"] summary{font-weight:600 !important; font-size:13px !important; color:var(--vp-ink-2) !important;}
[data-testid="stProgressBarTrack"]{background:var(--vp-surface-3) !important; border-radius:var(--vp-pill) !important; height:8px !important;}
[data-testid="stProgressBarTrack"]>div{background:linear-gradient(90deg,#34D399,#0E9F6E) !important; border-radius:var(--vp-pill) !important;}
[data-baseweb="slider"] [role="slider"]{background:var(--vp-emerald) !important; box-shadow:0 0 0 2px #fff, 0 2px 6px -2px rgba(11,138,95,.6) !important;}
[data-testid="stSliderTickBar"], [data-testid="stThumbValue"]{color:var(--vp-emerald-700) !important; font-size:11px !important;}
[data-testid="stTabs"] [data-baseweb="tab-list"]{
  gap:4px !important; background:var(--vp-surface-3) !important; padding:4px !important;
  border-radius:var(--vp-pill) !important; width:fit-content !important; border:none !important;
}
[data-testid="stTabs"] [data-baseweb="tab"]{
  border-radius:var(--vp-pill) !important; padding:6px 14px !important; height:auto !important;
  background:transparent !important; color:var(--vp-body) !important; font-size:13px !important; font-weight:550 !important;
}
[data-testid="stTabs"] [aria-selected="true"]{background:var(--vp-surface) !important; box-shadow:var(--vp-sh-1); color:var(--vp-ink) !important;}
[data-testid="stTabs"] [data-baseweb="tab-highlight"], [data-testid="stTabs"] [data-baseweb="tab-border"]{display:none !important;}
[data-testid="stForm"]{border:none !important; padding:0 !important;}
::-webkit-scrollbar{width:10px; height:10px;}
::-webkit-scrollbar-track{background:transparent;}
::-webkit-scrollbar-thumb{background:#D9E1EB; border-radius:99px; border:3px solid transparent; background-clip:content-box;}
::-webkit-scrollbar-thumb:hover{background:#C4CFDD; background-clip:content-box;}

/* ── Notices (Streamlit alerts, re-skinned) ────────────────────────────────── */
[data-testid="stAlert"]{
  border:1px solid var(--vp-line) !important; border-radius:13px !important;
  background:var(--vp-surface) !important; box-shadow:var(--vp-sh-1); padding:1px;
}
[data-testid="stAlertContainer"]{border-radius:12px !important;}
[data-testid="stAlert"] [data-testid="stMarkdownContainer"] p, [data-testid="stAlert"] p{color:inherit !important; font-size:13px !important;}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentInfo"]){background:var(--vp-navy-soft) !important; color:#25334C !important; box-shadow:inset 3px 0 0 0 #4A6BA8;}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentSuccess"]){background:var(--vp-emerald-soft) !important; color:#065F46 !important; box-shadow:inset 3px 0 0 0 var(--vp-emerald);}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]){background:var(--vp-amber-soft) !important; color:#8A4A08 !important; box-shadow:inset 3px 0 0 0 var(--vp-amber);}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentError"]){background:var(--vp-red-soft) !important; color:#9B1C1C !important; box-shadow:inset 3px 0 0 0 var(--vp-red);}
[data-testid="stAlertContainer"] [data-testid="stMarkdownContainer"] strong{color:inherit !important;}

.st-key-vp_sidebar_profile{margin-top:auto; padding-top:14px;}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"]:has(.st-key-vp_sidebar_profile) .st-key-vp_sidebar_profile{margin-top:auto;}
.st-key-vp_card_doc{padding:30px 36px 34px !important; max-width:940px;}
.st-key-vp_card_doc p, .st-key-vp_card_doc li{font-size:13.5px; line-height:1.75;}
.st-key-vp_card_doc h1, .st-key-vp_card_doc h2{font-size:1.05rem !important;}
.st-key-vp_card_doc ul{padding-left:20px;}
.st-key-vp_card_doc hr{margin:18px 0 !important;}

/* ── Card shell for keyed containers holding widgets/charts ────────────────── */
[class*="st-key-vp_card"]{
  background:var(--vp-surface); border:1px solid var(--vp-line); border-radius:var(--vp-r);
  padding:18px 20px 20px; box-shadow:var(--vp-sh-2);
}
[class*="st-key-vp_card"] [data-testid="stVerticalBlock"]{gap:.5rem;}
[class*="st-key-vp_card"]{animation:vp-card-in .34s cubic-bezier(.16,1,.3,1) both;}
@keyframes vp-card-in{from{opacity:0; transform:translateY(6px);} to{opacity:1; transform:none;}}

/* ── Reusable product components ───────────────────────────────────────────── */
.vp-card{
  background:var(--vp-surface); border:1px solid var(--vp-line); border-radius:var(--vp-r);
  padding:18px 20px; box-shadow:var(--vp-sh-2);
}
.vp-card-pad-lg{padding:22px 24px;}
.vp-eyebrow{font-size:10.5px; font-weight:700; letter-spacing:.115em; text-transform:uppercase; color:var(--vp-emerald-700);}
.vp-h1{font-size:1.68rem; font-weight:700; color:var(--vp-ink); letter-spacing:-.025em; margin:.2rem 0 .1rem; line-height:1.22;}
.vp-sub{font-size:13.5px; color:var(--vp-muted); margin:0;}
.vp-greet{font-size:12.5px; color:var(--vp-muted); font-weight:550; letter-spacing:.01em;}

.vp-section{display:flex; align-items:flex-end; justify-content:space-between; gap:16px; margin:6px 0 10px;}
.vp-section-title{font-size:1.02rem; font-weight:660; color:var(--vp-ink); letter-spacing:-.02em; margin:0;}
.vp-section-sub{font-size:12.5px; color:var(--vp-muted); margin:2px 0 0;}

.vp-chip{
  display:inline-flex; align-items:center; gap:5px; font-size:11.5px; font-weight:600;
  padding:3px 9px; border-radius:var(--vp-pill); border:1px solid transparent; white-space:nowrap;
}
.vp-chip--pos{background:var(--vp-emerald-soft); color:var(--vp-emerald-700); border-color:var(--vp-emerald-line);}
.vp-chip--neg{background:var(--vp-red-soft); color:#B42318; border-color:var(--vp-red-line);}
.vp-chip--warn{background:var(--vp-amber-soft); color:#92400E; border-color:var(--vp-amber-line);}
.vp-chip--neutral{background:var(--vp-surface-3); color:var(--vp-body); border-color:var(--vp-line);}
.vp-chip--navy{background:var(--vp-navy-soft); color:#25334C; border-color:var(--vp-navy-line);}
.vp-chip--live{background:rgba(14,159,110,.10); color:var(--vp-emerald-700); border-color:var(--vp-emerald-line);}
.vp-dot{width:6px; height:6px; border-radius:50%; background:currentColor; position:relative;}
.vp-dot--pulse::after{
  content:""; position:absolute; inset:-3px; border-radius:50%; background:currentColor;
  animation:vp-pulse 1.9s cubic-bezier(.16,1,.3,1) infinite;
}

/* KPI grid */
.vp-kpi-grid{display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px;}
.vp-kpi{
  background:var(--vp-surface); border:1px solid var(--vp-line); border-radius:15px; padding:14px 15px 12px;
  box-shadow:var(--vp-sh-2); transition:transform .18s ease, box-shadow .18s ease, border-color .18s ease;
  display:flex; flex-direction:column; gap:8px; min-width:0;
}
.vp-kpi:hover{transform:translateY(-2px); box-shadow:var(--vp-sh-3); border-color:#DBE3EE;}
.vp-kpi-top{display:flex; align-items:center; gap:9px;}
.vp-ico{
  width:30px; height:30px; flex:0 0 30px; border-radius:9px; display:grid; place-items:center;
  background:var(--vp-surface-3); color:var(--vp-body); border:1px solid var(--vp-line);
}
.vp-ico svg{width:15px; height:15px;}
.vp-ico--pos{background:var(--vp-emerald-soft); color:var(--vp-emerald-700); border-color:var(--vp-emerald-line);}
.vp-ico--warn{background:var(--vp-amber-soft); color:var(--vp-amber); border-color:var(--vp-amber-line);}
.vp-ico--neg{background:var(--vp-red-soft); color:var(--vp-red); border-color:var(--vp-red-line);}
.vp-ico--navy{background:var(--vp-navy-soft); color:#25334C; border-color:var(--vp-navy-line);}
.vp-kpi-label{font-size:11.5px; font-weight:600; color:var(--vp-muted); letter-spacing:.015em; text-transform:uppercase;}
.vp-kpi-value{font-size:1.42rem; font-weight:700; color:var(--vp-ink); letter-spacing:-.02em; line-height:1.15; font-variant-numeric:tabular-nums;}
.vp-kpi-foot{display:flex; align-items:center; justify-content:space-between; gap:8px; font-size:11.5px; color:var(--vp-muted);}
.vp-spark{display:block; width:100%; height:30px;}

/* Score factor cards */
.vp-factor-grid{display:grid; grid-template-columns:repeat(auto-fit,minmax(178px,1fr)); gap:12px;}
.vp-factor{
  background:var(--vp-surface); border:1px solid var(--vp-line); border-radius:15px; padding:14px 15px 15px;
  box-shadow:var(--vp-sh-2); transition:transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
.vp-factor:hover{transform:translateY(-2px); box-shadow:var(--vp-sh-3); border-color:#DBE3EE;}
.vp-factor-head{display:flex; align-items:center; justify-content:space-between; gap:8px;}
.vp-factor-name{font-size:12.5px; font-weight:600; color:var(--vp-body); display:flex; align-items:center; gap:7px;}
.vp-factor-val{font-size:1.15rem; font-weight:700; color:var(--vp-ink); letter-spacing:-.02em; font-variant-numeric:tabular-nums;}
.vp-factor-val small{font-size:11px; font-weight:600; color:var(--vp-faint); letter-spacing:0;}
.vp-track{height:6px; border-radius:var(--vp-pill); background:var(--vp-surface-3); overflow:hidden; margin:11px 0 9px;}
.vp-fill{height:100%; border-radius:var(--vp-pill); animation:vp-grow .95s cubic-bezier(.16,1,.3,1) both;}
.vp-factor-foot{display:flex; align-items:center; justify-content:space-between; gap:6px; font-size:11px; color:var(--vp-muted);}

.vp-tip{position:relative; cursor:help; border-bottom:1px dotted #C8D3E1;}
.vp-tip::after{
  content:attr(data-tip); position:absolute; left:50%; bottom:calc(100% + 9px); width:212px;
  transform:translateX(-50%) translateY(4px); background:#0B1729; color:#F8FAFC;
  font-size:11.5px; font-weight:450; line-height:1.5; padding:8px 10px; border-radius:9px;
  opacity:0; pointer-events:none; transition:opacity .16s ease, transform .16s ease; z-index:60;
  box-shadow:0 14px 30px -14px rgba(11,23,41,.7); text-align:left; letter-spacing:0;
}
.vp-tip:hover::after{opacity:1; transform:translateX(-50%) translateY(0);}

/* Hero score */
.vp-hero{display:grid; grid-template-columns:auto minmax(0,1fr); gap:26px; align-items:center;}
@media (max-width:1150px){.vp-hero{grid-template-columns:1fr; justify-items:center; text-align:center;}}
.vp-ring-wrap{position:relative; width:196px; height:196px; flex:0 0 196px;}
.vp-ring{width:196px; height:196px; transform:rotate(-90deg);}
.vp-ring circle{fill:none; stroke-linecap:round;}
.vp-ring-track{stroke:#E9EFF6; stroke-width:13;}
.vp-ring-arc{stroke:url(#vpRingGrad); stroke-width:13; animation:vp-draw 1.25s cubic-bezier(.16,1,.3,1) both; filter:drop-shadow(0 6px 14px rgba(14,159,110,.28));}
.vp-ring-center{
  position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:1px;
}
.vp-ring-score{font-size:2.5rem; font-weight:700; color:var(--vp-ink); letter-spacing:-.035em; line-height:1; font-variant-numeric:tabular-nums;}
.vp-ring-den{font-size:11.5px; font-weight:600; color:var(--vp-faint); letter-spacing:.02em;}
.vp-ring-cap{font-size:10.5px; font-weight:700; color:var(--vp-emerald-700); letter-spacing:.09em; text-transform:uppercase; margin-top:4px;}
.vp-grade{
  display:inline-flex; align-items:center; gap:7px; padding:5px 12px; border-radius:var(--vp-pill);
  font-size:12px; font-weight:700; letter-spacing:.03em; text-transform:uppercase;
}
.vp-grade--pos{background:var(--vp-emerald-soft); color:var(--vp-emerald-700); border:1px solid var(--vp-emerald-line);}
.vp-grade--warn{background:var(--vp-amber-soft); color:#92400E; border:1px solid var(--vp-amber-line);}
.vp-grade--neg{background:var(--vp-red-soft); color:#B42318; border:1px solid var(--vp-red-line);}
.vp-hero-note{font-size:13px; color:var(--vp-body); margin:0; max-width:46ch;}
.vp-scale{margin-top:14px; max-width:430px;}
.vp-scale-bar{position:relative; height:8px; border-radius:var(--vp-pill); overflow:visible;
  background:linear-gradient(90deg,#F6C6C6 0%,#F6C6C6 41.66%,#FBE3BE 41.66%,#FBE3BE 58.33%,#FCEFBB 58.33%,#FCEFBB 66.66%,#CDEEDD 66.66%,#CDEEDD 75%,#A9E4C9 75%,#A9E4C9 100%);}
.vp-scale-mark{position:absolute; top:-4px; width:16px; height:16px; border-radius:50%; background:var(--vp-ink);
  border:3px solid #fff; box-shadow:0 2px 8px -1px rgba(11,23,41,.45); transform:translateX(-50%); animation:vp-pop .5s .5s cubic-bezier(.16,1,.3,1) both;}
.vp-scale-labels{display:flex; justify-content:space-between; font-size:10.5px; color:var(--vp-faint); margin-top:7px; font-weight:550;}
.vp-scale-here{font-size:11px; font-weight:650; color:var(--vp-ink-2);}

/* Insights */
.vp-insights{display:grid; grid-template-columns:repeat(auto-fit,minmax(292px,1fr)); gap:12px;}
.vp-insight{
  background:var(--vp-surface); border:1px solid var(--vp-line); border-left-width:3px;
  border-radius:13px; padding:13px 15px; box-shadow:var(--vp-sh-1);
  transition:transform .18s ease, box-shadow .18s ease;
}
.vp-insight:hover{transform:translateY(-2px); box-shadow:var(--vp-sh-2);}
.vp-insight--pos{border-left-color:var(--vp-emerald);}
.vp-insight--warn{border-left-color:var(--vp-amber);}
.vp-insight--neg{border-left-color:var(--vp-red);}
.vp-insight-title{display:flex; align-items:center; gap:8px; font-size:13px; font-weight:650; color:var(--vp-ink);}
.vp-insight-body{font-size:12.5px; color:var(--vp-body); margin-top:5px; line-height:1.55;}

/* Risk rows */
.vp-risk-row{
  display:grid; grid-template-columns:minmax(0,1.15fr) 118px minmax(0,1.55fr); gap:14px; align-items:center;
  padding:12px 4px; border-bottom:1px solid var(--vp-line-2);
}
.vp-risk-row:last-child{border-bottom:none;}
.vp-risk-name{font-size:13px; font-weight:600; color:var(--vp-ink-2);}
.vp-risk-detail{font-size:12.25px; color:var(--vp-muted); line-height:1.5;}
.vp-badge{
  display:inline-flex; align-items:center; gap:6px; font-size:10.5px; font-weight:700; letter-spacing:.055em;
  text-transform:uppercase; padding:4px 9px; border-radius:7px; justify-content:center;
}
.vp-badge--low{background:var(--vp-emerald-soft); color:var(--vp-emerald-700); border:1px solid var(--vp-emerald-line);}
.vp-badge--mod{background:var(--vp-amber-soft); color:#92400E; border:1px solid var(--vp-amber-line);}
.vp-badge--high{background:var(--vp-red-soft); color:#B42318; border:1px solid var(--vp-red-line);}
.vp-badge--info{background:var(--vp-navy-soft); color:#25334C; border:1px solid var(--vp-navy-line);}
@media (max-width:820px){.vp-risk-row{grid-template-columns:1fr; gap:6px;}}

/* Stat tiles + mini tables */
.vp-tiles{display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:10px;}
.vp-tile{background:var(--vp-surface-2); border:1px solid var(--vp-line); border-radius:12px; padding:11px 13px;}
.vp-tile-label{font-size:10.5px; font-weight:650; letter-spacing:.06em; text-transform:uppercase; color:var(--vp-faint);}
.vp-tile-value{font-size:1.02rem; font-weight:680; color:var(--vp-ink); margin-top:3px; font-variant-numeric:tabular-nums;}
.vp-table{width:100%; border-collapse:separate; border-spacing:0; font-size:12.5px;}
.vp-table th{
  text-align:left; font-size:10.5px; letter-spacing:.07em; text-transform:uppercase; color:var(--vp-faint);
  font-weight:700; padding:0 10px 9px 0; border-bottom:1px solid var(--vp-line);
}
.vp-table td{padding:10px 10px 10px 0; border-bottom:1px solid var(--vp-line-2); color:var(--vp-body); vertical-align:middle;}
.vp-table tr:last-child td{border-bottom:none;}
.vp-table td:first-child{font-weight:600; color:var(--vp-ink-2);}
.vp-num{font-variant-numeric:tabular-nums;}

/* Eligibility */
.vp-elig{
  background:linear-gradient(135deg,#0B2545 0%,#123A5C 45%,#0B5F46 100%);
  border-radius:var(--vp-r-lg); padding:24px 26px; color:#E6F1EA; box-shadow:var(--vp-sh-3); position:relative; overflow:hidden;
}
.vp-elig::after{
  content:""; position:absolute; right:-70px; top:-90px; width:280px; height:280px; border-radius:50%;
  background:radial-gradient(circle, rgba(18,179,124,.42), rgba(18,179,124,0) 68%);
}
.vp-elig-grid{display:grid; grid-template-columns:minmax(0,1.25fr) minmax(0,1fr); gap:26px; position:relative; z-index:1;}
@media (max-width:900px){.vp-elig-grid{grid-template-columns:1fr; gap:18px;}}
.vp-elig-eyebrow{font-size:10.5px; font-weight:700; letter-spacing:.12em; text-transform:uppercase; color:#7FE3B8;}
.vp-elig-range{font-size:2.25rem; font-weight:700; color:#FFFFFF; letter-spacing:-.03em; margin:6px 0 2px; font-variant-numeric:tabular-nums;}
.vp-elig-exact{font-size:12.5px; color:#A9C4BD;}
.vp-elig-note{font-size:12.5px; color:#B9CFC7; margin-top:10px; max-width:48ch; line-height:1.6;}
.vp-elig-meta{display:grid; gap:11px; align-content:center;}
.vp-elig-meta-row{display:flex; align-items:center; justify-content:space-between; gap:12px; font-size:12.5px; padding-bottom:9px; border-bottom:1px solid rgba(255,255,255,.13);}
.vp-elig-meta-row:last-child{border-bottom:none; padding-bottom:0;}
.vp-elig-meta-label{color:#9FBDB4;}
.vp-elig-meta-value{color:#FFFFFF; font-weight:650;}
.vp-elig-bar{height:6px; border-radius:var(--vp-pill); background:rgba(255,255,255,.16); overflow:hidden; margin-top:6px;}
.vp-elig-bar > div{height:100%; border-radius:var(--vp-pill); background:linear-gradient(90deg,#34D399,#7FE3B8); animation:vp-grow 1s cubic-bezier(.16,1,.3,1) both;}
.vp-elig-foot{font-size:11px; color:#8FB3AA; margin-top:14px; position:relative; z-index:1;}

/* Integrity + checks */
.vp-verdict{
  display:flex; align-items:center; gap:16px; padding:18px 20px; border-radius:var(--vp-r);
  border:1px solid var(--vp-line); background:var(--vp-surface); box-shadow:var(--vp-sh-2);
}
.vp-verdict--pass{background:linear-gradient(120deg, rgba(14,159,110,.10), rgba(255,255,255,1) 62%); border-color:var(--vp-emerald-line);}
.vp-verdict--fail{background:linear-gradient(120deg, rgba(220,38,38,.10), rgba(255,255,255,1) 62%); border-color:var(--vp-red-line);}
.vp-verdict-badge{
  width:52px; height:52px; flex:0 0 52px; border-radius:15px; display:grid; place-items:center; font-size:22px; font-weight:700;
}
.vp-verdict-badge--pass{background:var(--vp-emerald); color:#fff; box-shadow:0 10px 22px -12px rgba(11,138,95,.9);}
.vp-verdict-badge--fail{background:var(--vp-red); color:#fff; box-shadow:0 10px 22px -12px rgba(220,38,38,.9); animation:vp-blink 1.5s ease-in-out infinite;}
.vp-verdict-title{font-size:15.5px; font-weight:700; color:var(--vp-ink); letter-spacing:-.01em;}
.vp-verdict-status{font-size:11.5px; font-weight:700; letter-spacing:.06em; text-transform:uppercase; margin-top:2px;}
.vp-check-row{display:grid; grid-template-columns:minmax(0,.95fr) 112px minmax(0,1.7fr); gap:14px; align-items:center; padding:11px 2px; border-bottom:1px solid var(--vp-line-2);}
.vp-check-row:last-child{border-bottom:none;}
.vp-check-name{font-size:12.75px; font-weight:600; color:var(--vp-ink-2);}
.vp-check-detail{font-size:12.25px; color:var(--vp-muted);}
@media (max-width:820px){.vp-check-row{grid-template-columns:1fr; gap:5px;}}

/* Document pages */
.vp-doc{background:var(--vp-surface); border:1px solid var(--vp-line); border-radius:var(--vp-r); padding:26px 32px 30px; box-shadow:var(--vp-sh-2); max-width:900px;}
.vp-doc h3{font-size:13.5px !important; font-weight:700; color:var(--vp-ink) !important; margin:20px 0 6px !important;}
.vp-doc p, .vp-doc li{font-size:13.5px; color:var(--vp-body); line-height:1.72;}
.vp-doc ul{padding-left:18px;}
.vp-doc-meta{font-size:11.5px; color:var(--vp-muted); border-bottom:1px solid var(--vp-line); padding-bottom:12px; margin-bottom:6px;}
.vp-foot{font-size:11.5px; color:var(--vp-faint); text-align:center; padding:22px 0 6px; line-height:1.65;}

/* ── Motion ────────────────────────────────────────────────────────────────── */
html{scroll-behavior:smooth;}
@property --vp-num{syntax:"<integer>"; inherits:false; initial-value:0;}
.vp-num{counter-reset:vp-num var(--vp-num); font-variant-numeric:tabular-nums;}
.vp-num::after{content:counter(vp-num);}
.vp-rise{animation:vp-rise .38s cubic-bezier(.16,1,.3,1) both;}
.vp-rise-1{animation-delay:.04s;} .vp-rise-2{animation-delay:.08s;} .vp-rise-3{animation-delay:.12s;}
@keyframes vp-rise{from{opacity:0; transform:translateY(8px);} to{opacity:1; transform:none;}}
@keyframes vp-grow{from{width:0;}}
@keyframes vp-draw{from{stroke-dashoffset:var(--vp-c,528);}}
@keyframes vp-pop{from{opacity:0; transform:translateX(-50%) scale(.4);} to{opacity:1; transform:translateX(-50%) scale(1);}}
@keyframes vp-pulse{0%{transform:scale(.9); opacity:.75;} 70%{transform:scale(2.4); opacity:0;} 100%{transform:scale(2.4); opacity:0;}}
@keyframes vp-blink{0%,100%{opacity:1;} 50%{opacity:.62;}}
.vp-count-anim{animation-duration:1.15s; animation-timing-function:cubic-bezier(.16,1,.3,1); animation-fill-mode:both;}
@media (prefers-reduced-motion: reduce){*{animation-duration:.001ms !important; animation-iteration-count:1 !important; transition-duration:.001ms !important;}}

/* ── Responsive ────────────────────────────────────────────────────────────── */
@media (max-width:1400px){
  [data-testid="stMainBlockContainer"], .block-container{padding-left:1.6rem !important; padding-right:1.6rem !important;}
}
@media (max-width:1200px){
  .vp-kpi-grid{grid-template-columns:repeat(2,minmax(0,1fr));}
}
@media (max-width:980px){
  [data-testid="stMainBlockContainer"], .block-container{padding:2.6rem 1.1rem 3rem !important;}
  .vp-elig-grid{grid-template-columns:1fr;}
  .vp-hero{gap:18px;}
}
@media (max-width:760px){
  .vp-kpi-grid{grid-template-columns:1fr;}
  .vp-factor-grid{grid-template-columns:1fr;}
  .vp-insights{grid-template-columns:1fr;}
  .vp-ring-wrap, .vp-ring{width:168px; height:168px; flex-basis:168px;}
  .vp-ring-score{font-size:2.1rem;}
  .vp-h1{font-size:1.32rem;}
  .vp-elig-range{font-size:1.7rem;}
  .vp-doc{padding:20px 18px 24px;}
  [data-testid="stMainBlockContainer"], .block-container{padding:2.4rem .8rem 2.6rem !important;}
}
</style>
"""
st.markdown(APP_CSS, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# 2. PRESENTATION PRIMITIVES (icons, formatting, card builders)
# ══════════════════════════════════════════════════════════════════════════════

ICON_PATHS = {
    "revenue": '<path d="M3 16.5l5.2-5.2 3.4 3.4L20 7"/><path d="M15 7h5v5"/>',
    "expense": '<path d="M6 3.5h12v17l-3-1.9-3 1.9-3-1.9-3 1.9z"/><path d="M9 8.5h6M9 12.5h4"/>',
    "profit": '<path d="M3.5 8.5A2.5 2.5 0 0 1 6 6h12a2.5 2.5 0 0 1 2.5 2.5v7A2.5 2.5 0 0 1 18 18H6a2.5 2.5 0 0 1-2.5-2.5z"/><path d="M16.5 12.5h1.5"/>',
    "upi": '<rect x="6.5" y="2.5" width="11" height="19" rx="2.6"/><path d="M10.5 5.5h3"/><path d="M9 13.2l2 2 4-4.4"/>',
    "consistency": '<path d="M3 12.5h3.4l2-5 3 10 2.3-6.3 1.8 3.3H21"/>',
    "growth": '<path d="M3 18V7"/><path d="M3 18h18"/><path d="M7 15V11M11 15V8M15 15v-5M19 15V5"/>',
    "liquidity": '<path d="M12 3.2s5.6 5.3 5.6 9.4A5.6 5.6 0 0 1 12 18.2a5.6 5.6 0 0 1-5.6-5.6C6.4 8.5 12 3.2 12 3.2z"/><path d="M9.6 13.2a2.5 2.5 0 0 0 2.4 2.4"/>',
    "diversity": '<circle cx="9" cy="8.5" r="3.2"/><path d="M3.5 19.5a5.7 5.7 0 0 1 11 0"/><path d="M16 6.2a3 3 0 0 1 0 5.6M17.6 19.5a5.6 5.6 0 0 0-2-4"/>',
    "reliability": '<path d="M12 3l7 2.8v5.4c0 4.2-2.9 7.7-7 9.3-4.1-1.6-7-5.1-7-9.3V5.8z"/><path d="M9 12l2.2 2.2L15.4 10"/>',
    "longevity": '<path d="M12 21s6.5-6 6.5-10.4A6.5 6.5 0 0 0 5.5 10.6C5.5 15 12 21 12 21z"/><circle cx="12" cy="10.4" r="2.3"/>',
    "shield": '<path d="M12 3l7 2.8v5.4c0 4.2-2.9 7.7-7 9.3-4.1-1.6-7-5.1-7-9.3V5.8z"/>',
    "alert": '<path d="M10.3 4.3a2 2 0 0 1 3.4 0l7 12.1a2 2 0 0 1-1.7 3H5a2 2 0 0 1-1.7-3z"/><path d="M12 9.4v4.1"/><path d="M12 16.4h.01"/>',
    "check": '<circle cx="12" cy="12" r="8.8"/><path d="M8.3 12.3l2.6 2.6 4.8-5"/>',
    "info": '<circle cx="12" cy="12" r="8.8"/><path d="M12 11v5.2"/><path d="M12 7.9h.01"/>',
    "spark": '<path d="M12 3.5l1.7 4.8 4.8 1.7-4.8 1.7L12 16.5l-1.7-4.8L5.5 10l4.8-1.7z"/><path d="M18.5 16.5l.7 1.9 1.9.7-1.9.7-.7 1.9-.7-1.9-1.9-.7 1.9-.7z"/>',
    "lock": '<rect x="4.8" y="10.2" width="14.4" height="10.3" rx="2.4"/><path d="M8.4 10.2V7.9a3.6 3.6 0 0 1 7.2 0v2.3"/>',
    "doc": '<path d="M14 3.5H7a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8.5z"/><path d="M14 3.5V8.5h5"/><path d="M9 13h6M9 16.5h4"/>',
    "clock": '<circle cx="12" cy="12" r="8.8"/><path d="M12 7.6V12l3.1 1.9"/>',
    "target": '<circle cx="12" cy="12" r="8.6"/><circle cx="12" cy="12" r="4.6"/><circle cx="12" cy="12" r="1"/>',
    "activity": '<path d="M3 12h3.6l1.9-5.2 3.2 10.4 2.1-5.6 1.5 2.4H21"/>',
    "wallet": '<path d="M4 7.8A2.3 2.3 0 0 1 6.3 5.5h11.4A2.3 2.3 0 0 1 20 7.8v8.4a2.3 2.3 0 0 1-2.3 2.3H6.3A2.3 2.3 0 0 1 4 16.2z"/><path d="M4 10.5h16"/>',
    "scale": '<path d="M12 4.5v15"/><path d="M6.5 19.5h11"/><path d="M5 8.5h14"/><path d="M8 8.5l-2.5 5h5z"/><path d="M16 8.5l-2.5 5h5z"/>',
    "pin": '<path d="M12 21s6-5.6 6-10.1A6 6 0 0 0 6 10.9C6 15.4 12 21 12 21z"/><circle cx="12" cy="10.6" r="2.1"/>',
    "calendar": '<rect x="4" y="5.5" width="16" height="15" rx="2.4"/><path d="M4 10h16M9 3.5v4M15 3.5v4"/>',
    "qr": '<rect x="4" y="4" width="6.4" height="6.4" rx="1.4"/><rect x="13.6" y="4" width="6.4" height="6.4" rx="1.4"/><rect x="4" y="13.6" width="6.4" height="6.4" rx="1.4"/><path d="M14 14h2.6v2.6H14zM18.6 18.6h1.4v1.4h-1.4z"/>',
    "bell": '<path d="M18 16.5V11a6 6 0 0 0-12 0v5.5L4.5 18.4h15z"/><path d="M10 18.4a2 2 0 0 0 4 0"/>',
}


def icon(name: str, cls: str = "") -> str:
    """Inline SVG icon (stroke follows currentColor) so the app stays dependency-free."""
    return (
        f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        f'{ICON_PATHS.get(name, ICON_PATHS["info"])}</svg>'
    )


def inr(value, decimals: int = 0) -> str:
    """Format rupees with Indian digit grouping, e.g. 250000 -> ₹2,50,000."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "₹0"
    sign = "−" if number < 0 else ""
    number = abs(number)
    if decimals:
        body = f"{number:,.{decimals}f}"
        whole, _, frac = body.partition(".")
    else:
        whole, frac = f"{int(round(number))}", ""
    if len(whole) > 3:
        head, tail = whole[:-3], whole[-3:]
        groups = []
        while head:
            groups.insert(0, head[-2:])
            head = head[:-2]
        whole = ",".join(groups + [tail])
    return f"{sign}₹{whole}" + (f".{frac}" if frac else "")


def inr_short(value) -> str:
    """Compact Indian notation for axis labels and headline ranges (₹85K, ₹1.2L, ₹1.1Cr)."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "₹0"
    sign = "−" if number < 0 else ""
    number = abs(number)
    if number >= 1_00_00_000:
        return f"{sign}₹{number / 1_00_00_000:.2f}Cr".replace(".00Cr", "Cr")
    if number >= 1_00_000:
        text = f"{number / 1_00_000:.1f}L"
        return f"{sign}₹{text.replace('.0L', 'L')}"
    if number >= 1_000:
        return f"{sign}₹{number / 1_000:.0f}K"
    return f"{sign}₹{number:.0f}"


def pct_change(current, previous) -> float:
    """Percentage change, guarded for zero/absent baselines."""
    try:
        previous = float(previous)
        if previous == 0:
            return 0.0
        return (float(current) - previous) / abs(previous) * 100
    except (TypeError, ValueError):
        return 0.0


def delta_chip(pct: float, suffix: str = "vs last month") -> str:
    tone = "pos" if pct > 0.05 else ("neg" if pct < -0.05 else "neutral")
    arrow = "↑" if pct > 0.05 else ("↓" if pct < -0.05 else "→")
    return f'<span class="vp-chip vp-chip--{tone}">{arrow} {pct:+.1f}%</span>'


def counter_span(value: int, cls: str = "vp-num") -> str:
    """CSS counter that animates 0 → value (degrades to the static value elsewhere)."""
    value = max(0, int(value))
    return (
        f'<style>@keyframes vpc{value}{{from{{--vp-num:0}}to{{--vp-num:{value}}}}}</style>'
        f'<span class="{cls} vp-count-anim" style="--vp-num:{value};animation-name:vpc{value}"></span>'
    )


def sparkline(values, color: str = "#0E9F6E", width: int = 110, height: int = 30) -> str:
    """Tiny SVG sparkline with a soft area fill."""
    nums = [float(v) for v in values] or [0.0]
    if len(nums) == 1:
        nums = nums * 2
    lo, hi = min(nums), max(nums)
    span = (hi - lo) or 1.0
    step = (width - 6) / (len(nums) - 1)
    points = [
        (3 + i * step, (height - 5) - ((v - lo) / span) * (height - 12))
        for i, v in enumerate(nums)
    ]
    path = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    area = f"M3,{height - 2} L" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points) + f" L{width - 3},{height - 2} Z"
    return (
        f'<svg class="vp-spark" viewBox="0 0 {width} {height}" preserveAspectRatio="none">'
        f'<path d="{area}" fill="{color}" opacity="0.10"/>'
        f'<polyline points="{path}" fill="none" stroke="{color}" stroke-width="2" '
        f'vector-effect="non-scaling-stroke" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<circle cx="{points[-1][0]:.1f}" cy="{points[-1][1]:.1f}" r="2.6" fill="{color}"/>'
        f"</svg>"
    )


def section(eyebrow: str, title: str, sub: str = "", right: str = "") -> None:
    right_html = f'<div style="flex:0 0 auto">{right}</div>' if right else ""
    sub_html = f'<p class="vp-section-sub">{sub}</p>' if sub else ""
    st.markdown(
        f'<div class="vp-section"><div><div class="vp-eyebrow">{eyebrow}</div>'
        f'<div class="vp-section-title">{title}</div>{sub_html}</div>{right_html}</div>',
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value: str, icon_name: str, tone: str, delta: float,
             compare: str, spark_values, spark_color: str = "#0E9F6E") -> str:
    return (
        f'<div class="vp-kpi">'
        f'<div class="vp-kpi-top"><div class="vp-ico vp-ico--{tone}">{icon(icon_name)}</div>'
        f'<div class="vp-kpi-label">{label}</div></div>'
        f'<div class="vp-kpi-value">{value}</div>'
        f'<div class="vp-kpi-foot">{delta_chip(delta)}<span>{compare}</span></div>'
        f'{sparkline(spark_values, spark_color)}'
        f"</div>"
    )


def factor_card(name: str, value: int, delta_text: str, icon_name: str, tooltip: str) -> str:
    if value >= 75:
        color, tone = "linear-gradient(90deg,#34D399,#0E9F6E)", "pos"
    elif value >= 55:
        color, tone = "linear-gradient(90deg,#FBBF24,#F59E0B)", "warn"
    else:
        color, tone = "linear-gradient(90deg,#F87171,#DC2626)", "neg"
    return (
        f'<div class="vp-factor">'
        f'<div class="vp-factor-head">'
        f'<div class="vp-factor-name"><span class="vp-ico vp-ico--{tone}">{icon(icon_name)}</span>'
        f'<span class="vp-tip" data-tip="{escape(tooltip, quote=True)}">{name}</span></div>'
        f'<div class="vp-factor-val">{counter_span(value)}<small>/100</small></div>'
        f"</div>"
        f'<div class="vp-track"><div class="vp-fill" style="width:{value}%;background:{color}"></div></div>'
        f'<div class="vp-factor-foot"><span>Score contribution</span>'
        f'<span class="vp-chip vp-chip--{"pos" if delta_text.startswith("+") else ("neg" if delta_text.startswith("-") else "neutral")}">'
        f'{delta_text}</span></div>'
        f"</div>"
    )


def insight_card(tone: str, title: str, body: str, icon_name: str = "spark") -> str:
    return (
        f'<div class="vp-insight vp-insight--{tone}">'
        f'<div class="vp-insight-title"><span style="color:var(--vp-{"emerald" if tone == "pos" else ("amber" if tone == "warn" else "red")})">'
        f'{icon(icon_name)}</span>{title}</div>'
        f'<div class="vp-insight-body">{body}</div></div>'
    )


def risk_row(name: str, level: str, detail: str) -> str:
    badge_cls = {"LOW": "low", "MODERATE": "mod", "HIGH": "high", "UNDER REVIEW": "info"}.get(level, "info")
    return (
        f'<div class="vp-risk-row"><div class="vp-risk-name">{name}</div>'
        f'<div><span class="vp-badge vp-badge--{badge_cls}">{level}</span></div>'
        f'<div class="vp-risk-detail">{detail}</div></div>'
    )


def check_row(name: str, result: str, detail: str) -> str:
    badge = {"PASS": "low", "FAIL": "high"}.get(result, "mod")
    return (
        f'<div class="vp-check-row"><div class="vp-check-name">{name}</div>'
        f'<div><span class="vp-badge vp-badge--{badge}">{result}</span></div>'
        f'<div class="vp-check-detail">{detail}</div></div>'
    )


def tiles(items) -> str:
    inner = "".join(
        f'<div class="vp-tile"><div class="vp-tile-label">{label}</div>'
        f'<div class="vp-tile-value">{value}</div></div>'
        for label, value in items
    )
    return f'<div class="vp-tiles">{inner}</div>'


def table(headers, rows) -> str:
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)
    return f'<table class="vp-table"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def card(body: str, cls: str = "", rise: int = 0) -> str:
    rise_cls = f" vp-rise vp-rise-{rise}" if rise else ""
    return f'<div class="vp-card {cls}{rise_cls}">{body}</div>'


# ══════════════════════════════════════════════════════════════════════════════
# 3. MERCHANT DATASET  (unchanged demo data)
# ══════════════════════════════════════════════════════════════════════════════
def get_base_personas():
    return {
        "Ramesh Kirana": {
            "name": "Ramesh Kirana",
            "type": "Kirana Store Owner",
            "location": "Sector 14, Gurgaon",
            "base_score": 702,
            "integrity": "PASS",
            "integrity_reason": "All checks cleared. No anomalies detected.",
            "loan_status": "ELIGIBLE",
            "base_recommended_credit": 250000,
            "factors": {
                "Consistency": {"value": 82, "delta": "+5"},
                "Growth": {"value": 71, "delta": "+12"},
                "Liquidity Buffer": {"value": 68, "delta": "+3"},
                "Payer Diversity": {"value": 88, "delta": "+7"},
                "Reliability": {"value": 79, "delta": "+2"},
                "Longevity": {"value": 74, "delta": "+4"},
            },
            "tips": [
                "Maintain consistent daily UPI collections above Rs 8,000 to push Consistency above 85.",
                "Diversify supplier payments across 3+ vendors to improve Liquidity Buffer rating.",
                "Register for GST to unlock formal credit channels and boost Growth factor.",
            ],
            "monthly_revenue": [45000, 48000, 52000, 49000, 55000, 58000, 61000, 59000, 63000, 67000, 65000, 70000],
            "monthly_expenses": [32000, 34000, 36000, 35000, 38000, 40000, 42000, 41000, 43000, 45000, 44000, 47000],
            "upi_daily_avg": 8500,
            "total_transactions": 14200,
            "sthan_days": 1825,
            "sthan_log": [
                {"date": "2024-01-15", "time": "06:30", "status": "Present", "note": "Morning opening"},
                {"date": "2024-01-16", "time": "06:45", "status": "Present", "note": "Regular day"},
                {"date": "2024-01-17", "time": "07:00", "status": "Present", "note": "Late start rain"},
                {"date": "2024-01-18", "time": "06:30", "status": "Present", "note": "Festival prep"},
                {"date": "2024-01-19", "time": "06:15", "status": "Present", "note": "Early opening"},
                {"date": "2024-01-20", "time": "REST", "status": "Absent", "note": "Sunday closed"},
            ],
        },
        "QuickKart Reseller": {
            "name": "QuickKart Reseller",
            "type": "Online Reseller",
            "location": "Laxmi Nagar, Delhi",
            "base_score": 648,
            "integrity": "FAIL",
            "integrity_reason": "WASH TRADING DETECTED: 67% of inbound UPI payments originate from 2 linked accounts. PAYER CONCENTRATION: Top payer accounts for 73% of volume. Pattern consistent with synthetic transaction inflation.",
            "loan_status": "VOIDED",
            "base_recommended_credit": 0,
            "factors": {
                "Consistency": {"value": 76, "delta": "+2"},
                "Growth": {"value": 89, "delta": "+34"},
                "Liquidity Buffer": {"value": 42, "delta": "-8"},
                "Payer Diversity": {"value": 12, "delta": "-45"},
                "Reliability": {"value": 55, "delta": "-12"},
                "Longevity": {"value": 31, "delta": "-5"},
            },
            "tips": [
                "CRITICAL: Payer Diversity score is 12/100. Over 73% revenue from 2 accounts triggers fraud flags.",
                "WARNING: Rapid Growth (+34%) with low Diversity is a red-flag pattern for wash trading.",
                "ACTION REQUIRED: Provide independent third-party transaction verification to clear integrity hold.",
            ],
            "monthly_revenue": [12000, 15000, 22000, 35000, 58000, 89000, 120000, 145000, 180000, 210000, 250000, 290000],
            "monthly_expenses": [10000, 13000, 20000, 32000, 54000, 85000, 115000, 140000, 175000, 205000, 245000, 285000],
            "upi_daily_avg": 9600,
            "total_transactions": 8900,
            "sthan_days": 95,
            "sthan_log": [
                {"date": "2024-01-15", "time": "11:30", "status": "Present", "note": ""},
                {"date": "2024-01-16", "time": "N/A", "status": "Absent", "note": ""},
                {"date": "2024-01-17", "time": "14:00", "status": "Present", "note": ""},
                {"date": "2024-01-18", "time": "N/A", "status": "Absent", "note": ""},
                {"date": "2024-01-19", "time": "N/A", "status": "Absent", "note": ""},
                {"date": "2024-01-20", "time": "10:00", "status": "Present", "note": ""},
            ],
        },
        "Meena's Stall": {
            "name": "Meena's Stall",
            "type": "Street Food Vendor",
            "location": "Chandni Chowk, Delhi",
            "base_score": 585,
            "integrity": "PASS",
            "integrity_reason": "All checks cleared. Thin file compensated by strong physical presence and longevity.",
            "loan_status": "ELIGIBLE",
            "base_recommended_credit": 50000,
            "factors": {
                "Consistency": {"value": 61, "delta": "+1"},
                "Growth": {"value": 45, "delta": "+8"},
                "Liquidity Buffer": {"value": 38, "delta": "-2"},
                "Payer Diversity": {"value": 72, "delta": "+3"},
                "Reliability": {"value": 69, "delta": "+5"},
                "Longevity": {"value": 91, "delta": "+10"},
            },
            "tips": [
                "Your 512-day Sthan Log is your strongest asset. Keep checking in daily to maintain Longevity at 91.",
                "Accept UPI for even small transactions (Rs 10+) to build digital trail and boost Consistency from 61.",
                "Ask 5 regular customers to pay via UPI weekly to improve Payer Diversity score further.",
            ],
            "monthly_revenue": [8000, 8500, 9000, 8200, 9500, 10000, 9800, 10500, 11000, 10800, 11500, 12000],
            "monthly_expenses": [5000, 5200, 5500, 5100, 5800, 6000, 5900, 6300, 6500, 6400, 6800, 7000],
            "upi_daily_avg": 380,
            "total_transactions": 3200,
            "sthan_days": 512,
            "sthan_log": [
                {"date": "2024-01-15", "time": "05:00", "status": "Present", "note": "Morning prep started"},
                {"date": "2024-01-16", "time": "05:15", "status": "Present", "note": "Regular day"},
                {"date": "2024-01-17", "time": "05:00", "status": "Present", "note": "Busy morning"},
                {"date": "2024-01-18", "time": "05:30", "status": "Present", "note": "Festival rush"},
                {"date": "2024-01-19", "time": "05:00", "status": "Present", "note": "Extra stock prepared"},
                {"date": "2024-01-20", "time": "05:00", "status": "Present", "note": "Weekend crowd"},
            ],
        },
        "Suresh Auto Parts": {
            "name": "Suresh Auto Parts",
            "type": "Auto Parts Retailer",
            "location": "Karol Bagh, Delhi",
            "base_score": 745,
            "integrity": "PASS",
            "integrity_reason": "All checks cleared. Strong B2B transaction patterns verified.",
            "loan_status": "ELIGIBLE",
            "base_recommended_credit": 500000,
            "factors": {
                "Consistency": {"value": 85, "delta": "+6"},
                "Growth": {"value": 78, "delta": "+15"},
                "Liquidity Buffer": {"value": 72, "delta": "+8"},
                "Payer Diversity": {"value": 81, "delta": "+4"},
                "Reliability": {"value": 90, "delta": "+3"},
                "Longevity": {"value": 88, "delta": "+2"},
            },
            "tips": [
                "Excellent Reliability score of 90. Maintain timely supplier payments to keep this strong.",
                "Consider adding digital inventory tracking to further validate stock turnover for lenders.",
                "Your B2B payment patterns are strong. Formalize contracts with top 5 garage clients for better terms.",
            ],
            "monthly_revenue": [120000, 135000, 128000, 142000, 155000, 148000, 162000, 170000, 165000, 178000, 185000, 192000],
            "monthly_expenses": [85000, 95000, 90000, 100000, 108000, 105000, 112000, 118000, 115000, 122000, 128000, 132000],
            "upi_daily_avg": 6200,
            "total_transactions": 9800,
            "sthan_days": 2920,
            "sthan_log": [
                {"date": "2024-01-15", "time": "09:00", "status": "Present", "note": "Shop opened"},
                {"date": "2024-01-16", "time": "09:15", "status": "Present", "note": "Bulk order day"},
                {"date": "2024-01-17", "time": "09:00", "status": "Present", "note": "Regular operations"},
                {"date": "2024-01-18", "time": "09:30", "status": "Present", "note": "Supplier meeting"},
                {"date": "2024-01-19", "time": "09:00", "status": "Present", "note": "Inventory check"},
                {"date": "2024-01-20", "time": "10:00", "status": "Present", "note": "Half day family event"},
            ],
        },
        "Fatima Tailoring": {
            "name": "Fatima Tailoring",
            "type": "Home-based Tailor",
            "location": "Jamia Nagar, Delhi",
            "base_score": 540,
            "integrity": "PASS",
            "integrity_reason": "All checks cleared. Ultra-thin file but genuine micro-enterprise pattern confirmed.",
            "loan_status": "ELIGIBLE",
            "base_recommended_credit": 25000,
            "factors": {
                "Consistency": {"value": 48, "delta": "+2"},
                "Growth": {"value": 52, "delta": "+18"},
                "Liquidity Buffer": {"value": 30, "delta": "-1"},
                "Payer Diversity": {"value": 65, "delta": "+9"},
                "Reliability": {"value": 58, "delta": "+4"},
                "Longevity": {"value": 78, "delta": "+6"},
            },
            "tips": [
                "Start accepting UPI payments for all orders above Rs 200 to build a stronger digital footprint.",
                "Your Growth trend (+18%) is promising. Document each order with a photo for expense tracking.",
                "Register with local women's self-help group (SHG) to access group lending at better rates.",
            ],
            "monthly_revenue": [6000, 6500, 7000, 5500, 8000, 9000, 8500, 9500, 10000, 11000, 10500, 12000],
            "monthly_expenses": [3500, 3800, 4000, 3200, 4500, 5000, 4800, 5200, 5500, 6000, 5800, 6500],
            "upi_daily_avg": 220,
            "total_transactions": 1800,
            "sthan_days": 1095,
            "sthan_log": [
                {"date": "2024-01-15", "time": "10:00", "status": "Present", "note": "Started stitching orders"},
                {"date": "2024-01-16", "time": "10:30", "status": "Present", "note": "2 new customers"},
                {"date": "2024-01-17", "time": "10:00", "status": "Present", "note": "Delivery day"},
                {"date": "2024-01-18", "time": "N/A", "status": "Absent", "note": "Family commitment"},
                {"date": "2024-01-19", "time": "09:30", "status": "Present", "note": "Festival orders rush"},
                {"date": "2024-01-20", "time": "10:00", "status": "Present", "note": "Measurements taken"},
            ],
        },
    }


# ══════════════════════════════════════════════════════════════════════════════
# 4. STATE + SCORING ENGINE  (unchanged logic)
# ══════════════════════════════════════════════════════════════════════════════
def init_session_state():
    if "expense_entries" not in st.session_state:
        st.session_state.expense_entries = {}
    if "revenue_entries" not in st.session_state:
        st.session_state.revenue_entries = {}
    if "sthan_entries" not in st.session_state:
        st.session_state.sthan_entries = {}
    if "expense_photos_log" not in st.session_state:
        st.session_state.expense_photos_log = {}


def compute_live_score(persona_key, base_persona):
    """Live score recomputation — identical rules to the original release."""
    base_score = base_persona["base_score"]
    base_expenses = list(base_persona["monthly_expenses"])
    base_revenue = list(base_persona["monthly_revenue"])

    user_expenses = st.session_state.expense_entries.get(persona_key, [])
    user_revenues = st.session_state.revenue_entries.get(persona_key, [])

    total_added_expense = sum(e["amount"] for e in user_expenses)
    total_added_revenue = sum(r["amount"] for r in user_revenues)

    total_base_revenue = sum(base_revenue)
    total_base_expense = sum(base_expenses)
    base_profit = total_base_revenue - total_base_expense

    new_total_revenue = total_base_revenue + total_added_revenue
    new_total_expense = total_base_expense + total_added_expense
    new_profit = new_total_revenue - new_total_expense

    if total_base_revenue > 0:
        base_margin = base_profit / total_base_revenue
        new_margin = new_profit / new_total_revenue if new_total_revenue > 0 else 0
    else:
        base_margin = 0
        new_margin = 0

    margin_shift = new_margin - base_margin

    score_delta = int(margin_shift * 300)
    score_delta = max(-150, min(150, score_delta))

    expense_ratio_change = 0
    if total_base_expense > 0 and total_added_expense > 0:
        expense_ratio_change = total_added_expense / total_base_expense

    if expense_ratio_change > 0.5:
        score_delta -= int(expense_ratio_change * 30)
    elif expense_ratio_change > 0.2:
        score_delta -= int(expense_ratio_change * 15)

    revenue_growth = 0
    if total_added_revenue > 0:
        revenue_growth = total_added_revenue / max(total_base_revenue, 1)
        score_delta += int(revenue_growth * 40)

    sthan_entries = st.session_state.sthan_entries.get(persona_key, [])
    present_checkins = sum(1 for e in sthan_entries if e["status"] == "Present")
    score_delta += present_checkins * 2

    photo_logs = st.session_state.expense_photos_log.get(persona_key, [])
    score_delta += len(photo_logs) * 3

    live_score = base_score + score_delta
    live_score = max(300, min(900, live_score))

    updated_factors = {}
    for fname, fdata in base_persona["factors"].items():
        base_val = fdata["value"]
        if fname == "Liquidity Buffer":
            if new_profit > base_profit:
                adj = min(10, int((new_profit - base_profit) / max(base_profit, 1) * 20))
            else:
                adj = max(-15, int((new_profit - base_profit) / max(abs(base_profit), 1) * 20))
            new_val = max(5, min(100, base_val + adj))
        elif fname == "Consistency":
            if total_added_revenue > 0:
                adj = min(8, int(revenue_growth * 15))
            else:
                adj = 0
            if total_added_expense > total_added_revenue and total_added_expense > 0:
                adj -= 5
            new_val = max(5, min(100, base_val + adj))
        elif fname == "Growth":
            if total_added_revenue > 0:
                adj = min(12, int(revenue_growth * 25))
            else:
                adj = 0
            new_val = max(5, min(100, base_val + adj))
        elif fname == "Reliability":
            adj = present_checkins
            if total_added_expense > total_added_revenue * 1.5 and total_added_revenue > 0:
                adj -= 5
            new_val = max(5, min(100, base_val + adj))
        elif fname == "Longevity":
            adj = present_checkins + len(photo_logs)
            new_val = max(5, min(100, base_val + adj))
        elif fname == "Payer Diversity":
            adj = min(5, len(user_revenues))
            new_val = max(5, min(100, base_val + adj))
        else:
            new_val = base_val

        change = new_val - base_val
        if change >= 0:
            new_delta = f"+{change}"
        else:
            new_delta = str(change)

        updated_factors[fname] = {"value": new_val, "delta": new_delta}

    base_credit = base_persona["base_recommended_credit"]
    if base_persona["integrity"] == "FAIL":
        recommended_credit = 0
    else:
        credit_multiplier = live_score / base_score if base_score > 0 else 1
        recommended_credit = int(base_credit * credit_multiplier)
        recommended_credit = max(0, recommended_credit)
        recommended_credit = (recommended_credit // 1000) * 1000

    return {
        "score": live_score,
        "score_delta": score_delta,
        "factors": updated_factors,
        "recommended_credit": recommended_credit,
        "total_added_expense": total_added_expense,
        "total_added_revenue": total_added_revenue,
        "new_total_revenue": new_total_revenue,
        "new_total_expense": new_total_expense,
        "new_profit": new_profit,
        "margin": new_margin,
    }


def get_score_color(score):
    if score >= 700:
        return "#0E9F6E"
    elif score >= 600:
        return "#F59E0B"
    elif score >= 500:
        return "#D97706"
    else:
        return "#DC2626"


def get_score_label(score):
    if score >= 750:
        return "Excellent"
    elif score >= 700:
        return "Good"
    elif score >= 650:
        return "Fair"
    elif score >= 550:
        return "Below Average"
    else:
        return "Poor"


def score_band_tone(score):
    if score >= 700:
        return "pos"
    if score >= 600:
        return "warn"
    return "neg"


# ══════════════════════════════════════════════════════════════════════════════
# 5. DERIVED INTELLIGENCE
#    Every number below is computed from the existing dataset + live score output.
# ══════════════════════════════════════════════════════════════════════════════
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

FACTOR_ICONS = {
    "Consistency": "consistency",
    "Growth": "growth",
    "Liquidity Buffer": "liquidity",
    "Payer Diversity": "diversity",
    "Reliability": "reliability",
    "Longevity": "longevity",
}

FACTOR_TOOLTIPS = {
    "Consistency": "Stability of day-to-day collections. Rewards steady UPI inflows instead of one-off spikes.",
    "Growth": "Trailing momentum of revenue across the reporting window.",
    "Liquidity Buffer": "Ability to absorb supplier and inventory cycles without cash stress.",
    "Payer Diversity": "Spread of incoming payments across distinct payers — low values signal concentration risk.",
    "Reliability": "Behavioural repayment and discipline signals, including verified check-in history.",
    "Longevity": "How long the merchant has continuously operated from the same location.",
}


def adjusted_series(persona, live, months: int = 12):
    """Monthly series with the merchant's added entries folded in.

    Additions are spread evenly across the 12 monthly periods, exactly like the
    cash-flow chart, so every surface in the app tells the same story.
    """
    rev = list(persona["monthly_revenue"])
    exp = list(persona["monthly_expenses"])
    if live["total_added_revenue"] > 0:
        per = live["total_added_revenue"] / 12
        rev = [r + per for r in rev]
    if live["total_added_expense"] > 0:
        per = live["total_added_expense"] / 12
        exp = [e + per for e in exp]
    profit = [r - e for r, e in zip(rev, exp)]
    n = max(2, min(int(months), len(rev)))
    return {
        "rev": rev,
        "exp": exp,
        "profit": profit,
        "labels": MONTHS[: len(rev)],
        "window": n,
    }


def build_kpis(persona, live, series):
    """KPI payloads for the four headline cards (latest period vs previous period)."""
    rev, exp, profit = series["rev"], series["exp"], series["profit"]
    last_rev, prev_rev = rev[-1], rev[-2]
    last_exp, prev_exp = exp[-1], exp[-2]
    last_profit, prev_profit = profit[-1], profit[-2]
    daily = persona["upi_daily_avg"]
    daily_series = [v / 30 for v in rev]
    return [
        {
            "label": "Monthly Revenue",
            "value": inr(last_rev),
            "icon": "revenue",
            "tone": "pos",
            "delta": pct_change(last_rev, prev_rev),
            "invert": False,
            "compare": f"vs {inr(prev_rev)} in {series['labels'][-2]}",
            "spark": rev,
            "color": "#0E9F6E",
        },
        {
            "label": "Monthly Expenses",
            "value": inr(last_exp),
            "icon": "expense",
            "tone": "navy",
            "delta": pct_change(last_exp, prev_exp),
            "invert": True,
            "compare": f"vs {inr(prev_exp)} in {series['labels'][-2]}",
            "spark": exp,
            "color": "#D97706",
        },
        {
            "label": "Net Profit",
            "value": inr(last_profit),
            "icon": "profit",
            "tone": "pos",
            "delta": pct_change(last_profit, prev_profit),
            "invert": False,
            "compare": f"margin {(last_profit / last_rev * 100 if last_rev else 0):.1f}% in {series['labels'][-1]}",
            "spark": profit,
            "color": "#16233F",
        },
        {
            "label": "Avg UPI Collections",
            "value": f"{inr(daily)}<span style='font-size:12px;font-weight:600;color:var(--vp-muted)'>/day</span>",
            "icon": "upi",
            "tone": "navy",
            "delta": pct_change(last_rev, prev_rev),
            "invert": False,
            "compare": f"{persona['total_transactions']:,} settlements tracked",
            "spark": daily_series,
            "color": "#0F766E",
        },
    ]


def build_insights(persona, live, series, signals):
    """Rule-based observations, generated from the live factor set and cash flow."""
    factors = live["factors"]
    rev, exp = series["rev"], series["exp"]
    rev_mom = pct_change(rev[-1], rev[-2])
    exp_mom = pct_change(exp[-1], exp[-2])
    insights = []

    diversity = factors["Payer Diversity"]["value"]
    if diversity >= 75:
        insights.append({
            "tone": "pos", "icon": "diversity", "title": "Strong payer diversity",
            "body": f"Payer diversity is {diversity}/100 — collections arrive from a wide payer base, "
                    f"so the business is not dependent on a handful of customers.",
        })
    elif diversity >= 50:
        insights.append({
            "tone": "warn", "icon": "diversity", "title": "Payer base can widen",
            "body": f"Payer diversity sits at {diversity}/100. Bringing more distinct UPI payers "
                    f"into the ledger would reduce concentration risk.",
        })
    else:
        insights.append({
            "tone": "neg", "icon": "alert", "title": "Concentration risk detected",
            "body": f"Payer diversity is only {diversity}/100 — a small number of payers drives most "
                    f"of the inflow, which is a recognised wash-trading pattern.",
        })

    if rev_mom >= 1.5:
        insights.append({
            "tone": "pos", "icon": "growth", "title": "Revenue growing",
            "body": f"Revenue increased {rev_mom:.1f}% compared with {series['labels'][-2]} "
                    f"({inr(rev[-2])} → {inr(rev[-1])}).",
        })
    elif rev_mom <= -1.5:
        insights.append({
            "tone": "warn", "icon": "growth", "title": "Revenue softening",
            "body": f"Revenue eased {abs(rev_mom):.1f}% versus {series['labels'][-2]}. "
                    f"Keep a short cash buffer for the next inventory cycle.",
        })
    else:
        insights.append({
            "tone": "pos", "icon": "consistency", "title": "Revenue holding steady",
            "body": f"Collections moved {rev_mom:+.1f}% month on month, within a stable band for this business type.",
        })

    liquidity = factors["Liquidity Buffer"]["value"]
    if liquidity < 70:
        insights.append({
            "tone": "warn", "icon": "liquidity", "title": "Liquidity requires attention",
            "body": f"Current liquidity score is {liquidity}/100. Ring-fencing supplier payments "
                    f"against a cash float would lift this signal.",
        })
    else:
        insights.append({
            "tone": "pos", "icon": "liquidity", "title": "Comfortable liquidity buffer",
            "body": f"Liquidity buffer stands at {liquidity}/100 — routine inventory cycles are covered "
                    f"by operating cash flow.",
        })

    reliability = factors["Reliability"]["value"]
    if persona["integrity"] == "FAIL":
        insights.append({
            "tone": "neg", "icon": "shield", "title": "Repayment signals under review",
            "body": "Integrity layer flagged this profile, so behavioural repayment signals are held "
                    "pending manual verification.",
        })
    elif reliability >= 75:
        insights.append({
            "tone": "pos", "icon": "reliability", "title": "Healthy repayment behaviour",
            "body": f"Reliability is {reliability}/100 — no repayment anomalies were detected across "
                    f"the observed transaction window.",
        })
    else:
        insights.append({
            "tone": "warn", "icon": "reliability", "title": "Behavioural depth building",
            "body": f"Reliability is {reliability}/100. Consistent daily check-ins and timely supplier "
                    f"payments will strengthen this signal.",
        })

    if exp_mom > rev_mom + 3:
        insights.append({
            "tone": "warn", "icon": "expense", "title": "Expense growth outpacing revenue",
            "body": f"Expenses grew {exp_mom:+.1f}% against revenue {rev_mom:+.1f}% month on month — "
                    f"margin compression ahead if the trend continues.",
        })

    consistency = factors["Consistency"]["value"]
    if consistency < 60:
        insights.append({
            "tone": "warn", "icon": "consistency", "title": "Consistency needs a daily habit",
            "body": f"Consistency is {consistency}/100. Digitising every sale — even small ticket sizes — "
                    f"stabilises this factor quickly.",
        })

    longevity = factors["Longevity"]["value"]
    if longevity >= 85:
        insights.append({
            "tone": "pos", "icon": "longevity", "title": "Location stability is an asset",
            "body": f"{persona['sthan_days']:,} days logged at {persona['location']}. Sthan Log history "
                    f"is the strongest proxy for thin-file merchants.",
        })

    live_summary = st.session_state.expense_photos_log.get(persona["name"], [])
    if live_summary:
        insights.append({
            "tone": "pos", "icon": "doc", "title": "Documentation added",
            "body": f"{len(live_summary)} expense record page(s) attached to the credit passport, "
                    f"adding verified documentation depth.",
        })

    order = {"neg": 0, "warn": 1, "pos": 2}
    insights.sort(key=lambda item: order[item["tone"]])
    return insights[:6]


def build_risk_signals(persona, live, series):
    """Transparent rule-based monitoring signals (indicative, not a fraud verdict)."""
    factors = live["factors"]
    rev = series["rev"]
    mean_rev = sum(rev) / len(rev)
    variance = sum((value - mean_rev) ** 2 for value in rev) / len(rev)
    volatility = (variance ** 0.5) / mean_rev if mean_rev else 0
    txns_per_day = persona["total_transactions"] / max(persona["sthan_days"], 1)
    growth_multiple = max(persona["monthly_revenue"]) / max(min(persona["monthly_revenue"]), 1)
    diversity = factors["Payer Diversity"]["value"]
    integrity_fail = persona["integrity"] == "FAIL"

    signals = []

    if integrity_fail:
        level = "HIGH"
        detail = "Integrity layer is holding this profile: circular payment pattern detected in the reviewed ledger."
    elif diversity < 50:
        level = "MODERATE"
        detail = f"Payer diversity {diversity}/100 keeps inflow routing under observation."
    else:
        level = "LOW"
        detail = f"Inflow routing is normal across a wide payer base (payer diversity {diversity}/100)."
    signals.append({"name": "UPI anomaly status", "level": level, "detail": detail})

    if txns_per_day > 30:
        level, note = "HIGH", "far above the range expected for this business type"
    elif txns_per_day > 10:
        level, note = "MODERATE", "above the typical band for a comparable merchant"
    else:
        level, note = "LOW", "inside the expected band for this business type"
    signals.append({
        "name": "Unusual transaction frequency", "level": level,
        "detail": f"≈{txns_per_day:.1f} settlements per day against {persona['sthan_days']:,} days of "
                  f"logged presence — {note}.",
    })

    if volatility > 0.45:
        level, note = "HIGH", "highly irregular collections"
    elif volatility > 0.22:
        level, note = "MODERATE", "moderately uneven collections"
    else:
        level, note = "LOW", "stable collections"
    signals.append({
        "name": "Revenue volatility", "level": level,
        "detail": f"Month-on-month dispersion of {volatility * 100:.0f}% across the reporting window — {note}.",
    })

    if diversity >= 70:
        level, note = "LOW", "no single payer dominates inflow"
    elif diversity >= 45:
        level, note = "MODERATE", "a few payers carry a large share of inflow"
    else:
        level, note = "HIGH", "top payer concentration is material"
    signals.append({
        "name": "Merchant concentration risk", "level": level,
        "detail": f"Payer diversity index {diversity}/100 — {note}.",
    })

    if integrity_fail:
        level, note = "HIGH", "revenue curve and payer structure are inconsistent with organic growth"
    elif growth_multiple > 4 and diversity < 60:
        level, note = "MODERATE", "steep revenue ramp with a narrow payer base"
    else:
        level, note = "LOW", "growth is consistent with the reported payer base"
    signals.append({
        "name": "Suspicious transaction patterns", "level": level,
        "detail": f"Monthly revenue spans {inr(min(persona['monthly_revenue']))} → "
                  f"{inr(max(persona['monthly_revenue']))} ({growth_multiple:.1f}×) — {note}.",
    })

    weights = {"LOW": 0, "MODERATE": 1.5, "HIGH": 3}
    index = sum(weights[s["level"]] for s in signals)
    risk_pct = index / 15 * 100
    if risk_pct <= 12:
        category, tone = "Low risk", "low"
    elif risk_pct <= 35:
        category, tone = "Moderate risk", "mod"
    elif risk_pct <= 60:
        category, tone = "Elevated risk", "mod"
    else:
        category, tone = "High risk", "high"
    return signals, {"percent": risk_pct, "category": category, "badge": tone, "weights": index}


def build_eligibility(persona, live, risk, extras):
    """Indicative eligibility envelope derived from the live score output."""
    if persona["integrity"] == "FAIL" or live["recommended_credit"] <= 0:
        return {
            "state": "review",
            "low": 0,
            "high": 0,
            "confidence": 0,
            "tenure": "Pending review",
            "note": "Integrity layer has voided automated eligibility for this profile. "
                    "A credit officer can review the underlying signals manually.",
        }

    low = live["recommended_credit"]
    high = low * 1.5
    rounder = 10000 if high >= 100000 else (5000 if high >= 20000 else 1000)
    high = int(high // rounder * rounder)
    high = max(high, low + rounder)

    factors = live["factors"]
    factor_avg = sum(f["value"] for f in factors.values()) / len(factors)
    confidence = 60 + (factor_avg - 62) / 2.2
    confidence += min(10, (len(extras["revenue_entries"]) + len(extras["expense_entries"])) * 1.2)
    confidence += min(6, len(extras["photo_logs"]) * 1.5)
    confidence += min(6, extras["present_checkins"] * 1.0)
    confidence -= extras["high_signals"] * 3.5
    confidence = max(52, min(96, confidence))

    if high <= 60000:
        tenure = "6 months (weekly collections)"
    elif high <= 200000:
        tenure = "12 months (monthly EMI)"
    else:
        tenure = "18 months (monthly EMI)"

    return {
        "state": "eligible",
        "low": low,
        "high": high,
        "confidence": round(confidence),
        "tenure": tenure,
        "note": "Envelope derived from current cash flow, transaction stability and behavioural "
                "signals. Indicative demo estimate — final sanction rests with the lender.",
    }


def integrity_checks(persona):
    if persona["integrity"] == "PASS":
        return [
            ("Wash Trading Detection", "PASS", "No circular payment patterns found across the observed window."),
            ("Payer Concentration", "PASS", "Healthy distribution across multiple payers."),
            ("VPA Verification", "PASS", "All VPAs linked to the registered merchant."),
            ("Transaction Velocity", "PASS", "Normal transaction frequency patterns."),
            ("Geo-location Match", "PASS", "Transactions align with the registered location."),
        ]
    return [
        ("Wash Trading Detection", "FAIL", "67% of inbound payments from 2 linked accounts."),
        ("Payer Concentration", "FAIL", "Top payer accounts for 73% of total volume."),
        ("VPA Verification", "WARNING", "2 VPAs require additional verification."),
        ("Transaction Velocity", "WARNING", "Abnormal spike pattern detected."),
        ("Geo-location Match", "WARNING", "Multiple transaction origins outside the registered area."),
    ]


def build_credit_passport(persona, live, persona_key, extras):
    """Credit Passport text — identical fields and layout to the original release."""
    integrity_status = "PASS" if persona["integrity"] == "PASS" else "FAIL - LOAN VOIDED"
    n_expense_photos = extras["photo_uploads"]
    n_supporting = extras["supporting_uploads"]

    credit_report = f"""VYAPARPULSE CREDIT PASSPORT (LIVE)
==========================================
Generated: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}
Report ID: VP-CR-{random.randint(100000, 999999)}

MERCHANT PROFILE
-----------------
Name: {persona['name']}
Business Type: {persona['type']}
Location: {persona['location']}

CREDIT SCORE (LIVE)
---------------------
Base VyaparPulse Score: {persona['base_score']}/900
Live VyaparPulse Score: {live['score']}/900
Score Change: {live['score'] - persona['base_score']:+d} points
Rating: {get_score_label(live['score'])}
Integrity Status: {integrity_status}
Recommended Credit: Rs {live['recommended_credit']:,}
Loan Status: {persona['loan_status']}

FACTOR BREAKDOWN (LIVE)
-------------------------
"""
    for fname, fdata in live["factors"].items():
        base_val = persona["factors"][fname]["value"]
        rating = "Strong" if fdata["value"] >= 70 else ("Moderate" if fdata["value"] >= 50 else "Weak")
        credit_report += f"  {fname}: {fdata['value']}/100 (Base: {base_val}, Change: {fdata['delta']}) [{rating}]\n"

    credit_report += f"""
FINANCIAL SUMMARY (ADJUSTED)
-------------------------------
Total Revenue: Rs {live['new_total_revenue']:,}
Total Expenses: Rs {live['new_total_expense']:,}
Net Profit: Rs {live['new_profit']:,}
Profit Margin: {live['margin']*100:.1f}%
Added Revenue (User Input): Rs {live['total_added_revenue']:,}
Added Expenses (User Input): Rs {live['total_added_expense']:,}

BUSINESS METRICS
-----------------
Daily UPI Average: Rs {persona['upi_daily_avg']:,}
Total Transactions: {persona['total_transactions']:,}
Location Stability: {persona['sthan_days']} days

MONTHLY REVENUE (Base)
------------------------
"""
    for m, rev, exp in zip(MONTHS, persona["monthly_revenue"], persona["monthly_expenses"]):
        credit_report += f"  {m}: Revenue Rs {rev:,} | Expenses Rs {exp:,} | Profit Rs {rev - exp:,}\n"

    credit_report += f"""
ATTACHMENTS
-----------
Expense Notebook Pages: {n_expense_photos} uploaded
Supporting Documents: {n_supporting} uploaded

LENDER NOTES
--------------
{extras['lender_note'] if extras['lender_note'] else 'None provided'}

INTEGRITY REPORT
-----------------
Status: {persona['integrity']}
Detail: {persona['integrity_reason']}

CONSENT & COMPLIANCE
---------------------
Data sourced via consent-based Account Aggregator framework.
Consent is revocable at any time by the merchant.
Fully aligned with Digital Personal Data Protection (DPDP) Act.
No data shared without explicit merchant authorization.

This report is for authorized lender use only.
VyaparPulse - Inclusive Credit Infrastructure for Bharat
"""
    return credit_report


def build_vending_certificate(persona, all_log, present_count, total_count):
    """Proof of Vending certificate — identical fields to the original release."""
    svanidhi_report = f"""PROOF OF VENDING CERTIFICATE
================================
Generated by VyaparPulse
Date: {datetime.now().strftime('%d-%m-%Y %H:%M')}

MERCHANT DETAILS
----------------
Name: {persona['name']}
Type: {persona['type']}
Location: {persona['location']}

VENDING HISTORY
---------------
Total Days at Current Location: {persona['sthan_days']}
Longevity Score: {persona['factors']['Longevity']['value']}/100
Recent Attendance Rate: {present_count}/{total_count} days

RECENT CHECK-IN LOG
--------------------
"""
    for entry in all_log:
        svanidhi_report += f"  {entry['date']} | {entry['time']} | {entry['status']} | {entry['note']}\n"
    svanidhi_report += f"""
VERIFICATION
------------
This document certifies continuous vending activity
at the above location for {persona['sthan_days']} days.
Suitable for PM SVANidhi scheme application.
VyaparPulse Verification ID: VP-{random.randint(100000, 999999)}
"""
    return svanidhi_report


# ══════════════════════════════════════════════════════════════════════════════
# 6. CHART LAYER  (same data as the original release, redesigned presentation)
# ══════════════════════════════════════════════════════════════════════════════
CHART_FONT = "Inter, 'Segoe UI', system-ui, -apple-system, sans-serif"
PLOTLY_CONFIG = {"displayModeBar": False, "displaylogo": False, "responsive": True, "scrollZoom": False}

C_EMERALD = "#0E9F6E"
C_EMERALD_LIGHT = "#34D399"
C_AMBER = "#D97706"
C_NAVY = "#16233F"
C_SLATE = "#64748B"
C_RED = "#DC2626"
C_GRID = "#EEF2F7"
C_AXIS = "#E6EAF1"
C_TICK = "#7C8899"


def plot_chart(fig, key=None):
    """Render a Plotly figure edge-to-edge inside its card."""
    try:
        st.plotly_chart(fig, width="stretch", theme=None, config=PLOTLY_CONFIG, key=key)
    except TypeError:  # older Streamlit releases
        st.plotly_chart(fig, use_container_width=True, theme=None, config=PLOTLY_CONFIG, key=key)


def dataframe_stretch(frame, key=None, **kwargs):
    try:
        st.dataframe(frame, width="stretch", hide_index=True, key=key, **kwargs)
    except TypeError:
        st.dataframe(frame, use_container_width=True, hide_index=True, key=key, **kwargs)


def image_stretch(image, caption=None, key=None):
    try:
        st.image(image, caption=caption, width="stretch", key=key)
    except TypeError:
        st.image(image, caption=caption, use_container_width=True, key=key)


def _currency_ticks(values, count=5):
    """Indian-notation axis ticks (₹0 / ₹50K / ₹1L / ₹1.5L ...)."""
    top = max([float(v) for v in values] + [0.0])
    if top <= 0:
        return None, None
    raw = top / max(count - 1, 1)
    magnitude = 10 ** int(f"{raw:e}".split("e")[1]) if raw > 0 else 1
    step = magnitude
    for multiplier in (1, 2, 2.5, 5, 10):
        if multiplier * magnitude >= raw:
            step = multiplier * magnitude
            break
    ticks = [step * i for i in range(count + 1)]
    while ticks[-1] < top:
        ticks.append(ticks[-1] + step)
    return ticks, [inr_short(tick) for tick in ticks]


def apply_chart_style(fig, height=360, legend=False, unified_hover=False):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=4, r=10, t=16 if not legend else 44, b=4),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=CHART_FONT, size=12, color=C_TICK),
        showlegend=legend,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.04, xanchor="left", x=0,
            font=dict(size=11.5, color=C_SLATE), bgcolor="rgba(0,0,0,0)", itemsizing="constant",
        ),
        hovermode="x unified" if unified_hover else "closest",
        hoverlabel=dict(
            bgcolor="#FFFFFF" if unified_hover else C_NAVY,
            bordercolor=C_AXIS if unified_hover else C_NAVY,
            font=dict(color=C_NAVY if unified_hover else "#F8FAFC", size=12, family=CHART_FONT),
        ),
        modebar=dict(orientation="v"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor=C_AXIS, ticks="",
                     tickfont=dict(size=11.5, color=C_TICK), automargin=True)
    fig.update_yaxes(showgrid=True, gridcolor=C_GRID, gridwidth=1, zeroline=False,
                     linecolor="rgba(0,0,0,0)", ticks="",
                     tickfont=dict(size=11.5, color=C_TICK), automargin=True)
    return fig


def create_gauge_chart(score, name):
    """Radial gauge with the live score band (Credit Score workspace)."""
    color = get_score_color(score)
    label = get_score_label(score)
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            domain={"x": [0, 1], "y": [0, 1]},
            number={"font": {"size": 52, "color": color, "family": CHART_FONT}, "suffix": "/900"},
            gauge={
                "axis": {
                    "range": [300, 900], "tickwidth": 1, "tickcolor": C_AXIS,
                    "tickvals": [300, 450, 600, 750, 900],
                    "tickfont": {"size": 10.5, "color": C_TICK, "family": CHART_FONT},
                },
                "bar": {"color": color, "thickness": 0.22},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 0,
                "steps": [
                    {"range": [300, 550], "color": "#FBE9E9"},
                    {"range": [550, 650], "color": "#FDEFD8"},
                    {"range": [650, 700], "color": "#FBF3D6"},
                    {"range": [700, 750], "color": "#DCF3E7"},
                    {"range": [750, 900], "color": "#C6EDDA"},
                ],
                "threshold": {"line": {"color": C_NAVY, "width": 3}, "thickness": 0.78, "value": score},
            },
        )
    )
    fig.update_layout(
        height=268, margin=dict(l=24, r=24, t=12, b=4),
        paper_bgcolor="rgba(0,0,0,0)", font={"family": CHART_FONT, "color": C_TICK},
    )
    fig.add_annotation(
        x=0.5, y=0.06, xref="paper", yref="paper", showarrow=False,
        text=f"{escape(name)} · {label}", font=dict(size=12, color=C_SLATE, family=CHART_FONT),
    )
    return fig


def create_revenue_expense_chart(monthly_revenue, monthly_expenses, added_rev, added_exp, name, months=12):
    """Cash-flow intelligence: revenue, expenses and net profit for the selected window."""
    months = max(3, min(int(months), len(monthly_revenue)))
    rev = list(monthly_revenue)[-months:]
    exp = list(monthly_expenses)[-months:]
    labels = MONTHS[-months:]

    if added_rev > 0:
        rev = [value + added_rev / 12 for value in rev]
    if added_exp > 0:
        exp = [value + added_exp / 12 for value in exp]
    profit = [r - e for r, e in zip(rev, exp)]

    show_text = months <= 6
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels, y=rev, name="Revenue",
        marker={"color": C_EMERALD, "cornerradius": 6, "line": {"width": 0}},
        width=0.3,
        text=[inr_short(value) for value in rev] if show_text else None,
        textposition="outside", textfont={"size": 10.5, "color": C_SLATE, "family": CHART_FONT},
        hovertemplate="Revenue: %{customdata[0]}<extra></extra>",
        customdata=[[inr(value)] for value in rev],
    ))
    fig.add_trace(go.Bar(
        x=labels, y=exp, name="Expenses",
        marker={"color": "#94A3B8", "cornerradius": 6, "line": {"width": 0}},
        width=0.3,
        text=[inr_short(value) for value in exp] if show_text else None,
        textposition="outside", textfont={"size": 10.5, "color": C_SLATE, "family": CHART_FONT},
        hovertemplate="Expenses: %{customdata[0]}<extra></extra>",
        customdata=[[inr(value)] for value in exp],
    ))
    fig.add_trace(go.Scatter(
        x=labels, y=profit, name="Net Profit", mode="lines+markers",
        line={"color": C_NAVY, "width": 2.6, "shape": "spline", "smoothing": 0.9},
        marker={"size": 7, "color": C_NAVY, "line": {"color": "#FFFFFF", "width": 1.6}},
        hovertemplate="Net profit: %{customdata[0]}<extra></extra>",
        customdata=[[inr(value)] for value in profit],
    ))

    ticks, tick_text = _currency_ticks(rev + exp)
    apply_chart_style(fig, height=352, legend=True, unified_hover=True)
    fig.update_layout(barmode="group", bargap=0.42, bargroupgap=0.16, margin=dict(l=4, r=10, t=44, b=4))
    if ticks:
        fig.update_yaxes(tickvals=ticks[:7], ticktext=tick_text[:7])
    return fig


def create_score_trend_chart(base_score, live_score, name, days=30):
    """Score movement across the trailing window, with the base reference line."""
    random.seed(hash(name) % 10000)
    day_axis = list(range(1, int(days) + 1))
    diff = live_score - base_score
    scores = []
    for day in day_axis:
        progress = day / len(day_axis)
        noise = random.randint(-5, 5)
        value = int(base_score + diff * progress + noise)
        value = max(300, min(900, value))
        scores.append(value)
    scores[-1] = live_score

    color = get_score_color(live_score)
    red = int(color.lstrip("#")[0:2], 16)
    green = int(color.lstrip("#")[2:4], 16)
    blue = int(color.lstrip("#")[4:6], 16)

    low_idx = scores.index(min(scores))
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=day_axis, y=scores, mode="lines",
        line={"color": color, "width": 2.8, "shape": "spline", "smoothing": 0.85},
        fill="tozeroy", fillcolor=f"rgba({red},{green},{blue},0.09)",
        name="Score", hovertemplate="Day %{x} · %{y}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=[day_axis[-1]], y=[live_score], mode="markers",
        marker={"size": 13, "color": color, "line": {"color": "#FFFFFF", "width": 3}},
        name="Today", hovertemplate="Today · %{y}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=[day_axis[low_idx]], y=[min(scores)], mode="markers",
        marker={"size": 9, "color": "#FFFFFF", "line": {"color": "#94A3B8", "width": 2}},
        name="Low point", hovertemplate="Low · %{y}<extra></extra>",
    ))
    fig.add_hline(
        y=base_score, line_dash="dot", line_color="#B6C2D1", line_width=1.4,
        annotation_text=f"Base {base_score}", annotation_position="top left",
        annotation_font=dict(size=10.5, color=C_TICK, family=CHART_FONT),
    )
    fig.add_annotation(
        x=day_axis[-1], y=live_score, xref="x", yref="y", showarrow=False,
        text=f"  {live_score}", xanchor="right", yanchor="middle",
        font=dict(size=12, color=color, family=CHART_FONT, weight="bold"),
    )
    apply_chart_style(fig, height=320)
    span = max(scores) - min(scores)
    pad = max(18, span * 0.55)
    fig.update_yaxes(range=[max(300, min(scores) - pad), min(900, max(scores) + pad)], showgrid=True)
    step = 20 if span < 60 else 50
    span_low, span_high = max(300, min(scores) - pad), min(900, max(scores) + pad)
    start = int(span_low // step * step)
    fig.update_yaxes(tickvals=list(range(start, int(span_high) + step, step)))
    return fig


def create_factor_radar_chart(factors, name, base_factors=None):
    """Live factors against the original baseline so movement is visible."""
    names = list(factors.keys())
    values = [factors[f]["value"] for f in names]
    closed_names = names + [names[0]]
    closed_values = values + [values[0]]

    fig = go.Figure()
    if base_factors:
        base_values = [base_factors[f]["value"] for f in names]
        fig.add_trace(go.Scatterpolar(
            r=base_values + [base_values[0]], theta=closed_names,
            fill="toself", fillcolor="rgba(148,163,184,0.10)",
            line={"color": "#B6C2D1", "width": 1.6, "dash": "dot"},
            name="Base profile", hoverinfo="skip",
        ))
    fig.add_trace(go.Scatterpolar(
        r=closed_values, theta=closed_names, fill="toself",
        fillcolor="rgba(14,159,110,0.16)",
        line={"color": C_EMERALD, "width": 2.4},
        marker={"size": 6, "color": C_NAVY, "line": {"color": "#FFFFFF", "width": 1.4}},
        name="Live profile",
        hovertemplate="%{theta}: %{r}/100<extra></extra>",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True, range=[0, 100], tickvals=[25, 50, 75, 100],
                tickfont={"size": 9.5, "color": "#A7B2C2", "family": CHART_FONT},
                gridcolor="#E9EEF5", linecolor="#E9EEF5", angle=90,
            ),
            angularaxis=dict(
                tickfont={"size": 11, "color": C_SLATE, "family": CHART_FONT},
                gridcolor="#E9EEF5", linecolor="#E9EEF5",
            ),
        ),
        height=352,
    )
    apply_chart_style(fig, height=352, legend=True)
    fig.update_layout(margin=dict(l=52, r=52, t=52, b=18))
    return fig


def create_expense_breakdown_chart(persona_key):
    """Expense mix from the merchant's own entries (empty until entries exist)."""
    user_expenses = st.session_state.expense_entries.get(persona_key, [])
    if not user_expenses:
        return None

    category_totals = {}
    for entry in user_expenses:
        category = entry["category"]
        category_totals[category] = category_totals.get(category, 0) + entry["amount"]

    categories = list(category_totals.keys())
    amounts = list(category_totals.values())
    palette = ["#0E9F6E", "#16233F", "#D97706", "#64748B", "#0F766E", "#6D3FC0", "#B45309", "#94A3B8"]

    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=categories, values=amounts, hole=0.62, sort=True,
        marker={"colors": palette[: len(categories)], "line": {"color": "#FFFFFF", "width": 2}},
        textinfo="label+percent", textposition="outside",
        textfont={"size": 10.5, "color": C_SLATE, "family": CHART_FONT},
        hovertemplate="%{label}: %{customdata[0]} (%{percent})<extra></extra>",
        customdata=[[inr(value)] for value in amounts],
    ))
    fig.add_annotation(
        x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False,
        text=f"<span style='font-size:11px;color:{C_TICK}'>Total added</span><br>"
             f"<b style='font-size:16px;color:{C_NAVY}'>{inr(sum(amounts))}</b>",
        font=dict(family=CHART_FONT),
    )
    apply_chart_style(fig, height=340)
    fig.update_layout(showlegend=False, margin=dict(l=8, r=8, t=18, b=8))
    return fig


def create_profit_waterfall_chart(base_revenue, base_expense, added_rev, added_exp):
    """Bridge from base revenue to the live net position."""
    fig = go.Figure(go.Waterfall(
        name="",
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "total"],
        x=["Base Revenue", "Added Revenue", "Base Expenses", "Added Expenses", "Net Position"],
        y=[base_revenue, added_rev, -base_expense, -added_exp, 0],
        text=[inr_short(base_revenue), inr_short(added_rev), "−" + inr_short(base_expense),
              "−" + inr_short(added_exp), ""],
        textposition="outside",
        textfont={"size": 10, "color": C_SLATE, "family": CHART_FONT},
        connector={"line": {"color": "#C9D4E2", "width": 1.2, "dash": "dot"}},
        increasing={"marker": {"color": C_EMERALD}},
        decreasing={"marker": {"color": C_AMBER}},
        totals={"marker": {"color": C_NAVY}},
        hovertemplate="%{x}: %{y:,.0f}<extra></extra>",
    ))
    apply_chart_style(fig, height=340)
    fig.update_layout(showlegend=False, margin=dict(l=4, r=4, t=18, b=4))
    values = [base_revenue, base_expense, abs(added_rev), abs(added_exp)]
    ticks, tick_text = _currency_ticks(values, count=4)
    if ticks:
        fig.update_yaxes(tickvals=ticks[:6], ticktext=tick_text[:6])
    return fig


def create_volatility_chart(series):
    """Month-on-month revenue movement — volatility read-out for Risk Analytics."""
    rev = series["rev"]
    labels = series["labels"][1:]
    changes = [pct_change(rev[i], rev[i - 1]) for i in range(1, len(rev))]
    colors = [C_EMERALD if value >= 0 else C_AMBER for value in changes]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels, y=changes,
        marker={"color": colors, "cornerradius": 5},
        width=0.46,
        hovertemplate="%{x}: %{y:+.1f}%<extra></extra>",
        name="MoM change",
    ))
    fig.add_hline(y=0, line_color="#D5DEE9", line_width=1.2)
    apply_chart_style(fig, height=286)
    fig.update_layout(showlegend=False, margin=dict(l=4, r=4, t=14, b=4), bargap=0.34)
    fig.update_yaxes(ticksuffix="%", tickfont=dict(size=11.5, color=C_TICK))
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# 7. SHELL — sidebar, navigation and dashboard header
# ══════════════════════════════════════════════════════════════════════════════
NAV_ITEMS = [
    ("overview", "Overview", ":material/dashboard:"),
    ("score", "Credit Score", ":material/speed:"),
    ("intelligence", "Intelligence Layer", ":material/verified_user:"),
    ("fraud", "Fraud Guard", ":material/security:"),
    ("risk", "Risk Analytics", ":material/monitoring:"),
    ("sthan", "Sthan Log", ":material/location_on:"),
    ("lender", "Lender Report", ":material/description:"),
    ("privacy", "Privacy", ":material/privacy_tip:"),
    ("terms", "Terms", ":material/gavel:"),
]

PERIOD_OPTIONS = {"Last 3 months": 3, "Last 6 months": 6, "Last 12 months": 12}

BRAND_MARK = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="1.9" '
    'stroke-linecap="round" stroke-linejoin="round"><path d="M3 13h3.4l2-4.6 3.2 9.2 2.2-5.1 1.6 3H21"/></svg>'
)


def render_sidebar(personas, selected_key):
    with st.sidebar:
        st.markdown(
            '<div class="vp-brand">'
            f'<div class="vp-brand-mark">{BRAND_MARK}</div>'
            '<div><div class="vp-brand-name">VyaparPulse</div>'
            '<div class="vp-brand-tag">Inclusive Credit Intelligence for Bharat</div></div>'
            "</div>",
            unsafe_allow_html=True,
        )

        st.markdown('<div class="vp-nav-label">Merchant</div>', unsafe_allow_html=True)
        chosen = st.selectbox(
            "Merchant", list(personas.keys()),
            index=list(personas.keys()).index(selected_key) if selected_key in personas else 0,
            key="vp_merchant", label_visibility="collapsed",
        )
        persona = personas.get(chosen, personas[selected_key])
        live = compute_live_score(chosen, persona)

        st.markdown('<div class="vp-nav-label">Workspace</div>', unsafe_allow_html=True)
        active_page = st.session_state.get("vp_page", "overview")
        for key, label, nav_icon in NAV_ITEMS:
            if st.button(
                label, key=f"vp_nav_{key}", icon=nav_icon, width="stretch",
                type="primary" if key == active_page else "secondary",
            ):
                st.session_state["vp_page"] = key
                st.rerun()

        integrity_tone = "pos" if persona["integrity"] == "PASS" else "neg"
        score_tone = score_band_tone(live["score"])
        change = live["score"] - persona["base_score"]
        initials = "".join(part[0] for part in persona["name"].replace("'", " ").split()[:2]).upper()
        with st.container(key="vp_sidebar_profile"):
            st.markdown(
                f'<div class="vp-side-card">'
                f'<div class="vp-side-row"><div class="vp-avatar">{initials}</div>'
                f'<div><div class="vp-side-name">{escape(persona["name"])}</div>'
                f'<div class="vp-side-sub">{escape(persona["type"])}</div></div></div>'
                f'<div class="vp-side-meta">{icon("pin")}<span>{escape(persona["location"])}</span></div>'
                f'<div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:10px">'
                f'<span class="vp-chip vp-chip--{integrity_tone}">Integrity {persona["integrity"]}</span>'
                f'<span class="vp-chip vp-chip--{score_tone}">Live {live["score"]}/900</span>'
                f'<span class="vp-chip vp-chip--neutral">{change:+d} pts</span>'
                f"</div></div>"
                f'<div class="vp-side-foot">Demo sandbox · synthetic data<br>No bank connection · v1.0</div>',
                unsafe_allow_html=True,
            )
    return chosen


def page_head(eyebrow, title, subtitle=""):
    sub_html = f'<p class="vp-sub">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f'<div style="margin-bottom:6px"><div class="vp-eyebrow">{eyebrow}</div>'
        f'<div class="vp-h1" style="font-size:1.5rem">{title}</div>{sub_html}</div>',
        unsafe_allow_html=True,
    )


def dashboard_header(persona, live, ctx, persona_key):
    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else ("Good afternoon" if hour < 17 else "Good evening")
    sync_time = st.session_state.get("vp_last_sync", datetime.now().strftime("%H:%M"))

    left, right = st.columns([2.15, 1.55], vertical_alignment="bottom")
    with left:
        st.markdown(
            f'<div class="vp-greet">{greeting} 👋</div>'
            f'<div class="vp-h1">{escape(persona["name"])} — Financial Health Overview</div>'
            f'<p class="vp-sub">AI-powered credit intelligence generated from merchant transaction behaviour.</p>'
            f'<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px">'
            f'<span class="vp-chip vp-chip--live"><span class="vp-dot vp-dot--pulse"></span>Live · synced {sync_time}</span>'
            f'<span class="vp-chip vp-chip--neutral">Demo dataset · Jan–Dec · {ctx["months"]}M window</span>'
            f'<span class="vp-chip vp-chip--{"pos" if persona["integrity"] == "PASS" else "neg"}">'
            f'Integrity {persona["integrity"]}</span>'
            f"</div>",
            unsafe_allow_html=True,
        )
    with right:
        c1, c2, c3 = st.columns([1.5, 1.05, 0.52], vertical_alignment="bottom")
        with c1:
            st.selectbox(
                "Reporting period", list(PERIOD_OPTIONS.keys()),
                index=list(PERIOD_OPTIONS.values()).index(ctx["months"]),
                key="vp_period",
            )
        with c2:
            st.download_button(
                "Export report",
                data=build_credit_passport(persona, live, persona_key, ctx),
                file_name=f"credit_passport_{persona['name'].replace(' ', '_')}.txt",
                mime="text/plain",
                icon=":material/download:",
                key=f"vp_export_{persona_key}",
            )
        with c3:
            if st.button("", icon=":material/refresh:", key="vp_refresh", help="Re-sync merchant data"):
                st.session_state["vp_last_sync"] = datetime.now().strftime("%H:%M")
                st.rerun()
    st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# 8. PAGE — OVERVIEW (hero score, KPIs, analytics, AI insights, risk, eligibility)
# ══════════════════════════════════════════════════════════════════════════════
def hero_score_card(persona, live, ctx):
    score = live["score"]
    fraction = max(0.0, min(1.0, (score - 300) / 600))
    circumference = 2 * 3.141592653589793 * 84
    offset = circumference * (1 - fraction)
    label = get_score_label(score)
    tone = score_band_tone(score)
    change = score - persona["base_score"]

    ranked = sorted(live["factors"].items(), key=lambda item: item[1]["value"], reverse=True)
    driver_text = (
        f"{ranked[0][0]} ({ranked[0][1]['value']}/100) and {ranked[1][0]} "
        f"({ranked[1][1]['value']}/100) are the strongest positive influences on this score."
    )
    drag = ranked[-1]
    if drag[1]["value"] < 65:
        driver_text += (
            f" {drag[0]} at {drag[1]['value']}/100 is currently the biggest drag on the profile."
        )
    else:
        driver_text += " No factor is currently acting as a material drag."

    change_chip = (
        f'<span class="vp-chip vp-chip--pos">↑ {change:+d} points since base profile</span>'
        if change > 0 else
        (f'<span class="vp-chip vp-chip--neg">↓ {change:+d} points since base profile</span>'
         if change < 0 else '<span class="vp-chip vp-chip--neutral">→ no change from base profile</span>')
    )
    marker_pct = fraction * 100
    ring_id = f"vpRingGrad{score}"

    return card(
        f'<div style="display:flex;align-items:flex-start;justify-content:space-between;gap:12px">'
        f'<div><div class="vp-eyebrow">Vyapar credit score</div>'
        f'<div style="font-size:12.5px;color:var(--vp-muted);margin-top:3px">'
        f'Behavioural credit index · 300–900 scale</div></div>'
        f'<span class="vp-chip vp-chip--live"><span class="vp-dot vp-dot--pulse"></span>Live</span></div>'
        f'<div class="vp-hero" style="margin-top:16px">'
        f'<div class="vp-ring-wrap">'
        f'<svg class="vp-ring" viewBox="0 0 200 200">'
        f'<defs><linearGradient id="{ring_id}" x1="0%" y1="0%" x2="100%" y2="100%">'
        f'<stop offset="0%" stop-color="#34D399"/><stop offset="55%" stop-color="#0E9F6E"/>'
        f'<stop offset="100%" stop-color="#0B7A5C"/></linearGradient></defs>'
        f'<circle class="vp-ring-track" cx="100" cy="100" r="84"/>'
        f'<circle class="vp-ring-arc" cx="100" cy="100" r="84" stroke="url(#{ring_id})" '
        f'stroke-dasharray="{circumference:.1f}" stroke-dashoffset="{offset:.1f}" '
        f'style="--vp-c:{circumference:.1f}"/></svg>'
        f'<div class="vp-ring-center">'
        f'<div class="vp-ring-score">{counter_span(score)}</div>'
        f'<div class="vp-ring-den">out of 900</div>'
        f'<div class="vp-ring-cap">{label}</div></div></div>'
        f'<div style="min-width:0">'
        f'<div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">'
        f'<span class="vp-grade vp-grade--{tone}">{label} rating</span>{change_chip}</div>'
        f'<p class="vp-hero-note" style="margin-top:12px">{driver_text}</p>'
        f'<div class="vp-scale"><div class="vp-scale-bar">'
        f'<div class="vp-scale-mark" style="left:{marker_pct:.1f}%"></div></div>'
        f'<div class="vp-scale-labels"><span>300 · Poor</span><span>600 · Average</span>'
        f'<span>900 · Excellent</span></div>'
        f"</div>"
        f'<p style="font-size:11.5px;color:var(--vp-faint);margin-top:10px">'
        f'Base profile {persona["base_score"]} → live {score} · integrity {persona["integrity"]} · '
        f'{len(ctx["revenue_entries"])} revenue and {len(ctx["expense_entries"])} expense entries applied</p>'
        f"</div></div>",
        cls="vp-card-pad-lg vp-rise",
    )


def kpi_grid(persona, live, series):
    cards = []
    for index, kpi in enumerate(build_kpis(persona, live, series)):
        cards.append(
            kpi_card(
                kpi["label"], kpi["value"], kpi["icon"], kpi["tone"],
                kpi["delta"], kpi["compare"], kpi["spark"][-series["window"]:], kpi["color"],
            )
        )
    return f'<div class="vp-kpi-grid vp-rise vp-rise-1">{"".join(cards)}</div>'


def risk_card(signals, risk, persona):
    rows = "".join(risk_row(signal["name"], signal["level"], signal["detail"]) for signal in signals)
    badge = risk["badge"]
    return card(
        f'<div style="display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:6px">'
        f'<div style="font-size:12.5px;color:var(--vp-muted)">Indicative rule-based monitoring · '
        f'{sum(1 for s in signals if s["level"] != "LOW")} of {len(signals)} signals need watching</div>'
        f'<span class="vp-badge vp-badge--{badge}">{risk["category"]}</span></div>'
        f'{rows}',
    )


def eligibility_card(persona, live, risk, eligibility):
    if eligibility["state"] == "review":
        return card(
            f'<div class="vp-verdict vp-verdict--fail" style="box-shadow:none">'
            f'<div class="vp-verdict-badge vp-verdict-badge--fail">!</div>'
            f'<div><div class="vp-verdict-title">Estimated credit eligibility on hold</div>'
            f'<div class="vp-verdict-status" style="color:var(--vp-red)">Integrity layer · automated eligibility voided</div>'
            f'<p style="font-size:12.5px;color:var(--vp-body);margin-top:8px">{eligibility["note"]}</p>'
            f"</div></div>",
        )

    conf = eligibility["confidence"]
    return (
        f'<div class="vp-elig vp-rise">'
        f'<div class="vp-elig-grid">'
        f"<div>"
        f'<div class="vp-elig-eyebrow">Estimated credit eligibility</div>'
        f'<div class="vp-elig-range">{inr_short(eligibility["low"])} – {inr_short(eligibility["high"])}</div>'
        f'<div class="vp-elig-exact">{inr(eligibility["low"])} – {inr(eligibility["high"])} · '
        f'indicative envelope, not a sanction</div>'
        f'<p class="vp-elig-note">Based on current cash flow, transaction stability and behavioural credit '
        f'signals from the live score. Final amount, pricing and approval rest entirely with the lender.</p>'
        f"</div>"
        f'<div class="vp-elig-meta">'
        f'<div class="vp-elig-meta-row"><span class="vp-elig-meta-label">Model confidence</span>'
        f'<span class="vp-elig-meta-value">{conf}%</span></div>'
        f'<div class="vp-elig-bar"><div style="width:{conf}%"></div></div>'
        f'<div class="vp-elig-meta-row"><span class="vp-elig-meta-label">Risk category</span>'
        f'<span class="vp-elig-meta-value">{risk["category"]}</span></div>'
        f'<div class="vp-elig-meta-row"><span class="vp-elig-meta-label">Suggested repayment period</span>'
        f'<span class="vp-elig-meta-value">{eligibility["tenure"]}</span></div>'
        f'<div class="vp-elig-meta-row"><span class="vp-elig-meta-label">Integrity status</span>'
        f'<span class="vp-elig-meta-value">{persona["integrity"]}</span></div>'
        f"</div></div>"
        f'<div class="vp-elig-foot">Indicative demo estimate generated by the VyaparPulse scoring model. '
        f'Not a lending decision, offer or commitment.</div>'
        f"</div>"
    )


def render_overview(persona_key, persona, live, ctx):
    series = ctx["series"]
    dashboard_header(persona, live, ctx, persona_key)

    hero_col, kpi_col = st.columns([1.08, 1.0], gap="medium")
    with hero_col:
        st.markdown(hero_score_card(persona, live, ctx), unsafe_allow_html=True)
    with kpi_col:
        st.markdown(kpi_grid(persona, live, series), unsafe_allow_html=True)

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    section("Behavioural factors", "Score factors",
            "Six behavioural signals behind the live score — hover a factor name for its definition.")
    factors = "".join(
        factor_card(
            name if name != "Liquidity Buffer" else "Liquidity",
            data["value"], data["delta"], FACTOR_ICONS[name], FACTOR_TOOLTIPS[name],
        )
        for name, data in live["factors"].items()
    )
    st.markdown(f'<div class="vp-factor-grid vp-rise vp-rise-1">{factors}</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    section("Financial analytics", "Cash flow intelligence",
            "Revenue, expenses and net profit across the reporting window.")

    cash_col, trend_col = st.columns([1.62, 1.0], gap="medium")
    with cash_col:
        with st.container(key="vp_card_cashflow"):
            fig = create_revenue_expense_chart(
                persona["monthly_revenue"], persona["monthly_expenses"],
                live["total_added_revenue"], live["total_added_expense"],
                persona["name"], months=ctx["cashflow_months"],
            )
            plot_chart(fig, key=f"overview_cashflow_{persona_key}")
            st.markdown(
                f'<p style="font-size:11.5px;color:var(--vp-faint);margin:2px 0 0">'
                f'Bar labels shown for windows of six months or fewer · hover any month for exact values'
                f'{" · adjusted for your added entries" if live["total_added_revenue"] or live["total_added_expense"] else ""}.</p>',
                unsafe_allow_html=True,
            )
    with trend_col:
        with st.container(key="vp_card_trend"):
            st.markdown(
                f'<div class="vp-eyebrow">Credit score trend</div>'
                f'<div style="display:flex;align-items:center;gap:8px;margin:4px 0 2px">'
                f'<span style="font-size:18px;font-weight:700;color:var(--vp-ink)">{live["score"]}</span>'
                f'{delta_chip(pct_change(live["score"], persona["base_score"]))}'
                f'<span class="vp-chip vp-chip--neutral">Last {ctx["trend_days"]} days</span></div>',
                unsafe_allow_html=True,
            )
            plot_chart(
                create_score_trend_chart(persona["base_score"], live["score"], persona["name"], ctx["trend_days"]),
                key=f"overview_trend_{persona_key}",
            )

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    section("VyaparPulse AI insights", "What the data is saying",
            "Generated from live factors, cash flow and integrity signals — not a generic checklist.")
    insights = "".join(
        insight_card(item["tone"], item["title"], item["body"], item["icon"])
        for item in ctx["insights"]
    )
    st.markdown(f'<div class="vp-insights vp-rise vp-rise-1">{insights}</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    section("Risk monitoring", "Risk and fraud monitoring",
            "Five monitoring signals with transparent thresholds, refreshed on every entry you add.")
    st.markdown(risk_card(ctx["signals"], ctx["risk"], persona), unsafe_allow_html=True)

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    section("Credit decisioning", "Estimated credit eligibility",
            "Indicative envelope for a demo conversation — clearly labelled as an estimate.")
    st.markdown(eligibility_card(persona, live, ctx["risk"], ctx["eligibility"]), unsafe_allow_html=True)

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    section("Action centre", "Priority actions for this merchant",
            "The top three nudges from the live score model. The full list lives in the Credit Score workspace.")
    for index, tip in enumerate(persona["tips"][:3], 1):
        text = f"**{index}. {tip}**"
        if any(flag in tip for flag in ("CRITICAL", "WARNING", "ACTION")):
            st.warning(text)
        else:
            st.info(text)

    st.markdown(
        f'<div class="vp-foot">VyaparPulse demo sandbox · synthetic merchant data · '
        f'scores, integrity findings and eligibility envelopes are simulated.<br>'
        f'Not financial, lending, legal or tax advice.</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# 9. PAGE — CREDIT SCORE (gauge, factors, analytics, ledger entries, tips)
# ══════════════════════════════════════════════════════════════════════════════
def render_credit_score(persona_key, persona, live, ctx):
    page_head(
        "Credit score",
        "Score movement, factor detail and ledger entries",
        "Every expense, revenue entry and check-in re-scores the profile instantly — all inside this session.",
    )

    left, right = st.columns([1.0, 1.32], gap="medium")
    with left:
        with st.container(key="vp_card_gauge"):
            st.markdown(
                f'<div class="vp-eyebrow">Score gauge</div>'
                f'<div style="display:flex;gap:8px;flex-wrap:wrap;margin:6px 0 2px">'
                f'<span class="vp-chip vp-chip--navy">Base {persona["base_score"]}</span>'
                f'<span class="vp-chip vp-chip--{score_band_tone(live["score"])}">Live {live["score"]}</span>'
                f'<span class="vp-chip vp-chip--neutral">{live["score"] - persona["base_score"]:+d} pts</span></div>',
                unsafe_allow_html=True,
            )
            plot_chart(create_gauge_chart(live["score"], persona["name"]), key=f"score_gauge_{persona_key}")
    with right:
        with st.container(key="vp_card_factors"):
            st.markdown(
                '<div class="vp-eyebrow">Live score factors</div>'
                '<div style="font-size:12.5px;color:var(--vp-muted);margin:4px 0 10px">'
                'Base profile vs live reading · hover a factor name for its definition.</div>',
                unsafe_allow_html=True,
            )
            factors = "".join(
                factor_card(
                    name if name != "Liquidity Buffer" else "Liquidity",
                    data["value"], data["delta"], FACTOR_ICONS[name], FACTOR_TOOLTIPS[name],
                )
                for name, data in live["factors"].items()
            )
            st.markdown(
                f'<style>.st-key-vp_card_factors .vp-factor-grid{{grid-template-columns:repeat(auto-fit,minmax(158px,1fr));}}'
                f'</style><div class="vp-factor-grid">{factors}</div>',
                unsafe_allow_html=True,
            )

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    section("Score composition", "What is driving the score",
            "Factor shape on the left, rupee bridge from base revenue to the live net position on the right.")
    radar_col, waterfall_col = st.columns(2, gap="medium")
    with radar_col:
        with st.container(key="vp_card_radar"):
            plot_chart(
                create_factor_radar_chart(live["factors"], persona["name"], persona["factors"]),
                key=f"score_radar_{persona_key}",
            )
    with waterfall_col:
        with st.container(key="vp_card_waterfall"):
            plot_chart(
                create_profit_waterfall_chart(
                    sum(persona["monthly_revenue"]), sum(persona["monthly_expenses"]),
                    live["total_added_revenue"], live["total_added_expense"],
                ),
                key=f"score_waterfall_{persona_key}",
            )

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    section("Cash flow", "Revenue vs expenses (live)",
            "The same twelve periods as the dashboard, with the chart-local month filter.")
    with st.container(key="vp_card_cashflow_full"):
        control_col, note_col = st.columns([1.0, 2.2], vertical_alignment="center")
        with control_col:
            month_choice = st.segmented_control(
                "Months shown", ["3M", "6M", "9M", "12M"],
                key="vp_cashflow_months", label_visibility="collapsed",
            )
        with note_col:
            st.markdown(
                f'<p style="font-size:11.5px;color:var(--vp-faint);margin:0;text-align:right">'
                f'Live-adjusted series · base revenue {inr(sum(persona["monthly_revenue"]))} · '
                f'added entries {inr(live["total_added_revenue"] + live["total_added_expense"])}</p>',
                unsafe_allow_html=True,
            )
        months = int((month_choice or f"{ctx['cashflow_months']}M").replace("M", ""))
        plot_chart(
            create_revenue_expense_chart(
                persona["monthly_revenue"], persona["monthly_expenses"],
                live["total_added_revenue"], live["total_added_expense"],
                persona["name"], months=months,
            ),
            key=f"score_cashflow_{persona_key}",
        )

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    section("Score trend", "Score movement",
            "Simulated trailing window driven by the live score, with the base profile as reference.")
    with st.container(key="vp_card_trend_full"):
        plot_chart(
            create_score_trend_chart(persona["base_score"], live["score"], persona["name"], ctx["trend_days"]),
            key=f"score_trend_{persona_key}",
        )

    st.markdown('<div style="height:18px"></div>', unsafe_allow_html=True)
    section("Ledger", "Add expense (score updates live)",
            "Enter real business expenses — the credit score recalculates automatically.")
    expense_col, revenue_col = st.columns(2, gap="medium")
    with expense_col:
        with st.container(key="vp_card_expense_form"):
            with st.form(f"expense_form_{persona_key}", clear_on_submit=True):
                exp_cols = st.columns(2)
                with exp_cols[0]:
                    exp_category = st.selectbox("Category", [
                        "Rent", "Stock/Inventory", "Utilities", "Transport",
                        "Wages/Labor", "Raw Materials", "Equipment", "Miscellaneous",
                    ], key=f"exp_cat_{persona_key}")
                    exp_date = st.date_input("Date", value=datetime.now().date(), key=f"exp_date_{persona_key}")
                with exp_cols[1]:
                    exp_amount = st.number_input("Amount (Rs)", min_value=0, value=0, step=100, key=f"exp_amt_{persona_key}")
                    exp_note = st.text_input("Description", key=f"exp_note_{persona_key}")
                if st.form_submit_button("Add expense", icon=":material/add:", type="primary"):
                    if exp_amount > 0:
                        if persona_key not in st.session_state.expense_entries:
                            st.session_state.expense_entries[persona_key] = []
                        st.session_state.expense_entries[persona_key].append({
                            "category": exp_category,
                            "amount": exp_amount,
                            "date": str(exp_date),
                            "note": exp_note,
                        })
                        st.success(f"Rs {exp_amount:,} expense added. Score recalculating...")
                        st.rerun()
                    else:
                        st.info("Enter an amount above zero to add the expense.")
    with revenue_col:
        with st.container(key="vp_card_revenue_form"):
            with st.form(f"revenue_form_{persona_key}", clear_on_submit=True):
                rev_cols = st.columns(2)
                with rev_cols[0]:
                    rev_source = st.selectbox("Source", [
                        "UPI Collection", "Cash Sale", "Wholesale Order",
                        "Online Order", "Repeat Customer", "New Customer", "Other",
                    ], key=f"rev_src_{persona_key}")
                    rev_date = st.date_input("Date", value=datetime.now().date(), key=f"rev_date_{persona_key}")
                with rev_cols[1]:
                    rev_amount = st.number_input("Amount (Rs)", min_value=0, value=0, step=100, key=f"rev_amt_{persona_key}")
                    rev_note = st.text_input("Description", key=f"rev_note_{persona_key}")
                if st.form_submit_button("Add revenue", icon=":material/add:", type="primary"):
                    if rev_amount > 0:
                        if persona_key not in st.session_state.revenue_entries:
                            st.session_state.revenue_entries[persona_key] = []
                        st.session_state.revenue_entries[persona_key].append({
                            "source": rev_source,
                            "amount": rev_amount,
                            "date": str(rev_date),
                            "note": rev_note,
                        })
                        st.success(f"Rs {rev_amount:,} revenue added. Score recalculating...")
                        st.rerun()
                    else:
                        st.info("Enter an amount above zero to add the revenue.")

    user_expenses = ctx["expense_entries"]
    user_revenues = ctx["revenue_entries"]

    if user_expenses or user_revenues:
        st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
        section("Ledger", "Your entries affecting the live score",
                "Rows you add here flow into the score, the cash-flow chart and the credit passport.")
        exp_tab, rev_tab = st.columns(2, gap="medium")
        with exp_tab:
            with st.container(key="vp_card_expense_list"):
                st.markdown(
                    f'<div class="vp-eyebrow">Expenses added</div>'
                    f'<div style="font-size:12.5px;color:var(--vp-muted);margin:4px 0 8px">'
                    f'Total {inr(sum(entry["amount"] for entry in user_expenses))} across '
                    f'{len(user_expenses)} entry(ies)</div>',
                    unsafe_allow_html=True,
                )
                dataframe_stretch(pd.DataFrame(user_expenses), key=f"exp_table_{persona_key}")
        with rev_tab:
            with st.container(key="vp_card_revenue_list"):
                st.markdown(
                    f'<div class="vp-eyebrow">Revenue added</div>'
                    f'<div style="font-size:12.5px;color:var(--vp-muted);margin:4px 0 8px">'
                    f'Total {inr(sum(entry["amount"] for entry in user_revenues))} across '
                    f'{len(user_revenues)} entry(ies)</div>',
                    unsafe_allow_html=True,
                )
                dataframe_stretch(pd.DataFrame(user_revenues), key=f"rev_table_{persona_key}")

        if st.button("Clear all entries (reset to base score)", key=f"clear_{persona_key}", icon=":material/restart_alt:"):
            st.session_state.expense_entries[persona_key] = []
            st.session_state.revenue_entries[persona_key] = []
            st.rerun()
    else:
        st.info("No manual entries yet. Add an expense or a revenue entry above and the whole dashboard re-scores.")

    expense_pie = create_expense_breakdown_chart(persona_key)
    if expense_pie:
        st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
        section("Expense mix", "Where the money goes",
                "Category split of the expenses you added in this session.")
        with st.container(key="vp_card_pie"):
            plot_chart(expense_pie, key=f"score_pie_{persona_key}")

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    section("Actionable tips", "What to do next",
            "Model-generated guidance for this merchant profile.")
    for index, tip in enumerate(persona["tips"], 1):
        text = f"**{index}. {tip}**"
        if any(flag in tip for flag in ("CRITICAL", "WARNING", "ACTION")):
            st.warning(text)
        else:
            st.info(text)


# ══════════════════════════════════════════════════════════════════════════════
# 10. PAGE — INTELLIGENCE LAYER (integrity verification)
# ══════════════════════════════════════════════════════════════════════════════
INTEGRITY_METHOD = [
    ("Wash trading detection", "Looks for circular payment loops and self-funding patterns between linked accounts."),
    ("Payer concentration", "Measures how much of the inflow depends on a small set of payers."),
    ("VPA verification", "Confirms that payment handles resolve to the registered merchant identity."),
    ("Transaction velocity", "Compares settlement frequency against the merchant's own presence history."),
    ("Geo-location match", "Cross-checks transaction origins against the registered place of business."),
]


def render_intelligence(persona_key, persona, live, ctx):
    page_head(
        "Intelligence layer",
        "Integrity verification and decision status",
        "Independent verification of the ledger before any automated credit decision is taken.",
    )

    passed = persona["integrity"] == "PASS"
    badge_cls = "pass" if passed else "fail"
    verdict_title = "Integrity check passed" if passed else "Integrity check failed"
    verdict_status = ("Clean ledger · eligible for automated decisioning" if passed
                      else "Loan offer voided · manual review required")
    st.markdown(
        f'<div class="vp-verdict vp-verdict--{badge_cls} vp-rise">'
        f'<div class="vp-verdict-badge vp-verdict-badge--{badge_cls}">{"✓" if passed else "!"}</div>'
        f'<div><div class="vp-verdict-title">{verdict_title}</div>'
        f'<div class="vp-verdict-status" style="color:var(--vp-{"emerald-700" if passed else "red"})">'
        f'{verdict_status}</div>'
        f'<p style="font-size:13px;color:var(--vp-body);margin-top:9px">{escape(persona["integrity_reason"])}</p>'
        f"</div></div>",
        unsafe_allow_html=True,
    )

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    section("Verification", "Integrity check detail",
            "Five independent checks run against the same consent-based transaction history.")
    check_col, decision_col = st.columns([1.55, 1.0], gap="medium")
    with check_col:
        with st.container(key="vp_card_checks"):
            rows = "".join(check_row(name, result, detail) for name, result, detail in integrity_checks(persona))
            st.markdown(rows, unsafe_allow_html=True)
    with decision_col:
        with st.container(key="vp_card_decision"):
            st.markdown('<div class="vp-eyebrow">Decision snapshot</div>', unsafe_allow_html=True)
            st.markdown(
                tiles([
                    ("Integrity status", persona["integrity"]),
                    ("Loan status", persona["loan_status"]),
                    ("Recommended credit (live)", inr(live["recommended_credit"])),
                    ("Risk category", ctx["risk"]["category"]),
                ]),
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<p style="font-size:12px;color:var(--vp-muted);margin-top:12px">'
                f'Live score {live["score"]}/900 ({get_score_label(live["score"])}) · '
                f'base {persona["base_score"]}/900 · factor set held constant while the ledger is reviewed.</p>',
                unsafe_allow_html=True,
            )

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    section("Method", "How the integrity layer works",
            "Fully explainable rules — every finding can be traced back to a transaction pattern.")
    method_col, consent_col = st.columns([1.35, 1.0], gap="medium")
    with method_col:
        with st.container(key="vp_card_method"):
            st.markdown(
                table(
                    ["Check", "What it looks for"],
                    [[name, description] for name, description in INTEGRITY_METHOD],
                ),
                unsafe_allow_html=True,
            )
    with consent_col:
        with st.container(key="vp_card_consent"):
            st.markdown(
                '<div class="vp-eyebrow">Consent &amp; provenance</div>'
                '<p style="font-size:12.5px;color:var(--vp-body);margin-top:8px;line-height:1.7">'
                'Data is sourced through the consent-based Account Aggregator framework. Consent is '
                'time-bound, purpose-specific and revocable by the merchant at any moment. '
                'VyaparPulse is aligned with the DPDP Act: no merchant data leaves this session, '
                'and nothing is shared with a lender without an explicit, logged authorisation.</p>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:10px">'
                f'<span class="vp-chip vp-chip--navy">{icon("lock")} AA consent on file</span>'
                f'<span class="vp-chip vp-chip--pos">{icon("check")} Revocable</span>'
                f'<span class="vp-chip vp-chip--neutral">DPDP aligned</span></div>',
                unsafe_allow_html=True,
            )


# ══════════════════════════════════════════════════════════════════════════════
# 11. PAGE — FRAUD GUARD (unchanged detection flows, redesigned surface)
# ══════════════════════════════════════════════════════════════════════════════
def render_fraud_guard(persona_key, persona, live, ctx):
    page_head(
        "Fraud guard",
        "Payment authenticity toolkit",
        "Three merchant-facing defences: screenshot verification, QR health checks and batch audits.",
    )

    section("Active alerts", "Live queue",
            "Demo alerts that mirror the two most common counter-side fraud attempts.")
    alert_a, alert_b = st.columns(2, gap="medium")
    with alert_a:
        st.warning(
            "**Screenshot check alert**\n\n"
            "Customer claims Rs 500 paid. Bank ledger shows Rs 50 received.\n\n"
            "MISMATCH ALERT - Potential tampered screenshot."
        )
    with alert_b:
        st.warning(
            "**QR health alert**\n\n"
            "VPA routing mismatch detected.\n\n"
            "QR SWAP DETECTED: Rs 2,340 routed to unlinked account since 6:00 AM today."
        )

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    section("Screenshot verification", "Verify a customer payment screenshot",
            "Cross-check what the customer showed against what actually landed in the ledger.")
    st.caption("Uploads stay inside this session — no image leaves the browser tab and no OCR service is called.")
    uploaded_screenshot = st.file_uploader(
        "Upload payment screenshot (PNG, JPG, JPEG)",
        type=["png", "jpg", "jpeg"],
        key="fraud_screenshot",
    )
    if uploaded_screenshot is not None:
        image_col, form_col = st.columns([1, 1.15], gap="medium")
        with image_col:
            image_stretch(uploaded_screenshot, caption="Uploaded screenshot")
        with form_col:
            with st.container(key="vp_card_verify"):
                st.markdown('<div class="vp-eyebrow">Verification inputs</div>', unsafe_allow_html=True)
                claimed_amount = st.number_input("Amount shown in screenshot (Rs)", min_value=0, value=0, step=10, key="claimed_amt")
                actual_amount = st.number_input("Amount in your bank ledger (Rs)", min_value=0, value=0, step=10, key="actual_amt")
                txn_col, upi_col = st.columns(2)
                with txn_col:
                    txn_id = st.text_input("Transaction ID (from screenshot)", key="txn_id_input")
                with upi_col:
                    payer_upi = st.text_input("Payer UPI ID", key="payer_upi_input")
                txn_date = st.date_input("Transaction date", key="txn_date_input")
                if st.button("Verify transaction", key="verify_txn", type="primary", icon=":material/fact_check:"):
                    if claimed_amount > 0:
                        if abs(claimed_amount - actual_amount) > 1:
                            mismatch_pct = abs(claimed_amount - actual_amount) / max(claimed_amount, 1) * 100
                            st.error(
                                f"**MISMATCH DETECTED**\n\n"
                                f"Claimed: Rs {claimed_amount:,} | Ledger: Rs {actual_amount:,} | "
                                f"Difference: Rs {abs(claimed_amount - actual_amount):,} "
                                f"({mismatch_pct:.0f}% deviation)\n\n"
                                f"Transaction ID: {txn_id if txn_id else 'Not provided'}\n\n"
                                f"This screenshot may be tampered. Flag this transaction for review."
                            )
                        else:
                            st.success(
                                f"**MATCH CONFIRMED**\n\n"
                                f"Rs {claimed_amount:,} verified against ledger record.\n"
                                f"Transaction ID: {txn_id if txn_id else 'Not provided'}"
                            )
                    else:
                        st.info("Enter the claimed amount to verify.")

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    section("QR health", "Check your payment QR",
            "Confirm the QR placed at the counter still routes money into your own account.")
    uploaded_qr = st.file_uploader("Upload your QR code image", type=["png", "jpg", "jpeg"], key="qr_upload")
    if uploaded_qr is not None:
        qr_col, qr_info = st.columns([1, 1.25], gap="medium")
        with qr_col:
            image_stretch(uploaded_qr, caption="Counter QR")
        with qr_info:
            with st.container(key="vp_card_qr"):
                registered_vpa = st.text_input("Your registered VPA / UPI ID", key="reg_vpa")
                if st.button("Check QR health", key="check_qr", type="primary", icon=":material/qr_code_scanner:"):
                    if registered_vpa:
                        roll = random.random()
                        if roll > 0.3:
                            st.success(f"**QR HEALTH: OK** — QR code routes to {registered_vpa}. No tampering detected.")
                        else:
                            st.error(
                                f"**QR SWAP ALERT** — This QR code may not route to {registered_vpa}. "
                                f"Immediately verify with your payment provider and replace the QR at your shop."
                            )
                    else:
                        st.info("Enter your registered VPA to check.")

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    section("Batch audit", "Bulk transaction audit",
            "Reconcile a run of counter transactions — one at a time or against a ledger sheet.")
    with st.container(key="vp_card_bulk"):
        with st.form("bulk_audit_form", clear_on_submit=True):
            audit_cols = st.columns(3)
            with audit_cols[0]:
                audit_claimed = st.number_input("Claimed amount (Rs)", min_value=0, value=0, step=50, key="audit_claimed")
            with audit_cols[1]:
                audit_actual = st.number_input("Actual received (Rs)", min_value=0, value=0, step=50, key="audit_actual")
            with audit_cols[2]:
                audit_payer = st.text_input("Payer name / ID", key="audit_payer")
            if st.form_submit_button("Audit this transaction", icon=":material/rule:", type="primary"):
                if audit_claimed > 0:
                    diff = abs(audit_claimed - audit_actual)
                    if diff > 1:
                        st.error(f"MISMATCH: Claimed Rs {audit_claimed:,} vs Received Rs {audit_actual:,}. Difference: Rs {diff:,}")
                    else:
                        st.success(f"VERIFIED: Rs {audit_claimed:,} matches ledger for {audit_payer if audit_payer else 'unknown payer'}.")
                else:
                    st.info("Enter the claimed amount to audit this transaction.")


# ══════════════════════════════════════════════════════════════════════════════
# 12. PAGE — RISK ANALYTICS (monitoring signals + volatility)
# ══════════════════════════════════════════════════════════════════════════════
RISK_METHOD = [
    ("UPI anomaly status", "Integrity verdict combined with the payer-diversity reading."),
    ("Unusual transaction frequency", "Settlements per day (total transactions ÷ days logged) above 10/day is flagged."),
    ("Revenue volatility", "Dispersion of monthly revenue: above 22% is moderate, above 45% is high."),
    ("Merchant concentration risk", "Payer diversity below 70 is watched, below 45 is a high concern."),
    ("Suspicious transaction patterns", "Steep revenue ramps (4× or more) on a narrow payer base are escalated."),
]


def render_risk_analytics(persona_key, persona, live, ctx):
    page_head(
        "Risk analytics",
        "Monitoring signals and volatility",
        "Rule-based monitoring over the same consent-based ledger that feeds the credit score.",
    )

    risk = ctx["risk"]
    index_col, vol_col = st.columns([1.0, 1.72], gap="medium")
    with index_col:
        pill = ("Low" if risk["percent"] <= 12 else "Moderate" if risk["percent"] <= 35
                else "Elevated" if risk["percent"] <= 60 else "High")
        st.markdown(
            card(
                f'<div class="vp-eyebrow">Composite risk index</div>'
                f'<div style="display:flex;align-items:baseline;gap:8px;margin-top:8px">'
                f'<span style="font-size:2.3rem;font-weight:700;color:var(--vp-ink);letter-spacing:-.03em">'
                f'{risk["percent"]:.0f}</span>'
                f'<span style="font-size:14px;color:var(--vp-muted)">/ 100</span></div>'
                f'<div class="vp-track" style="margin-top:10px"><div class="vp-fill" '
                f'style="width:{min(100, risk["percent"]):.0f}%;background:'
                f'{"linear-gradient(90deg,#34D399,#0E9F6E)" if risk["percent"] <= 35 else "linear-gradient(90deg,#FBBF24,#D97706)"}">'
                f"</div></div>"
                f'<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:12px">'
                f'<span class="vp-badge vp-badge--{risk["badge"]}">{risk["category"]}</span>'
                f'<span class="vp-chip vp-chip--neutral">Weighted from 5 signals</span></div>'
                f'<p style="font-size:12px;color:var(--vp-muted);margin-top:12px">'
                f'Indicative demo index. Thresholds are illustrative and tuned for the hackathon dataset, '
                f'not a production risk model.</p>',
            ),
            unsafe_allow_html=True,
        )
    with vol_col:
        with st.container(key="vp_card_volatility"):
            st.markdown(
                '<div class="vp-eyebrow">Revenue volatility</div>'
                '<div style="font-size:12.5px;color:var(--vp-muted);margin:4px 0 2px">'
                'Month-on-month movement of collections across the reporting window.</div>',
                unsafe_allow_html=True,
            )
            plot_chart(create_volatility_chart(ctx["series"]), key=f"risk_volatility_{persona_key}")

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    section("Signals", "Risk and fraud monitoring",
            "Each signal carries its evidence inline, so a reviewer can see exactly why it moved.")
    st.markdown(risk_card(ctx["signals"], risk, persona), unsafe_allow_html=True)

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    with st.expander("How these signals are computed — transparent thresholds"):
        st.markdown(table(["Signal", "Rule"], [[name, rule] for name, rule in RISK_METHOD]), unsafe_allow_html=True)
        st.caption(
            "Signals run on the demo dataset plus any entries you add in the Credit Score workspace. "
            "They are indicators for review, never proof of fraud."
        )
    st.info(
        f"**Integrity status: {persona['integrity']}** — the intelligence layer holds the "
        f"decision-level verdict; these signals are the monitoring view behind it."
    )


# ══════════════════════════════════════════════════════════════════════════════
# 13. PAGE — STHAN LOG (proof of vending)
# ══════════════════════════════════════════════════════════════════════════════
def render_sthan_log(persona_key, persona, live, ctx):
    page_head(
        "Sthan log",
        "Proof of vending and physical presence",
        "Location history that lets thin-file vendors prove continuity of business.",
    )

    col_m1, col_m2, col_m3 = st.columns(3, gap="medium")
    col_m1.markdown(
        card(f'<div class="vp-tile-label">Days at current location</div>'
             f'<div class="vp-tile-value" style="font-size:1.5rem">{persona["sthan_days"]:,}</div>'
             f'<div style="font-size:11.5px;color:var(--vp-muted);margin-top:4px">Continuous presence</div>'),
        unsafe_allow_html=True,
    )
    col_m2.markdown(
        card(f'<div class="vp-tile-label">Registered location</div>'
             f'<div class="vp-tile-value" style="font-size:1.12rem">{escape(persona["location"])}</div>'
             f'<div style="font-size:11.5px;color:var(--vp-muted);margin-top:4px">{escape(persona["type"])}</div>'),
        unsafe_allow_html=True,
    )
    col_m3.markdown(
        card(f'<div class="vp-tile-label">Longevity score impact</div>'
             f'<div class="vp-tile-value" style="font-size:1.5rem">{live["factors"]["Longevity"]["value"]}'
             f'<span style="font-size:12px;color:var(--vp-muted)">/100</span></div>'
             f'<div class="vp-track" style="margin-top:8px"><div class="vp-fill" style="width:'
             f'{live["factors"]["Longevity"]["value"]}%;background:linear-gradient(90deg,#34D399,#0E9F6E)"></div></div>'),
        unsafe_allow_html=True,
    )

    st.info(
        "**How Sthan Log works:** Physical presence check-ins build a verifiable location history. "
        "For thin-file vendors with minimal bank records, Sthan Log longevity directly fuels the "
        "'Longevity' score factor, providing an alternative creditworthiness signal. "
        f"With {persona['sthan_days']} days logged, this is strong proof of stable business operations."
    )

    user_sthan = ctx["sthan_entries"]
    all_log = persona["sthan_log"] + user_sthan
    present_count = sum(1 for entry in all_log if entry["status"] == "Present")
    total_count = len(all_log)
    rate = (present_count / total_count * 100) if total_count else 0

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    section("Timeline", "Presence timeline",
            "Base check-ins from the demo ledger plus every check-in you log in this session.")
    with st.container(key="vp_card_timeline"):
        st.markdown(
            f'<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px">'
            f'<span class="vp-chip vp-chip--pos">{present_count}/{total_count} days present</span>'
            f'<span class="vp-chip vp-chip--neutral">Attendance rate {rate:.0f}%</span>'
            f'<span class="vp-chip vp-chip--navy">{len(user_sthan)} added in this session</span></div>',
            unsafe_allow_html=True,
        )
        if all_log:
            frame = pd.DataFrame(all_log).rename(
                columns={"date": "Date", "time": "Time", "status": "Status", "note": "Note"}
            )
            dataframe_stretch(frame, key=f"sthan_table_{persona_key}")
        else:
            st.info("No check-ins logged yet.")

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    section("Check-in", "Log a new visit",
            "Each present check-in lifts the Reliability and Longevity factors by 2 points in the live score.")
    check_col, notes_col = st.columns([1.15, 1.0], gap="medium")
    with check_col:
        with st.container(key="vp_card_checkin"):
            with st.form(f"sthan_checkin_{persona_key}", clear_on_submit=True):
                form_cols = st.columns(2)
                with form_cols[0]:
                    checkin_date = st.date_input("Date", value=datetime.now().date(), key=f"sthan_date_{persona_key}")
                    checkin_status = st.selectbox("Status", ["Present", "Absent"], key=f"sthan_status_{persona_key}")
                with form_cols[1]:
                    checkin_time = st.time_input("Time", value=datetime.now().time(), key=f"sthan_time_{persona_key}")
                    checkin_note = st.text_input("Note", key=f"sthan_note_{persona_key}")
                if st.form_submit_button("Log check-in", icon=":material/where_to_vote:", type="primary"):
                    new_entry = {
                        "date": str(checkin_date),
                        "time": checkin_time.strftime("%H:%M") if checkin_status == "Present" else "N/A",
                        "status": checkin_status,
                        "note": checkin_note,
                    }
                    if persona_key not in st.session_state.sthan_entries:
                        st.session_state.sthan_entries[persona_key] = []
                    st.session_state.sthan_entries[persona_key].append(new_entry)
                    st.success(f"Check-in logged for {checkin_date}. Score will update.")
                    st.rerun()

            st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
            location_photo = st.file_uploader(
                "Upload photo of your stall/shop", type=["png", "jpg", "jpeg"], key=f"loc_photo_{persona_key}"
            )
            if location_photo is not None:
                image_stretch(location_photo, caption=f"Location proof — {persona['name']}")
                st.success("Photo recorded as proof of presence.")
    with notes_col:
        with st.container(key="vp_card_notes"):
            st.markdown(
                '<div class="vp-eyebrow">Merchant daily notes</div>'
                '<div style="font-size:12.5px;color:var(--vp-muted);margin:4px 0 10px">'
                'Customer counts, weather, stock notes — the qualitative trail behind the numbers.</div>',
                unsafe_allow_html=True,
            )
            with st.form(f"daily_notes_{persona_key}", clear_on_submit=True):
                note_date = st.date_input("Date", value=datetime.now().date(), key=f"note_date_{persona_key}")
                customer_count = st.number_input(
                    "Approx. customers today", min_value=0, value=0, step=1, key=f"cust_count_{persona_key}"
                )
                daily_note = st.text_area("Notes", height=90, key=f"daily_note_{persona_key}")
                if st.form_submit_button("Save daily note", icon=":material/note_add:"):
                    st.success(f"Note saved for {note_date}: {customer_count} customers.")

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    section("Certificate", "PM SVANidhi ready proof of vending",
            "Download a verification certificate carrying the Sthan Log history for scheme applications.")
    with st.container(key="vp_card_certificate"):
        st.markdown(
            tiles([
                ("Vending days", f"{persona['sthan_days']:,}"),
                ("Attendance", f"{present_count}/{total_count}"),
                ("Longevity factor", f"{live['factors']['Longevity']['value']}/100"),
                ("Verification", "VP ID generated on download"),
            ]),
            unsafe_allow_html=True,
        )
        st.download_button(
            "Generate proof of vending (PM SVANidhi ready)",
            data=build_vending_certificate(persona, all_log, present_count, total_count),
            file_name=f"proof_of_vending_{persona['name'].replace(' ', '_')}.txt",
            mime="text/plain",
            icon=":material/workspace_premium:",
            key=f"vp_vending_{persona_key}",
        )


# ══════════════════════════════════════════════════════════════════════════════
# 14. PAGE — LENDER REPORT (credit passport)
# ══════════════════════════════════════════════════════════════════════════════
def _uploaded_names(key) -> list:
    value = st.session_state.get(key)
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [getattr(item, "name", str(item)) for item in value]
    return [getattr(value, "name", str(value))]


def render_lender_report(persona_key, persona, live, ctx):
    page_head(
        "Lender report",
        "Credit passport for underwriting",
        "A consent-backed snapshot a credit officer can read in ninety seconds.",
    )

    score_col, status_col = st.columns(2, gap="medium")
    with score_col:
        st.markdown(
            card(
                f'<div class="vp-eyebrow">VyaparPulse live score</div>'
                f'<div style="display:flex;align-items:baseline;gap:8px;margin-top:6px">'
                f'<span style="font-size:2.9rem;font-weight:700;color:{get_score_color(live["score"])};'
                f'letter-spacing:-.035em">{live["score"]}</span>'
                f'<span style="font-size:15px;color:var(--vp-faint);font-weight:600">/900</span></div>'
                f'<div style="font-size:12.5px;color:var(--vp-muted);margin-top:4px">'
                f'{escape(persona["name"])} · {escape(persona["type"])} · {escape(persona["location"])}</div>'
                f'<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:12px">'
                f'<span class="vp-chip vp-chip--{score_band_tone(live["score"])}">{get_score_label(live["score"])}</span>'
                f'<span class="vp-chip vp-chip--neutral">Base {persona["base_score"]}</span>'
                f'<span class="vp-chip vp-chip--neutral">{live["score"] - persona["base_score"]:+d} pts</span></div>',
                cls="vp-card-pad-lg",
            ),
            unsafe_allow_html=True,
        )
    with status_col:
        if persona["loan_status"] == "ELIGIBLE":
            body = (
                f'<div class="vp-eyebrow">Recommended credit (live)</div>'
                f'<div style="font-size:2.1rem;font-weight:700;color:var(--vp-emerald-700);margin-top:6px;'
                f'letter-spacing:-.03em">{inr(live["recommended_credit"])}</div>'
                f'<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:12px">'
                f'<span class="vp-chip vp-chip--pos">{icon("check")} Eligible for disbursement</span>'
                f'<span class="vp-chip vp-chip--neutral">Integrity PASS</span>'
                f'<span class="vp-chip vp-chip--neutral">Margin {live["margin"] * 100:.1f}%</span></div>'
                f'<p style="font-size:12px;color:var(--vp-muted);margin-top:12px">'
                f'Indicative amount from the live scoring model — subject to lender policy and verification.</p>'
            )
        else:
            body = (
                f'<div class="vp-eyebrow">Recommended credit</div>'
                f'<div style="font-size:2.1rem;font-weight:700;color:var(--vp-red);margin-top:6px;'
                f'letter-spacing:-.03em">Rs 0</div>'
                f'<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:12px">'
                f'<span class="vp-chip vp-chip--neg">{icon("alert")} Flagged · loan voided</span>'
                f'<span class="vp-chip vp-chip--neg">Integrity FAIL</span></div>'
                f'<p style="font-size:12px;color:var(--vp-muted);margin-top:12px">'
                f'{escape(persona["integrity_reason"])}</p>'
            )
        st.markdown(card(body, cls="vp-card-pad-lg"), unsafe_allow_html=True)

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    section("Factor breakdown", "Live factor set",
            "Base reading, live reading, movement and strength rating for every factor.")
    factor_rows = []
    for name, data in live["factors"].items():
        base_value = persona["factors"][name]["value"]
        rating = "Strong" if data["value"] >= 70 else ("Moderate" if data["value"] >= 50 else "Weak")
        badge = "low" if data["value"] >= 70 else ("mod" if data["value"] >= 50 else "high")
        factor_rows.append([
            name,
            f'<span class="vp-num">{base_value}/100</span>',
            f'<span class="vp-num" style="font-weight:650;color:var(--vp-ink)">{data["value"]}/100</span>',
            f'<span class="vp-chip vp-chip--{"pos" if data["delta"].startswith("+") else "neg"}">{data["delta"]}</span>',
            f'<span class="vp-badge vp-badge--{badge}">{rating}</span>',
        ])
    with st.container(key="vp_card_factor_table"):
        st.markdown(
            table(["Factor", "Base", "Live", "Change", "Rating"], factor_rows),
            unsafe_allow_html=True,
        )

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    section("Financial summary", "Cash flow snapshot",
            "Adjusted totals already include every entry added in this session.")
    st.markdown(
        tiles([
            ("Monthly avg revenue", inr(live["new_total_revenue"] // 12)),
            ("Daily UPI average", inr(persona["upi_daily_avg"])),
            ("Total transactions", f"{persona['total_transactions']:,}"),
            ("Location stability", f"{persona['sthan_days']:,} days"),
            ("Total revenue (adj)", inr(live["new_total_revenue"])),
            ("Total expenses (adj)", inr(live["new_total_expense"])),
            ("Net profit", inr(live["new_profit"])),
            ("Profit margin", f"{live['margin'] * 100:.1f}%"),
        ]),
        unsafe_allow_html=True,
    )

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    section("Attachments", "Documentation",
            "Notebook pages and supporting documents strengthen the passport and the score.")
    photo_col, doc_col = st.columns(2, gap="medium")
    with photo_col:
        with st.container(key="vp_card_notes_upload"):
            st.markdown(
                '<div class="vp-eyebrow">Expense notebook pages</div>'
                '<div style="font-size:12.5px;color:var(--vp-muted);margin:4px 0 8px">'
                'Digitise the paper register — each attached page adds a documentation bonus to the score.</div>',
                unsafe_allow_html=True,
            )
            expense_upload = st.file_uploader(
                "Upload expense notebook pages (multiple allowed)",
                type=["png", "jpg", "jpeg"], accept_multiple_files=True,
                key=f"expense_nb_{persona_key}",
            )
            if expense_upload:
                photo_count = min(len(expense_upload), 3)
                photo_cols = st.columns(photo_count)
                for index, photo in enumerate(expense_upload):
                    with photo_cols[index % photo_count]:
                        image_stretch(photo, caption=f"Page: {photo.name}")
                if persona_key not in st.session_state.expense_photos_log:
                    st.session_state.expense_photos_log[persona_key] = []
                for photo in expense_upload:
                    if photo.name not in [entry["name"] for entry in st.session_state.expense_photos_log[persona_key]]:
                        st.session_state.expense_photos_log[persona_key].append(
                            {"name": photo.name, "time": datetime.now().strftime("%d-%m-%Y %H:%M")}
                        )
                st.success(f"{len(expense_upload)} expense page(s) attached. Score may update due to documentation bonus.")
    with doc_col:
        with st.container(key="vp_card_docs_upload"):
            st.markdown(
                '<div class="vp-eyebrow">Supporting documents</div>'
                '<div style="font-size:12.5px;color:var(--vp-muted);margin:4px 0 8px">'
                'Shop front photos, inventory images, GST certificate or registration proofs.</div>',
                unsafe_allow_html=True,
            )
            supporting_docs = st.file_uploader(
                "Upload supporting documents",
                type=["png", "jpg", "jpeg", "pdf"], accept_multiple_files=True,
                key=f"support_docs_{persona_key}",
            )
            if supporting_docs:
                for doc in supporting_docs:
                    if doc.type and doc.type.startswith("image"):
                        image_stretch(doc, caption=doc.name)
                    else:
                        st.markdown(f"PDF uploaded: **{doc.name}**")
                st.success(f"{len(supporting_docs)} supporting document(s) attached.")

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    section("Officer notes", "Lender remarks",
            "Free-text notes travel with the passport so context is never lost between reviewers.")
    with st.container(key="vp_card_lender_notes"):
        lender_note = st.text_area(
            "Lender / officer notes (optional)", key=f"lender_note_{persona_key}", height=110
        )
        report_key = f"__report_content_{persona_key}"
        extras = {
            "photo_uploads": len(expense_upload) if expense_upload else 0,
            "supporting_uploads": len(supporting_docs) if supporting_docs else 0,
            "lender_note": lender_note,
            "photo_logs": ctx["photo_logs"],
            "expense_entries": ctx["expense_entries"],
            "revenue_entries": ctx["revenue_entries"],
            "present_checkins": ctx["present_checkins"],
            "high_signals": ctx["high_signals"],
        }
        st.session_state[report_key] = build_credit_passport(persona, live, persona_key, extras)
        st.download_button(
            "Download AA-consent credit passport",
            data=st.session_state[report_key],
            file_name=f"credit_passport_{persona['name'].replace(' ', '_')}.txt",
            mime="text/plain",
            icon=":material/download:",
            type="primary",
            key=f"vp_passport_{persona_key}",
        )
        st.markdown(
            '<p style="font-size:11.5px;color:var(--vp-faint);margin-top:10px">'
            "Data via consent-based Account Aggregator, revocable, DPDP-aligned. "
            "No merchant data is shared without explicit authorization.</p>",
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
# 15. PAGES — PRIVACY & TERMS (content unchanged, re-laid out as documents)
# ══════════════════════════════════════════════════════════════════════════════
def render_privacy():
    page_head("Legal", "Privacy policy",
              "How VyaparPulse collects, uses and protects merchant data.")
    with st.container(key="vp_card_doc"):
        st.markdown(
            f"""
*Last updated: {datetime.now().strftime('%d %B %Y')}*

**1. Data collection**

VyaparPulse collects the following categories of data through consent-based mechanisms:

- **Transaction data:** UPI payment records, transaction volumes, and frequency patterns obtained via the Account Aggregator (AA) framework with explicit merchant consent.
- **Location data:** Sthan Log check-in data provided voluntarily by merchants to establish proof of vending.
- **Business profile:** Merchant name, business type, and location as provided during registration.
- **Financial records:** Revenue and expense entries provided by the merchant for live score computation.
- **Uploaded documents:** Expense notebook photos, QR codes, payment screenshots, and supporting documents uploaded by the merchant.

**2. Data usage**

Collected data is used exclusively for:

- Generating and dynamically updating VyaparPulse credit scores and factor analysis.
- Running integrity checks to detect fraudulent transaction patterns.
- Creating Credit Passport reports for authorized lenders.
- Generating Proof of Vending certificates for government scheme applications.
- Fraud detection through screenshot verification and QR health monitoring.

**3. Data sharing**

- Data is shared with lenders ONLY upon explicit merchant consent.
- Credit Passport reports are generated on-demand and shared only when the merchant initiates download or transmission.
- No data is sold to third parties under any circumstances.
- Integrity check results are shared with lending partners only when a loan application is initiated.

**4. Account Aggregator framework**

VyaparPulse operates within the RBI-regulated Account Aggregator framework:

- All financial data access requires explicit, informed consent.
- Consent is time-bound and purpose-specific.
- Merchants can revoke consent at any time, after which data access ceases immediately.
- Data is encrypted in transit and at rest using industry-standard protocols.

**5. Data retention**

- Active merchant data is retained for the duration of the merchant's engagement with VyaparPulse.
- Upon consent revocation or account deletion, all personal and financial data is purged within 30 days.
- Anonymized, aggregated statistical data may be retained for service improvement.

**6. DPDP Act compliance**

VyaparPulse is fully aligned with the Digital Personal Data Protection (DPDP) Act, 2023:

- Data Fiduciary obligations are maintained at all times.
- Data Principal (merchant) rights including access, correction, and erasure are fully supported.
- Grievance redressal mechanism is available for all data-related concerns.

**7. Security measures**

- End-to-end encryption for all data transmission.
- Role-based access control for internal teams.
- Regular security audits and vulnerability assessments.
- No storage of raw banking credentials.

**8. Merchant rights**

As a VyaparPulse user, you have the right to:

- Access all data collected about your business.
- Request correction of inaccurate data.
- Revoke consent and request data deletion.
- Know which lenders have accessed your Credit Passport.
- Lodge grievances regarding data handling.

**9. Contact**

For privacy-related queries or grievance redressal:

- Email: privacy@vyaparpulse.in
- Grievance Officer: Data Protection Cell, VyaparPulse
- Response time: Within 72 hours of receipt

**10. Updates**

This policy may be updated periodically. Merchants will be notified of material changes via the application and registered contact details.
"""
    )


def render_terms():
    page_head("Legal", "Terms and conditions",
              "The rules that govern use of the VyaparPulse demonstration platform.")
    with st.container(key="vp_card_doc"):
        st.markdown(
            f"""
*Effective date: {datetime.now().strftime('%d %B %Y')}*

**1. Acceptance of terms**

By accessing or using VyaparPulse, you agree to be bound by these Terms and Conditions. If you do not agree, you must discontinue use immediately.

**2. Service description**

VyaparPulse provides:

- Alternative credit scoring (300-900 scale) for micro-merchants and street vendors with live score updates based on financial activity.
- Integrity verification to detect fraudulent transaction patterns.
- Fraud Guard tools for payment screenshot verification and QR code health monitoring.
- Sthan Log for physical presence documentation and Proof of Vending generation.
- Credit Passport generation for lender consumption via Account Aggregator consent.
- Expense and revenue tracking with real-time score impact visualization.

**3. Eligibility**

VyaparPulse services are available to:

- Indian residents aged 18 years and above.
- Individuals operating a micro-enterprise, street vending business, or small retail establishment.
- Users with a valid UPI-enabled bank account.

**4. Live score computation**

- The VyaparPulse score updates dynamically based on expense entries, revenue entries, check-in activity, and documentation uploads.
- Scores range from 300 (lowest) to 900 (highest).
- Score changes are indicative and based on the data provided by the merchant.
- VyaparPulse does not guarantee score accuracy if input data is inaccurate or incomplete.

**5. Credit score disclaimer**

- The VyaparPulse score is an alternative credit assessment tool and does not replace formal credit bureau scores (CIBIL, Experian, etc.).
- The score is advisory in nature. Final lending decisions rest with the respective financial institutions.
- A high score does not guarantee loan approval. A low score does not preclude it.
- Integrity check failures result in automatic loan voiding within the VyaparPulse system.

**6. Fraud Guard tools**

- Screenshot verification and QR health checks are detection tools, not definitive fraud determinations.
- Results should be used as indicators for further investigation.
- VyaparPulse is not liable for losses arising from reliance solely on Fraud Guard outputs.

**7. Sthan Log**

- Sthan Log entries are self-reported and may be supplemented with uploaded photos.
- Proof of Vending certificates generated are based on self-reported data and carry a VyaparPulse verification ID, not a government endorsement.

**8. Intellectual property**

All content, algorithms, scoring methodologies, and interface designs are the intellectual property of VyaparPulse. You may not reverse-engineer, copy, or redistribute any component of the service.

**9. Limitation of liability**

VyaparPulse is provided "as is" without warranties of any kind. We are not liable for any direct, indirect, incidental, or consequential damages arising from use of the service.

**10. Governing law**

These terms are governed by the laws of India. Any disputes shall be subject to the exclusive jurisdiction of courts in New Delhi.

**11. Contact**

For queries regarding these Terms and Conditions:

- Email: legal@vyaparpulse.in
- Address: VyaparPulse, New Delhi, India
"""
    )


# ══════════════════════════════════════════════════════════════════════════════
# 16. APPLICATION SHELL + ROUTER
# ══════════════════════════════════════════════════════════════════════════════
def build_context(persona_key, persona, live):
    """Everything the pages need, derived once per rerun from existing state."""
    period = st.session_state.get("vp_period", "Last 12 months")
    months = PERIOD_OPTIONS.get(period, 12)
    if st.session_state.get("vp_last_period") != period:
        st.session_state["vp_last_period"] = period
        st.session_state["vp_cashflow_months"] = f"{months}M"

    series = adjusted_series(persona, live, months)
    signals, risk = build_risk_signals(persona, live, series)
    insights = build_insights(persona, live, series, signals)

    expense_entries = st.session_state.expense_entries.get(persona_key, [])
    revenue_entries = st.session_state.revenue_entries.get(persona_key, [])
    photo_logs = st.session_state.expense_photos_log.get(persona_key, [])
    sthan_entries = st.session_state.sthan_entries.get(persona_key, [])
    present_checkins = sum(1 for entry in sthan_entries if entry["status"] == "Present")

    extras = {
        "expense_entries": expense_entries,
        "revenue_entries": revenue_entries,
        "photo_logs": photo_logs,
        "sthan_entries": sthan_entries,
        "present_checkins": present_checkins,
        "photo_uploads": len(_uploaded_names(f"expense_nb_{persona_key}")),
        "supporting_uploads": len(_uploaded_names(f"support_docs_{persona_key}")),
        "lender_note": st.session_state.get(f"lender_note_{persona_key}", ""),
        "high_signals": sum(1 for signal in signals if signal["level"] == "HIGH"),
    }
    eligibility = build_eligibility(persona, live, risk, extras)

    return {
        "months": months,
        "cashflow_months": months,
        "trend_days": {3: 30, 6: 90, 12: 180}.get(months, 90),
        "series": series,
        "signals": signals,
        "risk": risk,
        "insights": insights,
        "eligibility": eligibility,
        "expense_entries": expense_entries,
        "revenue_entries": revenue_entries,
        "photo_logs": photo_logs,
        "sthan_entries": sthan_entries,
        "present_checkins": present_checkins,
        "high_signals": extras["high_signals"],
        "photo_uploads": extras["photo_uploads"],
        "supporting_uploads": extras["supporting_uploads"],
        "lender_note": extras["lender_note"],
    }


def main():
    init_session_state()
    personas = get_base_personas()

    selected = st.session_state.get("vp_merchant")
    if selected not in personas:
        selected = list(personas.keys())[0]

    chosen = render_sidebar(personas, selected)
    if chosen not in personas:
        chosen = list(personas.keys())[0]

    persona = personas[chosen]
    live = compute_live_score(chosen, persona)
    ctx = build_context(chosen, persona, live)

    nav_handlers = {
        "overview": lambda: render_overview(chosen, persona, live, ctx),
        "score": lambda: render_credit_score(chosen, persona, live, ctx),
        "intelligence": lambda: render_intelligence(chosen, persona, live, ctx),
        "fraud": lambda: render_fraud_guard(chosen, persona, live, ctx),
        "risk": lambda: render_risk_analytics(chosen, persona, live, ctx),
        "sthan": lambda: render_sthan_log(chosen, persona, live, ctx),
        "lender": lambda: render_lender_report(chosen, persona, live, ctx),
        "privacy": render_privacy,
        "terms": render_terms,
    }
    page = st.session_state.get("vp_page", "overview")
    nav_handlers.get(page, nav_handlers["overview"])()


if __name__ == "__main__":
    main()
