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
SUPABASE_URL = "https://xiicgxqmmrvvvgdvkbej.supabase.co"
SUPABASE_KEY = "sb_publishable_l3TcwbLc7Dm9X-Ji-7bJdw_M0ey36-8"

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

# Persistent login check via refresh token query parameter
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
# MASTERCLASS LESSONS LIST
# -------------------------------------------------------------
LESSONS = [
    {
        "title": "LESSON 1: SCRIPT WRITING-NA ENNA? (THE BLUEPRINT REVELATION)",
        "content": """
### 🎬 Script Writing-na unmaiyile enna?
Nariya per nenaikiraanga script writing-na oru novel ezhudhuradho, illa dialogues mattum notebook-la type panradho nu. **Adhu thappu!**

Screenplay nguradhu oru building katturadhukku engineer podura **Architectural Blueprint** maadhiri.
Oru padathoda shooting spot-la 150-kum periya crew irupaanga:
* **DOP (Cinematographer):** Endha lens podanum, camera tracking epdi irukanum?
* **Art Director:** Room kulla enna props irukanum?
* **Sound Engineer:** Enna maadhiri foley sound kekkanum?
* **Actors:** Enna express pannanum?

Indha 150 perukkum orey oru guide dhaan unga **Screenplay**.
Oru script-oda fundamental rule: **"Camera paakadha vishayathaiyo, mic kekkadha vishayathaiyo script page-la ezhudha koodadhu."**
        """
    },
    {
        "title": "LESSON 2: SLUGLINE (SCENE HEADING) & CAMERA GEOGRAPHY",
        "content": """
### 📍 Sluglines: Camera Enga, Eppodhu Shoot Pannudhu?
Oru scene start aagumbodhu mela irukura bold capital line dhaan **Slugline**.

#### Slugline-oda 3 Core Parts:
1. **Camera Position:** `INT.` (Interior) / `EXT.` (Exterior) / `INT./EXT.` (Vehicle tracking).
2. **Specific Location:** ❌ *Thappu:* `INT. HOUSE` ➔ ✅ *Sari:* `INT. VIKRAM'S DUSTY STUDY ROOM`.
3. **Lighting Time:** `DAY`, `NIGHT`, `DAWN`, `MAGIC HOUR`, or `CONTINUOUS`.
        """
    },
    {
        "title": "LESSON 3: 'SHOW, DON'T TELL' (VISUAL ACTION vs INTERNAL THOUGHT)",
        "content": """
### 👁️ Camera Enna Paakudho Adha Mattum Ezhudhu!
* ❌ **Novel Style (Unfilmable):** *"Siva feels deep guilt and depression thinking about his dead brother while drinking water."*
* ✅ **Screenplay Standard (Pure Visual Lens):** *"Siva holds a glass of water to his mouth. His hand tremors. Water spills over his knuckles, soaking a faded photograph of two boys on the desk."*
        """
    },
    {
        "title": "LESSON 4: SUBTEXT & DIALOGUE POWER DYNAMICS",
        "content": """
### 🎭 Subtext: Varthaiku Pinnadi Olinjirukura Unmai
Direct-ah solra dialogue boring. True drama hides in what people HIDE.
* ❌ **Flat Dialogue:** *"I know you stole the money from the safe."*
* ✅ **Subtextual Cinema:** *"Pudhu shoes nalla irukku Madhan. Salary potaachu pola?"* *(Madhan pulls his feet back into the shadow).*
        """
    },
    {
        "title": "LESSON 5: THE 3-ACT ENGINE & SCENE MICRO-BEATS",
        "content": """
### ⏱️ Oru Scene epdi build aagi climax aagudhu?
Ovvoru thani scene-ukkum mini 3-Act structure irukkum:
1. **Entry Beat (+ or -):** Initial situation.
2. **Escalation / Complication:** Obstacle arises.
3. **Exit Beat (Opposite polarity):** Scene enter aana status reverse aagi mudiyanum!
        """
    }
]

# =============================================================
# 1. AUTHENTICATION GATEWAY
# =============================================================
if st.session_state["user"] is None:
    st.write("")
    st.markdown('<div class="funky-title" style="text-align:center;">⚡ CINEMATEX </div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center; color:#00f0ff; font-family:Orbitron;">NEURAL PRE-PRODUCTION DECK & SCRIPTWRITING ACADEMY</div>', unsafe_allow_html=True)
    st.write("")

    col_l1, col_center, col_l2 = st.columns([1, 1.4, 1])
    with col_center:
        auth_mode = st.radio("GATEWAY SELECTOR", ["RETURNING DIRECTOR (LOGIN)", "NEW CREATOR (SIGN UP)"], horizontal=True)
        email = st.text_input("GMAIL / EMAIL", placeholder="director@gmail.com")
        password = st.text_input("SECURITY KEY", type="password", placeholder="••••••••")
        
        st.write("")
        if "LOGIN" in auth_mode:
            if st.button("🚀 ENTER THE STUDIO", use_container_width=True):
                if not email or not password:
                    st.error("Please fill credentials!")
                else:
                    try:
                        res = supabase.auth.sign_in_with_password({"email": email.strip(), "password": password})
                        st.session_state["user"] = res.user
                        load_user_progress(res.user.id)
                        st.query_params["token"] = res.session.access_token
                        set_active_view("HUB")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Login failed: {e}")
        else:
            if st.button("✨ FORGE MY CREATOR ACCOUNT", use_container_width=True):
                if not email or not password:
                    st.error("Please enter credentials!")
                else:
                    try:
                        res = supabase.auth.sign_up({"email": email.strip(), "password": password})
                        if res.user:
                            st.session_state["user"] = res.user
                            load_user_progress(res.user.id)
                            if res.session:
                                st.query_params["token"] = res.session.access_token
                            set_active_view("HUB")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Registration error: {e}")
    st.stop()

# =============================================================
# TOP NAVIGATION
# =============================================================
col_nav1, col_nav2, col_nav3 = st.columns([2.5, 2, 1])
with col_nav1:
    st.markdown('<div class="funky-title" style="font-size:1.8rem;">⚡ CINEMATEX</div>', unsafe_allow_html=True)
with col_nav2:
    st.markdown(f"<div style='margin-top:12px; font-size:13px; color:#94a3b8;'>DIRECTOR: <b style='color:#00f0ff;'>{st.session_state['user'].email}</b></div>", unsafe_allow_html=True)
with col_nav3:
    if st.button("🚪 LOGOUT", use_container_width=True):
        save_user_progress(st.session_state["user"].id)
        supabase.auth.sign_out()
        st.session_state["user"] = None
        st.query_params.clear()
        set_active_view("HUB")
        st.rerun()

# =============================================================
# 2. STUDIO COMMAND NEXUS (HUB)
# =============================================================
if st.session_state["current_view"] == "HUB":
    st.write("")
    st.markdown("<h2 style='text-align:center; font-family:Orbitron; color:#ffe600;'>⚡ STUDIO COMMAND NEXUS</h2>", unsafe_allow_html=True)
    st.write("")

    st.markdown("""
    <div class="hero-learn-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <span class="time-badge" style="color:#c084fc; border-color:#c084fc;">CINEMA MASTERCLASS // ZERO TO PRO</span>
                <h2 style="font-family:Orbitron; color:#00f0ff; margin-top:8px; margin-bottom:4px;">🎓 SCRIPTWRITING ACADEMY & AI MENTOR</h2>
                <p style="color:#e2e8f0; font-size:15px; margin:0;">Learn screenplay architecture step-by-step with cloud auto-save, then unlock your private AI Mentor talking bot!</p>
            </div>
            <div style="font-size:3.5rem;">📜</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("ENTER ACADEMY & CHATBOT MENTOR ➔", use_container_width=True):
        set_active_view("LEARN_ACADEMY")
        st.rerun()

    st.write("")
    st.markdown("<h4 style='font-family:Orbitron; color:#94a3b8;'>CINEMA PRODUCTION SUITE // 4 WORKSPACES</h4>", unsafe_allow_html=True)

    col_w1, col_w2, col_w3, col_w4 = st.columns(4, gap="small")
    with col_w1:
        st.markdown("""
        <div class="mini-card">
            <h2 style="margin:0;">✍️</h2>
            <h4 style="color:#00ff66; margin-top:6px;">MANUAL SCRIPT WRITING</h4>
            <p style="color:#94a3b8; font-size:12px;">Live Green/Red syntax checking, exports & AI Auto-Correct.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("LAUNCH MANUAL IDE ➔", key="btn_manual", use_container_width=True):
            set_active_view("MANUAL_IDE")
            st.rerun()

    with col_w2:
        st.markdown("""
        <div class="mini-card">
            <h2 style="margin:0;">⚡</h2>
            <h4 style="color:#00f0ff; margin-top:6px;">QUANTUM FORGE</h4>
            <p style="color:#94a3b8; font-size:12px;">Auto-forge Courier screenplay & AI Storyboard Prompts.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("LAUNCH AUTO-FORGE ➔", key="btn_auto", use_container_width=True):
            st.session_state["active_project"] = {"title": "Untitled Sequence", "script": "", "data": None}
            set_active_view("WORKSPACE")
            st.rerun()

    with col_w3:
        st.markdown("""
        <div class="mini-card">
            <h2 style="margin:0;">📂</h2>
            <h4 style="color:#ffe600; margin-top:6px;">SAVED VAULT</h4>
            <p style="color:#94a3b8; font-size:12px;">Access or delete stored projects with IST timestamps.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("OPEN VAULT ➔", key="btn_vault", use_container_width=True):
            set_active_view("SAVED")
            st.rerun()

    with col_w4:
        st.markdown("""
        <div class="mini-card">
            <h2 style="margin:0;">📦</h2>
            <h4 style="color:#ff007f; margin-top:6px;">PDF EXPORTS</h4>
            <p style="color:#94a3b8; font-size:12px;">Download compiled production kits as official PDF dossiers.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("VIEW PDFS ➔", key="btn_dossier", use_container_width=True):
            set_active_view("EXPORTED")
            st.rerun()

# =============================================================
# 3. MANUAL SCRIPTWRITING WORKSPACE (LIVE SYNTAX & EXPORTS)
# =============================================================
elif st.session_state["current_view"] == "MANUAL_IDE":
    col_mback, col_mhead = st.columns([1, 4])
    with col_mback:
        if st.button("⬅️ COMMAND NEXUS"):
            set_active_view("HUB")
            st.rerun()
    with col_mhead:
        st.markdown("<h2 style='font-family:Orbitron; color:#00ff66; margin:0;'>✍️ MANUAL SCREENPLAY TERMINAL (LIVE SYNTAX DOCTOR)</h2>", unsafe_allow_html=True)
        st.caption("Write manually on pure black canvas. Standard format = Green letters. Format errors / unfilmable thoughts = Red letters.")

    st.write("")

    col_editor, col_preview = st.columns([1.1, 1.3], gap="medium")
    
    with col_editor:
        st.markdown("### ⌨️ WRITER TERMINAL")
        m_title = st.text_input("MANUAL PROJECT TITLE:", value="Neo-Noir Standoff Scene", key="manual_title_input")
        
        typed_script = st.text_area(
            "TYPE YOUR RAW SCRIPT (COURIER FORMAT):",
            value=st.session_state["manual_script_input"],
            height=380,
            key="manual_editor_area"
        )
        st.session_state["manual_script_input"] = typed_script

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            save_manual_btn = st.button("💾 SAVE TO VAULT", use_container_width=True)
        with col_b2:
            fix_btn = st.button("💡 FIX ERROR & AUTO-CORRECT", use_container_width=True)

        col_exp1, col_exp2 = st.columns(2)
        ts_now = get_current_ist_time()
        
        with col_exp1:
            manual_pdf_bytes = generate_dossier_pdf(
                m_title, 
                typed_script, 
                {"formatted_script": typed_script}, 
                ts_now
            )
            st.download_button(
                label="📄 EXPORT PDF SCRIPT",
                data=manual_pdf_bytes,
                file_name=f"{m_title.replace(' ', '_')}_Script.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        with col_exp2:
            st.download_button(
                label="📥 EXPORT TEXT (.TXT)",
                data=typed_script,
                file_name=f"{m_title.replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )

        if save_manual_btn:
            ts = get_current_ist_time()
            try:
                supabase.table("saved_scripts").insert({
                    "user_id": st.session_state["user"].id,
                    "title": m_title,
                    "script_content": typed_script,
                    "parsed_data": {"formatted_script": typed_script},
                    "saved_at_formatted": ts,
                    "is_exported": True,
                    "is_manual": True
                }).execute()
                st.success(f"Manual screenplay archived and synced to Exported Dossiers at {ts}")
            except Exception as e:
                st.error(f"Error saving: {e}")

        api_key = st.secrets.get("GEMINI_API_KEY", "")
        if fix_btn:
            if not api_key:
                st.warning("Gemini API Key required for Auto-Correct!")
            else:
                with st.spinner("Cinema Doctor converting red error lines into Hollywood standard..."):
                    fix_prompt = f"""
                    You are an expert Hollywood and Tamil Cinema Screenplay Doctor.
                    The user wrote a raw conversational/novel passage with red syntax errors:
                    ---
                    {typed_script}
                    ---
                    TASK:
                    Convert this entire passage into a pure, industry-standard Courier screenplay.
                    Rules:
                    1. Use standard sluglines like INT. HOUSE - NIGHT.
                    2. Convert inline quotes into centered UPPERCASE Character cues followed by dialogue.
                    3. Convert casual conversational narration ('nu solra', 'revel panrom', 'camera angle') into strict 3rd-person visual action blocks.
                    4. Retain all Tamil/Tanglish linguistic emotion accurately.
                    Return ONLY the repaired Courier screenplay text with no markdown backticks and no conversational commentary.
                    """
                    repaired = call_cinematex_ai(api_key, fix_prompt, expect_json=False)
                    if repaired:
                        clean_repaired = repaired.strip().replace("```", "")
                        st.session_state["manual_script_input"] = clean_repaired
                        st.success("🎯 ALL RED ERRORS REPAIRED TO PERFECT COURIER STANDARD!")
                        st.rerun()

    with col_preview:
        st.markdown("### 🖥️ LIVE SYNTAX CHECKER HUD")
        
        lines = typed_script.split("\n")
        rendered_html = ['<div class="manual-screen-dark scroll-container">']
        error_count = 0
        error_details = []
        last_type = "EMPTY"

        for idx, line in enumerate(lines, 1):
            is_valid, tag, msg = analyze_screenplay_line(line, last_type)
            if line.strip():
                last_type = tag
            else:
                last_type = "EMPTY"

            escaped_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            
            if not line.strip():
                rendered_html.append("<br>")
            elif is_valid:
                rendered_html.append(f'<span class="code-line-green">{escaped_line}</span>')
            else:
                error_count += 1
                error_details.append((idx, line, msg))
                rendered_html.append(f'<span class="code-line-red"><b>[L{idx}]</b> {escaped_line}<br><span style="font-size:11px; color:#ffb3c6; font-family:sans-serif;">⚠️ {msg}</span></span>')

        rendered_html.append('</div>')
        st.markdown("".join(rendered_html), unsafe_allow_html=True)

        if error_count == 0:
            st.markdown("<span class='time-badge' style='color:#00ff66; border-color:#00ff66;'>✅ SCRIPT HEALTH: 100% CLEAN // ALL COURIER PROTOCOLS MET</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span class='time-badge' style='color:#ff0055; border-color:#ff0055;'>⚠️ SCRIPT WARNING: {error_count} RED SYNTAX ERRORS DETECTED</span>", unsafe_allow_html=True)
            for l_num, l_txt, reason in error_details[:3]:
                st.caption(f"Line {l_num}: {reason}")
            st.info("Click '💡 FIX ERROR & AUTO-CORRECT' to have AI automatically repair all red errors!")

# =============================================================
# 4. AUTOMATED WORKSPACE (QUANTUM FORGE & STORYBOARDS)
# =============================================================
elif st.session_state["current_view"] == "WORKSPACE":
    if st.button("⬅️ BACK TO COMMAND NEXUS"):
        set_active_view("HUB")
        st.rerun()

    col_side, col_main = st.columns([1, 2.5], gap="medium")
    api_key = st.secrets.get("GEMINI_API_KEY", "")

    with col_side:
        st.markdown("### 🕹️ QUANTUM FORGE")
        if api_key:
            st.markdown("<span class='time-badge' style='color:#00f0ff; border-color:#00f0ff;'>⚡ NEURAL ENGINE: LINKED & ACTIVE</span>", unsafe_allow_html=True)
        else:
            api_key = st.text_input("GEMINI API KEY (Override)", type="password")

        project_title = st.text_input("PROJECT TITLE", value=st.session_state["active_project"]["title"])
        script_input = st.text_area(
            "RAW STORY PASSAGE / CONVERSATIONAL OUTLINE:",
            value=st.session_state["active_project"]["script"],
            height=320,
            placeholder="Kadhai summary / rough passage inga paste pannunga. Engine adha Courier standard screenplay-va maathum, koodave Storyboard Prompts generate pannum..."
        )
        
        forge_btn = st.button("⚡ EXECUTE CINEMATEX FORGE", use_container_width=True)
        save_db_btn = st.button("💾 SAVE WITH TIMESTAMP", use_container_width=True)

        if save_db_btn:
            if not script_input.strip():
                st.warning("Buffer empty! Cannot save.")
            else:
                ts = get_current_ist_time()
                try:
                    supabase.table("saved_scripts").insert({
                        "user_id": st.session_state["user"].id,
                        "title": project_title,
                        "script_content": script_input,
                        "parsed_data": st.session_state["active_project"].get("data", {}),
                        "saved_at_formatted": ts,
                        "is_exported": False,
                        "is_manual": False
                    }).execute()
                    st.success(f"Project safely preserved at {ts}")
                except Exception as err:
                    st.error(f"Database error: {err}")

    with col_main:
        st.markdown("### 📊 PRODUCTION MATRIX")
        tab_script, tab_sb, tab1, tab2, tab3, tab5 = st.tabs([
            "📜 INDUSTRY SCREENPLAY",
            "🎨 STORYBOARD PROMPTS",
            "⚡ SCENE BEATS",
            "👤 CHARACTER BIBLE",
            "🎥 SHOT LIST",
            "📄 EXPORT PDF DOSSIER"
        ])

        if forge_btn:
            if not api_key:
                st.error("Gemini API Key missing! Check Secrets.")
            elif not script_input.strip():
                st.warning("Provide story passage to forge!")
            else:
                with st.spinner("Cinematex Neural Engine generating screenplay, breakdowns, and Storyboard prompts..."):
                    prompt = f"""
                    You are an elite cinema director, script doctor, and cinematographer.
                    Input text:
                    ---
                    {script_input}
                    ---
                    REQUIREMENTS:
                    1. "formatted_script": Flawless industry screenplay (SLUGLINES, visual action lines, centered character names, parentheticals, sharp dialogue).
                    2. "storyboard_prompts": ULTRA-DETAILED visual prompts ready for Midjourney v6 and Flux (camera lens, depth of field, framing, lighting setup, atmosphere, cinematic color grade, photorealistic movie still, --ar 16:9).
                    3. "scene_beats": "scene_title", "emotional_tone", "tension_rating", "micro_beats", "director_vision".
                    4. "characters": "name", "role", "appearance", "quirks", "core_conflict".
                    5. "shot_list": "scene_no", "shot_type", "camera_angle", "lighting_setup", "sound_cue".

                    Return STRICT JSON:
                    {{
                        "formatted_script": "string",
                        "storyboard_prompts": [ "string" ],
                        "scene_beats": [ {{"scene_title": "", "emotional_tone": "", "tension_rating": "", "micro_beats": "", "director_vision": ""}} ],
                        "characters": [ {{"name": "", "role": "", "appearance": "", "quirks": "", "core_conflict": ""}} ],
                        "shot_list": [ {{"scene_no": "", "shot_type": "", "camera_angle": "", "lighting_setup": "", "sound_cue": ""}} ]
                    }}
                    """
                    raw_res = call_cinematex_ai(api_key, prompt, expect_json=True)
                    if raw_res:
                        try:
                            clean_json = raw_res.strip().replace("```json", "").replace("```", "")
                            parsed = json.loads(clean_json)
                            st.session_state["active_project"]["data"] = parsed
                            st.session_state["active_project"]["script"] = script_input
                            st.session_state["active_project"]["title"] = project_title
                            st.success("CINEMATEX FORGE SUCCESSFUL // ALL MATRICES SYNCHRONIZED")
                        except Exception as e:
                            st.error(f"JSON parsing error: {e}")

        p_data = st.session_state["active_project"].get("data")
        if p_data:
            with tab_script:
                script_formatted = p_data.get("formatted_script", "Script not ready.")
                st.markdown(f'<div class="scroll-container"><div class="manual-screen-dark" style="color:#f8fafc;">{script_formatted}</div></div>', unsafe_allow_html=True)

            with tab_sb:
                st.markdown("### 🎨 CINEMATIC STORYBOARD PROMPTS")
                st.caption("Detailed Midjourney v6 / Flux prompts. Click the copy icon on the right to copy directly:")
                sb_prompts = p_data.get("storyboard_prompts", [])
                if not sb_prompts:
                    st.info("No storyboard prompts generated. Re-execute Forge.")
                else:
                    st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
                    for i, p in enumerate(sb_prompts, 1):
                        st.markdown(f"**🎬 Frame {i} Production Prompt:**")
                        st.code(p, language="text")
                    st.markdown('</div>', unsafe_allow_html=True)

            with tab1:
                st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
                for b in p_data.get("scene_beats", []):
                    st.markdown(f"""
                    <div class="cyber-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h4 style="color:#00f0ff; margin:0;">⚡ {b.get('scene_title', 'SCENE')}</h4>
                            <span class="time-badge">{b.get('emotional_tone')} • TENSION: {b.get('tension_rating')}</span>
                        </div>
                        <p style="margin-top:10px; color:#e2e8f0; font-size:15px;"><b>Micro-Beats:</b><br>{b.get('micro_beats', '')}</p>
                        <p style="color:#94a3b8; font-size:14px; margin:0;"><b>Director Subtext:</b> {b.get('director_vision', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with tab2:
                st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
                for c in p_data.get("characters", []):
                    st.markdown(f"""
                    <div class="cyber-card cyber-card-alt">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h3 style="color:#ff0055; margin:0;">👤 {c.get('name', 'UNKNOWN')}</h3>
                            <span class="time-badge" style="color:#ff0055; border-color:#ff0055;">{c.get('role', '')}</span>
                        </div>
                        <div style="margin-top:8px; font-size:14px;"><b style="color:#00f0ff;">Visual Textures:</b> {c.get('appearance', '')}</div>
                        <div style="margin-top:5px; font-size:14px;"><b style="color:#ffe600;">Mannerisms:</b> {c.get('quirks', '')}</div>
                        <div style="margin-top:5px; font-size:14px;"><b style="color:#ff0055;">Internal Conflict:</b> {c.get('core_conflict', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with tab3:
                st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
                st.dataframe(p_data.get("shot_list", []), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with tab5:
                ts_now = get_current_ist_time()
                pdf_bytes = generate_dossier_pdf(project_title, script_input, p_data, ts_now)
                if st.download_button(
                    label="⬇️ DOWNLOAD OFFICIAL CINEMATEX DOSSIER (.PDF)",
                    data=pdf_bytes,
                    file_name=f"{project_title.replace(' ', '_')}_Cinematex_Dossier.pdf",
                    mime="application/pdf",
                    use_container_width=True
                ):
                    supabase.table("saved_scripts").insert({
                        "user_id": st.session_state["user"].id,
                        "title": project_title,
                        "script_content": script_input,
                        "parsed_data": p_data,
                        "saved_at_formatted": ts_now,
                        "is_exported": True,
                        "is_manual": False
                    }).execute()
                    st.success("PDF exported and recorded!")

# =============================================================
# 5. STEP-BY-STEP ACADEMY & PERSISTENT CHATBOT MENTOR
# =============================================================
elif st.session_state["current_view"] == "LEARN_ACADEMY":
    col_aback, col_ahead = st.columns([1, 4])
    with col_aback:
        if st.button("⬅️ COMMAND NEXUS"):
            save_user_progress(st.session_state["user"].id)
            set_active_view("HUB")
            st.rerun()
    with col_ahead:
        st.markdown("<h2 style='font-family:Orbitron; color:#c084fc; margin:0;'>🎓 SCRIPTWRITING MASTERCLASS</h2>", unsafe_allow_html=True)
        st.caption("Deep Conceptual Breakdown // Persistent Cloud Auto-Save Engine")

    st.write("")
    step = st.session_state["learn_step"]
    total_lessons = len(LESSONS)

    if step < total_lessons:
        cur = LESSONS[step]
        st.markdown(f"""
        <div class="cyber-card cyber-card-purple">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span class="time-badge">MODULE {step + 1} OF {total_lessons}</span>
                <span style="color:#00f0ff; font-family:Orbitron; font-size:13px;">SAVED TO CLOUD VAULT ✅</span>
            </div>
            <h3 style="color:#ffe600; margin-top:10px;">{cur['title']}</h3>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
        st.markdown(cur["content"])
        st.markdown('</div>', unsafe_allow_html=True)
        st.write("")

        col_prev, col_spacer, col_nxt = st.columns([1, 2, 1.5])
        with col_prev:
            if step > 0:
                if st.button("⬅️ PREVIOUS LESSON", use_container_width=True):
                    st.session_state["learn_step"] -= 1
                    save_user_progress(st.session_state["user"].id)
                    st.rerun()

        with col_nxt:
            is_last = (step == total_lessons - 1)
            btn_label = "🔥 UNLOCK NEXT LEVEL (AI MENTOR) ➔" if is_last else "NEXT EXPLANATION ➔"
            if st.button(btn_label, use_container_width=True):
                st.session_state["learn_step"] += 1
                save_user_progress(st.session_state["user"].id)
                st.rerun()

    else:
        st.markdown("""
        <div class="cyber-card cyber-card-gold">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span class="time-badge" style="color:#ffe600; border-color:#ffe600;">FINAL LEVEL: MASTER MENTORSHIP</span>
                <span style="color:#00f0ff; font-family:Orbitron; font-size:13px;">SESSION ACTIVE • AUTO-SAVED ✅</span>
            </div>
            <h3 style="color:#00f0ff; margin-top:10px;">🎬 LIVE TALKING CHATBOT: YOUR PRIVATE SCREENPLAY MENTOR</h3>
            <p style="color:#f8fafc; font-size:14px; margin:0;">
            Neenga kathukitta ella concepts-ayum vechu mentor kooda live-a pesalam. Doubts kelunga, scene lines submit pannunga!
            </p>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state["mentor_chat"]:
            st.session_state["mentor_chat"].append({
                "role": "mentor",
                "text": "Vanakkam Director! Neenga 5 core modules-ayum mudichiteenga. Ippo ungalukku screenplay architecture clear. Enkitta unga scene pitch pannunga illana doubts kelunga, direct-a solve pannuvom!"
            })
            save_user_progress(st.session_state["user"].id)

        st.markdown('<div class="scroll-container" style="max-height: 380px;">', unsafe_allow_html=True)
        for m in st.session_state["mentor_chat"]:
            if m["role"] == "mentor":
                st.markdown(f"""
                <div class="cyber-card" style="border-left: 5px solid #a855f7; margin-bottom:8px;">
                    <b style="color:#c084fc;">🎬 DIRECTOR MENTOR:</b><br>
                    <span style="color:#f8fafc; font-size:15px;">{m['text']}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="cyber-card cyber-card-gold" style="text-align:right; margin-bottom:8px;">
                    <b style="color:#ffe600;">YOU (SCREENWRITER):</b><br>
                    <span style="color:#f8fafc; font-size:15px;">{m['text']}</span>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        api_key = st.secrets.get("GEMINI_API_KEY", "")
        col_ci, col_cb = st.columns([4, 1])
        with col_ci:
            u_text = st.text_input("Ask doubts or submit scene lines:", placeholder="E.g. Mentor, oru interval block-ku subtext dialogue epdi ezhudhuradhu?", label_visibility="collapsed")
        with col_cb:
            send_btn = st.button("SEND TO MENTOR ➔", use_container_width=True)

        if send_btn and u_text.strip():
            if not api_key:
                st.warning("Gemini API Key missing! Check Secrets.")
            else:
                st.session_state["mentor_chat"].append({"role": "user", "text": u_text})
                with st.spinner("Showrunner Mentor analyzing and replying..."):
                    chat_context = "\n".join([f"{m['role']}: {m['text']}" for m in st.session_state["mentor_chat"][-6:]])
                    mentor_prompt = f"""
                    You are an elite film school director mentoring a student in Tanglish (Tamil + English).
                    Explain screenplay craft, critique scene descriptions, point out any unfilmable words, and show how to make scenes visual and tense.
                    Conversation History:
                    {chat_context}

                    Reply as Director Mentor:
                    """
                    reply = call_cinematex_ai(api_key, mentor_prompt, expect_json=False)
                    if reply:
                        st.session_state["mentor_chat"].append({"role": "mentor", "text": reply})
                        save_user_progress(st.session_state["user"].id)
                        st.rerun()

        st.write("")
        if st.button("🔄 REVIEW LESSONS FROM START"):
            st.session_state["learn_step"] = 0
            save_user_progress(st.session_state["user"].id)
            st.rerun()

# =============================================================
# 6. SAVED VAULT (WITH LOAD & DELETE)
# =============================================================
elif st.session_state["current_view"] == "SAVED":
    if st.button("⬅️ BACK TO COMMAND NEXUS"):
        set_active_view("HUB")
        st.rerun()

    st.markdown("<h2 style='font-family:Orbitron; color:#ffe600;'>📂 SAVED PROJECTS VAULT</h2>", unsafe_allow_html=True)
    try:
        res = supabase.table("saved_scripts").select("*").eq("user_id", st.session_state["user"].id).order("created_at", desc=True).execute()
        items = res.data or []
        if not items:
            st.info("No saved drafts in the vault.")
        else:
            for item in items:
                col_i1, col_load, col_del = st.columns([3, 1, 0.6])
                is_man = item.get("is_manual", False)
                mode_badge = "✍️ MANUAL SCRIPT" if is_man else "⚡ QUANTUM FORGE"
                with col_i1:
                    st.markdown(f"### 🎬 {item['title']} <span class='time-badge' style='color:#00f0ff; font-size:11px;'>{mode_badge}</span>", unsafe_allow_html=True)
                    st.markdown(f"<span class='time-badge'>SAVED AT: {item.get('saved_at_formatted', 'N/A')}</span>", unsafe_allow_html=True)
                with col_load:
                    if st.button("LOAD SEQUENCE", key=f"load_{item['id']}", use_container_width=True):
                        if is_man:
                            st.session_state["manual_script_input"] = item["script_content"]
                            set_active_view("MANUAL_IDE")
                        else:
                            st.session_state["active_project"] = {
                                "title": item["title"],
                                "script": item["script_content"],
                                "data": item["parsed_data"]
                            }
                            set_active_view("WORKSPACE")
                        st.rerun()
                with col_del:
                    if st.button("🗑️", key=f"del_{item['id']}", use_container_width=True):
                        supabase.table("saved_scripts").delete().eq("id", item["id"]).execute()
                        st.rerun()
                st.divider()
    except Exception as e:
        st.error(f"Error: {e}")

# =============================================================
# 7. EXPORTED DOSSIERS (PDF VAULT)
# =============================================================
elif st.session_state["current_view"] == "EXPORTED":
    if st.button("⬅️ BACK TO COMMAND NEXUS"):
        set_active_view("HUB")
        st.rerun()

    st.markdown("<h2 style='font-family:Orbitron; color:#00f0ff;'>📦 EXPORTED PDF DOSSIERS</h2>", unsafe_allow_html=True)
    try:
        res = supabase.table("saved_scripts").select("*").eq("user_id", st.session_state["user"].id).eq("is_exported", True).order("created_at", desc=True).execute()
        exported_items = res.data or []
        if not exported_items:
            st.info("No exported PDFs found.")
        else:
            for item in exported_items:
                col_e1, col_e2 = st.columns([3, 1])
                with col_e1:
                    st.markdown(f"### 📄 {item['title']}")
                    st.markdown(f"<span class='time-badge'>EXPORTED AT: {item.get('saved_at_formatted', 'N/A')}</span>", unsafe_allow_html=True)
                with col_e2:
                    pdf_data = generate_dossier_pdf(item['title'], item['script_content'], item.get('parsed_data', {}), item.get('saved_at_formatted', ''))
                    st.download_button("⬇️ DOWNLOAD PDF", data=pdf_data, file_name=f"{item['title']}_Dossier.pdf", mime="application/pdf", key=f"dl_{item['id']}", use_container_width=True)
                st.divider()
    except Exception as e:
        st.error(f"Error: {e}")
