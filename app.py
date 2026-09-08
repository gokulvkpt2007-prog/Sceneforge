import streamlit as st
from google import genai
from supabase import create_client, Client
import json
import time
from datetime import datetime
import pytz
from fpdf import FPDF
import re

# -------------------------------------------------------------
# PAGE CONFIGURATION (LIGHTNING FAVICON LOCKED)
# -------------------------------------------------------------
st.set_page_config(
    page_title="CINEMATEX // NEURAL CINEMA DECK",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------------------
# CYBERPUNK HUD & ADVANCED TERMINAL STYLING
# -------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bungee&family=Orbitron:wght@600;900&family=Rajdhani:wght@600;700&family=JetBrains+Mono:wght@500;700&family=Courier+Prime:ital,wght@0,400;0,700;1,400&display=swap');

    .stApp {
        background: radial-gradient(circle at 10% 10%, #130722 0%, #040308 100%) !important;
        color: #f1f5f9;
        font-family: 'Rajdhani', sans-serif;
    }

    .funky-title {
        font-family: 'Bungee', cursive;
        font-size: 2.4rem;
        background: linear-gradient(90deg, #ff007f 0%, #00f0ff 50%, #ffe600 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 0px 25px rgba(255, 0, 127, 0.4);
        letter-spacing: 2px;
    }

    .hero-learn-card {
        background: linear-gradient(135deg, rgba(32, 14, 66, 0.9) 0%, rgba(13, 8, 28, 0.95) 100%);
        border: 2px solid #a855f7;
        box-shadow: 0 0 25px rgba(168, 85, 247, 0.4);
        border-radius: 14px;
        padding: 22px 28px;
        margin-bottom: 20px;
    }

    .mini-card {
        background: rgba(18, 12, 34, 0.85);
        border: 1.5px solid #2e1d50;
        border-radius: 10px;
        padding: 18px 14px;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .mini-card:hover {
        transform: translateY(-4px);
        border-color: #00f0ff;
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.3);
    }

    .manual-screen-dark {
        background-color: #020204;
        border: 2px solid #1a1a2e;
        border-radius: 8px;
        padding: 20px;
        font-family: 'Courier Prime', Courier, monospace;
        font-size: 0.92rem;
        line-height: 1.7;
        box-shadow: inset 0 0 35px rgba(0,0,0,0.95);
        min-height: 380px;
    }

    .code-line-green {
        color: #00ff66;
        display: block;
        padding: 1px 4px;
    }
    .code-line-red {
        color: #ff3366;
        background: rgba(255, 0, 85, 0.15);
        border-left: 3px solid #ff0055;
        display: block;
        padding: 4px 8px;
        margin: 4px 0;
        border-radius: 4px;
    }

    .scroll-container {
        max-height: 580px;
        overflow-y: auto;
        padding-right: 14px;
        margin-top: 10px;
    }
    .scroll-container::-webkit-scrollbar { width: 7px; }
    .scroll-container::-webkit-scrollbar-track { background: #090613; border-radius: 4px; }
    .scroll-container::-webkit-scrollbar-thumb { background: #00f0ff; border-radius: 4px; box-shadow: 0 0 12px #00f0ff; }

    .cyber-card {
        background: rgba(14, 18, 30, 0.85);
        border: 1px solid rgba(0, 240, 255, 0.25);
        border-left: 5px solid #00f0ff;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 14px;
    }
    .cyber-card-alt { border-left: 5px solid #ff0055; }
    .cyber-card-gold { border-left: 5px solid #ffe600; }
    .cyber-card-purple { border-left: 5px solid #a855f7; }

    .time-badge {
        font-family: 'JetBrains Mono', monospace;
        color: #ffe600;
        background: rgba(255, 230, 0, 0.1);
        border: 1px solid rgba(255, 230, 0, 0.3);
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.8rem;
    }

    .stTextInput input, .stTextArea textarea {
        background-color: #08060f !important;
        color: #00ff66 !important;
        border: 1.5px solid #2d1d4f !important;
        border-radius: 8px !important;
        font-family: 'Courier Prime', monospace !important;
    }

    div.stButton > button {
        background: linear-gradient(135deg, #ff007f 0%, #7928ca 100%) !important;
        color: #ffffff !important;
        font-family: 'Orbitron', monospace !important;
        font-weight: 800 !important;
        border: 1px solid #ff007f !important;
        border-radius: 8px !important;
        padding: 10px 18px !important;
        box-shadow: 0 0 18px rgba(255, 0, 127, 0.4) !important;
    }
    div.stButton > button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 0 28px rgba(0, 240, 255, 0.7) !important;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# SUPABASE CONNECTION CONFIG
# -------------------------------------------------------------
SUPABASE_URL = "https://YOUR_SUPABASE_PROJECT_URL.supabase.co"
SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY"

@st.cache_resource
def get_supabase():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        return None

supabase: Client = get_supabase()

# -------------------------------------------------------------
# PERSISTENT SESSION & STATE RESTORATION ENGINE
# -------------------------------------------------------------
if "user" not in st.session_state:
    st.session_state["user"] = None
if "current_view" not in st.session_state:
    st.session_state["current_view"] = st.query_params.get("view", "HUB")
if "active_project" not in st.session_state:
    st.session_state["active_project"] = {"title": "Untitled Sequence", "script": "", "data": None}
if "manual_script_input" not in st.session_state:
    st.session_state["manual_script_input"] = "INT. HOUSE - NIGHT\n\nRain drums against the window.\n\nGOKUL (30s) checks his watch.\n\nGOKUL\nTeja enga?"
if "learn_step" not in st.session_state:
    st.session_state["learn_step"] = 0
if "mentor_chat" not in st.session_state:
    st.session_state["mentor_chat"] = []

if st.session_state["user"] is None and "token" in st.query_params:
    try:
        res = supabase.auth.get_user(st.query_params["token"])
        if res and res.user:
            st.session_state["user"] = res.user
    except Exception:
        pass

def set_active_view(view_name):
    st.session_state["current_view"] = view_name
    st.query_params["view"] = view_name

def get_current_ist_time():
    tz = pytz.timezone('Asia/Kolkata')
    return datetime.now(tz).strftime("%d %b %Y • %I:%M:%S %p IST")

def load_user_progress(user_id):
    try:
        res = supabase.table("user_learning_progress").select("*").eq("user_id", user_id).execute()
        if res.data and len(res.data) > 0:
            row = res.data[0]
            st.session_state["learn_step"] = row.get("current_step", 0)
            st.session_state["mentor_chat"] = row.get("chat_history", [])
    except Exception:
        pass

def save_user_progress(user_id):
    try:
        supabase.table("user_learning_progress").upsert({
            "user_id": user_id,
            "current_step": st.session_state["learn_step"],
            "chat_history": st.session_state["mentor_chat"],
            "updated_at": "now()"
        }).execute()
    except Exception:
        pass

# Robust Gemini API Engine
def call_cinematex_ai(api_key, prompt, expect_json=True):
    models = ['gemini-3.6-flash', 'gemini-3.7-flash', 'gemini-3.5-flash-lite']
    client = genai.Client(api_key=api_key)
    cfg = {'response_mime_type': 'application/json'} if expect_json else {}
    for m in models:
        try:
            res = client.models.generate_content(
                model=m,
                contents=prompt,
                config=cfg
            )
            if res and res.text:
                return res.text
        except Exception:
            time.sleep(0.5)
            continue
    return None

# PDF Engine
def safe_pdf_text(text):
    if not text:
        return ""
    return str(text).encode('ascii', 'ignore').decode('ascii')

def generate_dossier_pdf(title, raw_text, p_data, timestamp):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    pdf.add_page()
    content_w = pdf.epw

    pdf.set_font("Helvetica", 'B', 18)
    pdf.cell(content_w, 12, safe_pdf_text("CINEMATEX PRODUCTION DOSSIER"), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", 'I', 10)
    pdf.cell(content_w, 8, safe_pdf_text(f"Project: {title} | Forged: {timestamp}"), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(6)
    
    pdf.set_font("Helvetica", 'B', 13)
    pdf.cell(content_w, 10, safe_pdf_text("1. INDUSTRY FORMATTED SCREENPLAY"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Courier", '', 9)
    script_content = p_data.get("formatted_script", "") if isinstance(p_data, dict) else ""
    pdf.multi_cell(content_w, 5, safe_pdf_text(script_content))
    pdf.ln(6)
    return bytes(pdf.output())

# -------------------------------------------------------------
# STRICT HOLLYWOOD/CINEMA SCREENPLAY SYNTAX ANALYZER
# -------------------------------------------------------------
def analyze_screenplay_line(line, prev_line_type="EMPTY"):
    raw = line.strip()
    if not raw:
        return True, "EMPTY", ""

    if re.match(r'^(INT\.|EXT\.|INT\./EXT\.)\s+[A-Z0-9\s\-\.\/\'\"]+', raw):
        return True, "SLUGLINE", "Valid Scene Heading"

    if any(raw.upper().startswith(p) for p in ["INT ", "EXT ", "SCENE ", "OPENING ", "SHOT "]):
        return False, "INVALID_SLUGLINE", "Invalid Slugline! Must strictly start with INT. or EXT. (e.g., INT. HOUSE - NIGHT)"

    if raw.isupper() and len(raw.split()) <= 4 and not any(char in raw for char in [".", ",", ":", ";", "!", "?"]):
        return True, "CHARACTER", "Valid Character Heading"

    if raw.startswith("(") and raw.endswith(")"):
        return True, "PARENTHETICAL", "Valid Actor Cue"

    if '"' in raw or "'" in raw:
        return False, "NOVEL_DIALOGUE", "Novel format detected! Screenplay dialogues cannot be inside quotes within paragraphs. Put Character Name in UPPERCASE above, then Dialogue below."

    if re.search(r'\b(nu solra|nu kekuran|nu kathuran|solran|kekra|solra)\b', raw, re.IGNORECASE):
        return False, "CASUAL_PASSAGE", "Conversational storytelling detected. Format into Character Cue followed by dialogue line."

    if prev_line_type in ["CHARACTER", "PARENTHETICAL"]:
        return True, "DIALOGUE", "Valid Dialogue Line"

    if re.search(r'\b(open agudhu|revel panrom|pakrom|camera angle)\b', raw, re.IGNORECASE):
        return False, "DIRECTOR_COMMENTARY", "Don't write director talk ('revel panrom', 'camera angle'). Write what the camera sees physically."

    unfilmable_words = [r'\bfeels?\b', r'\bthinking\b', r'\bthinks?\b', r'\bremembers?\b', r'\bguilty\b']
    for trig in unfilmable_words:
        if re.search(trig, raw, re.IGNORECASE):
            return False, "UNFILMABLE", "Unfilmable thought detected. Camera cannot film internal mind feelings."

    if len(raw.split()) > 14:
        return False, "RUNON_PARAGRAPH", "Action paragraph too dense. Screenplay action blocks must be short, punchy 1-2 visual lines."

    return True, "ACTION", "Valid Action Line"

# -------------------------------------------------------------
# THE DEFINITIVE SCREENPLAY MASTERCLASS: 8 COMPLETE BOOK CHAPTERS
# -------------------------------------------------------------
LESSONS = [
    {
        "title": "CHAPTER 1: THE CORE PHILOSOPHY — SCREENPLAY VS NOVEL",
        "content": """
### 📖 1.1 What Truly is a Screenplay?
Screenplay nguradhu oru novel kedayadhu, oru sirukadhai kedayadhu, kavithaiyum kedayadhu. Adhu 150-kum periya cinema shooting unit-kku (DOP, Gaffer, Art Director, Sound Designer, Actors, Editor) velai seiya kudukura **Industrial Technical Blueprint**.

Oru writer novel ezhudhum bodhu readers-oda manasula karpanai panna mudiyum:
* Novel Writer: *"Ravi avanoda thalaividhiye nenachu romba kavalaiyoda, pazhaya kaadhalai nenachu vizhundhu vizhundhu azhudhaan."*
* Cinema Screenplay: **Indha maadhiri ezhudhavay koodadhu!**

> **The Sacred Law of Cinema:**
> **"Camera lens enna photograph pannudho, microphone enna record pannudho — adha thavira oru ezhuthu kooda screenplay page-la irukka koodadhu."**

---

### ⚙️ 1.2 The 6 Building Blocks of Every Professional Script
1. **Scene Heading (Slugline):** Camera enga vekanum, shoot timing enna? (`INT.` / `EXT.`)
2. **Action Lines:** 3rd-person present tense-la camera paakura physical actions & foley textures.
3. **Character Cue:** Pesura character name — Full UPPERCASE-la (`VIKRAM`).
4. **Parenthetical:** Actor-kku micro physical direction `(into mirror)`.
5. **Dialogue:** Character vaai thirandhu pesura exact words.
6. **Transitions:** Editor cut cues (`SMASH CUT TO:`, `MATCH CUT TO:`).

---

### 🔬 1.3 Case Study: Novel Thinking vs Camera Writing
* ❌ **Amateur Novel Style:**
  > *"Sanjay feels immense guilt for having betrayed his sister 4 years ago. He is walking on the road full of depression."*
  *(Camera-vaala Sanjay manasula 4 years ago nadandha betrayal-ah paaka mudiyaadhu! Actor epdi '4 years ago guilt'-ah nadika mudiyum?)*

* ✅ **Professional Courier Screenplay Standard:**
  ```text
  EXT. NELSON MANICKAM ROAD - NIGHT
  
  Sodium streetlights reflect off greasy rain puddles.
  
  SANJAY (20s), hollow-eyed, drenches in the downpour. 
  
  He holds a torn passport photograph of his sister. His trembling thumb wipes water droplets from her printed face.
  
  A passing lorry splashes filthy water over his sneakers. He doesn't flinch.
