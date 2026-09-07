import streamlit as st
from google import genai
from supabase import create_client, Client
import json
import time
from datetime import datetime
import pytz
from fpdf import FPDF
import io

# -------------------------------------------------------------
# CUSTOM CYBER CINEMA FAVICON (SVG DATA-URI)
# -------------------------------------------------------------
CYBER_FAVICON = """data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="14" fill="%230b0717"/>
  <rect x="6" y="6" width="52" height="52" rx="10" fill="none" stroke="%23ff007f" stroke-width="2.5" stroke-dasharray="6,3"/>
  <circle cx="32" cy="32" r="18" fill="%23120b22" stroke="%2300f0ff" stroke-width="3"/>
  <circle cx="32" cy="32" r="9" fill="%23ffe600" opacity="0.9"/>
  <circle cx="32" cy="32" r="4" fill="%23ffffff"/>
  <path d="M32 10 L32 20 M32 44 L32 54 M10 32 L20 32 M44 32 L54 32" stroke="%2300f0ff" stroke-width="2.5" stroke-linecap="round"/>
  <circle cx="48" cy="16" r="3" fill="%23ff007f"/>
</svg>"""

st.set_page_config(
    page_title="CINEMATEX // NEURAL CINEMA DECK",
    page_icon=CYBER_FAVICON,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------------------
# CINEMATEX CYBER-RETRO STYLING & SCROLLBAR ENGINE
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
        font-size: 2.6rem;
        background: linear-gradient(90deg, #ff007f 0%, #00f0ff 50%, #ffe600 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 0px 25px rgba(255, 0, 127, 0.4);
        letter-spacing: 2px;
    }

    .funky-subtitle {
        font-family: 'Orbitron', monospace;
        color: #00f0ff;
        font-size: 0.95rem;
        letter-spacing: 2px;
    }

    .faded-watermark {
        position: relative;
        text-align: center;
        font-family: 'Bungee', sans-serif;
        font-size: 2.5rem;
        color: rgba(0, 240, 255, 0.04);
        text-transform: uppercase;
        letter-spacing: 3px;
        user-select: none;
        pointer-events: none;
        margin-bottom: -35px;
        margin-top: 5px;
    }

    .funky-card {
        background: rgba(20, 14, 38, 0.8);
        border: 2px solid #ff007f;
        box-shadow: 0 0 20px rgba(255, 0, 127, 0.25);
        border-radius: 12px;
        padding: 22px 18px;
        text-align: center;
        min-height: 220px;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .funky-card:hover {
        transform: translateY(-6px) scale(1.02);
        box-shadow: 0 0 35px rgba(0, 240, 255, 0.5);
        border-color: #00f0ff;
    }

    /* Precision Cyber Scrollbar */
    .scroll-container {
        max-height: 560px;
        overflow-y: auto;
        padding-right: 14px;
        margin-top: 10px;
    }
    .scroll-container::-webkit-scrollbar {
        width: 7px;
    }
    .scroll-container::-webkit-scrollbar-track {
        background: #090613;
        border-radius: 4px;
    }
    .scroll-container::-webkit-scrollbar-thumb {
        background: #00f0ff;
        border-radius: 4px;
        box-shadow: 0 0 12px #00f0ff;
    }

    /* Screenplay Display (Courier Standard) */
    .screenplay-box {
        font-family: 'Courier Prime', Courier, monospace;
        background-color: #07090e;
        color: #f8fafc;
        border: 1.5px solid #00f0ff;
        border-radius: 8px;
        padding: 26px;
        line-height: 1.65;
        font-size: 0.95rem;
        white-space: pre-wrap;
        box-shadow: inset 0 0 25px rgba(0, 0, 0, 0.9);
    }

    .cyber-card {
        background: rgba(14, 18, 30, 0.85);
        border: 1px solid rgba(0, 240, 255, 0.25);
        border-left: 5px solid #00f0ff;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 14px;
    }
    .cyber-card-alt { border-left: 5px solid #ff0055; }
    .cyber-card-gold { border-left: 5px solid #ffe600; }
    .cyber-card-purple { border-left: 5px solid #a855f7; }

    .stTextInput input, .stTextArea textarea {
        background-color: #0c0817 !important;
        color: #00f0ff !important;
        border: 1.5px solid #2d1d4f !important;
        border-radius: 8px !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #ff007f !important;
        box-shadow: 0 0 15px rgba(255, 0, 127, 0.5) !important;
    }

    div.stButton > button {
        background: linear-gradient(135deg, #ff007f 0%, #7928ca 100%) !important;
        color: #ffffff !important;
        font-family: 'Orbitron', monospace !important;
        font-weight: 800 !important;
        border: 1px solid #ff007f !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        box-shadow: 0 0 18px rgba(255, 0, 127, 0.4) !important;
    }
    div.stButton > button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 0 28px rgba(0, 240, 255, 0.7) !important;
    }

    .time-badge {
        font-family: 'JetBrains Mono', monospace;
        color: #ffe600;
        background: rgba(255, 230, 0, 0.1);
        border: 1px solid rgba(255, 230, 0, 0.3);
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.8rem;
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

if "user" not in st.session_state:
    st.session_state["user"] = None
if "current_view" not in st.session_state:
    st.session_state["current_view"] = "HUB"
if "active_project" not in st.session_state:
    st.session_state["active_project"] = {"title": "Untitled Sequence", "script": "", "data": None}

def get_current_ist_time():
    tz = pytz.timezone('Asia/Kolkata')
    return datetime.now(tz).strftime("%d %b %Y • %I:%M:%S %p IST")

# -------------------------------------------------------------
# SAFE UNICODE PDF GENERATOR ENGINE (FIXED GEOMETRY)
# -------------------------------------------------------------
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

    # Title & Header
    pdf.set_font("Helvetica", 'B', 18)
    pdf.cell(content_w, 12, safe_pdf_text("CINEMATEX PRODUCTION DOSSIER"), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", 'I', 10)
    pdf.cell(content_w, 8, safe_pdf_text(f"Project: {title} | Forged: {timestamp}"), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(6)
    
    # 1. Screenplay
    pdf.set_font("Helvetica", 'B', 13)
    pdf.cell(content_w, 10, safe_pdf_text("1. INDUSTRY FORMATTED SCREENPLAY"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Courier", '', 9)
    script_content = p_data.get("formatted_script", "No script data.") if isinstance(p_data, dict) else "No script data."
    pdf.multi_cell(content_w, 5, safe_pdf_text(script_content))
    pdf.ln(6)
    
    # 2. Scene Beats
    if isinstance(p_data, dict) and p_data.get("scene_beats"):
        pdf.set_font("Helvetica", 'B', 13)
        pdf.cell(content_w, 10, safe_pdf_text("2. SCENE BEATS & NARRATIVE ARCHITECTURE"), new_x="LMARGIN", new_y="NEXT")
        for b in p_data.get("scene_beats", []):
            t_title = f"- {b.get('scene_title', 'Scene')} [Tone: {b.get('emotional_tone')} | Tension: {b.get('tension_rating')}]"
            pdf.set_font("Helvetica", 'B', 10)
            pdf.cell(content_w, 6, safe_pdf_text(t_title), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", '', 9)
            pdf.multi_cell(content_w, 5, safe_pdf_text(f"Progression: {b.get('micro_beats', '')}"))
            pdf.multi_cell(content_w, 5, safe_pdf_text(f"Director Staging: {b.get('director_vision', '')}"))
            pdf.ln(2)
        pdf.ln(6)

    # 3. Character Bible
    if isinstance(p_data, dict) and p_data.get("characters"):
        pdf.set_font("Helvetica", 'B', 13)
        pdf.cell(content_w, 10, safe_pdf_text("3. CHARACTER PSYCHOLOGY & BIBLE"), new_x="LMARGIN", new_y="NEXT")
        for c in p_data.get("characters", []):
            pdf.set_font("Helvetica", 'B', 10)
            pdf.cell(content_w, 6, safe_pdf_text(f"- {c.get('name', '')} ({c.get('role', '')})"), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", '', 9)
            pdf.multi_cell(content_w, 5, safe_pdf_text(f"Visual & Attire: {c.get('appearance', '')}"))
            pdf.multi_cell(content_w, 5, safe_pdf_text(f"Mannerisms: {c.get('quirks', '')}"))
            pdf.multi_cell(content_w, 5, safe_pdf_text(f"Core Conflict: {c.get('core_conflict', '')}"))
            pdf.ln(2)
        pdf.ln(6)

    # 4. Storyboard Prompts
    if isinstance(p_data, dict) and p_data.get("storyboard_prompts"):
        pdf.set_font("Helvetica", 'B', 13)
        pdf.cell(content_w, 10, safe_pdf_text("4. DETAILED STORYBOARD PROMPTS (MIDJOURNEY / FLUX)"), new_x="LMARGIN", new_y="NEXT")
        for idx, p in enumerate(p_data.get("storyboard_prompts", []), 1):
            pdf.set_font("Helvetica", 'B', 9)
            pdf.cell(content_w, 6, safe_pdf_text(f"Frame {idx} Prompt:"), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", 'I', 8)
            pdf.multi_cell(content_w, 5, safe_pdf_text(p))
            pdf.ln(2)

    return bytes(pdf.output())

# =============================================================
# 1. AUTHENTICATION GATEWAY
# =============================================================
if st.session_state["user"] is None:
    st.write("")
    st.markdown('<div class="funky-title" style="text-align:center;">⚡ CINEMATEX // ACCESS</div>', unsafe_allow_html=True)
    st.markdown('<div class="funky-subtitle" style="text-align:center;">NEURAL PRE-PRODUCTION ENGINE FOR SCREENWRITERS</div>', unsafe_allow_html=True)
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
                    st.error("Please fill both Email & Password!")
                else:
                    try:
                        res = supabase.auth.sign_in_with_password({"email": email.strip(), "password": password})
                        st.session_state["user"] = res.user
                        st.session_state["current_view"] = "HUB"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Login failed: {e}")
        else:
            if st.button("✨ FORGE MY CREATOR ACCOUNT", use_container_width=True):
                if not email or not password:
                    st.error("Please enter email & password!")
                else:
                    try:
                        res = supabase.auth.sign_up({"email": email.strip(), "password": password})
                        if res.user:
                            st.session_state["user"] = res.user
                            st.session_state["current_view"] = "HUB"
                            st.success("Account activated! Redirecting...")
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
        supabase.auth.sign_out()
        st.session_state["user"] = None
        st.session_state["current_view"] = "HUB"
        st.rerun()

# =============================================================
# 2. STUDIO COMMAND NEXUS (HUB) - WITH 4 PILLARS
# =============================================================
if st.session_state["current_view"] == "HUB":
    st.write("")
    st.markdown("<h2 style='text-align:center; font-family:Orbitron; color:#ffe600;'>⚡ STUDIO COMMAND NEXUS</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#94a3b8;'>Select your pre-production trajectory or master the craft below</p>", unsafe_allow_html=True)
    st.write("")

    col_h1, col_h2, col_h3, col_h4 = st.columns(4, gap="small")
    
    with col_h1:
        st.markdown("""
        <div class="funky-card">
            <h1 style="margin:0;">🚀</h1>
            <h4 style="color:#00f0ff; margin-top:8px;">QUANTUM FORGE</h4>
            <p style="color:#94a3b8; font-size:13px;">Convert raw story passages into Courier scripts & breakdown matrices.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("ENTER WORKSPACE ➔", key="btn_new", use_container_width=True):
            st.session_state["active_project"] = {"title": "Untitled Sequence", "script": "", "data": None}
            st.session_state["current_view"] = "WORKSPACE"
            st.rerun()

    with col_h2:
        st.markdown("""
        <div class="funky-card" style="border-color:#a855f7; box-shadow:0 0 20px rgba(168, 85, 247, 0.25);">
            <h1 style="margin:0;">🎓</h1>
            <h4 style="color:#c084fc; margin-top:8px;">WRITING ACADEMY</h4>
            <p style="color:#94a3b8; font-size:13px;">Master screenplay formatting, 3-act structure, beats & subtext step-by-step.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("START MASTERCLASS ➔", key="btn_academy", use_container_width=True):
            st.session_state["current_view"] = "ACADEMY"
            st.rerun()

    with col_h3:
        st.markdown("""
        <div class="funky-card" style="border-color:#ffe600; box-shadow:0 0 20px rgba(255, 230, 0, 0.2);">
            <h1 style="margin:0;">📂</h1>
            <h4 style="color:#ffe600; margin-top:8px;">SAVED VAULT</h4>
            <p style="color:#94a3b8; font-size:13px;">Load or delete saved drafts preserved with precise timestamps.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("OPEN VAULT ➔", key="btn_saved", use_container_width=True):
            st.session_state["current_view"] = "SAVED"
            st.rerun()

    with col_h4:
        st.markdown("""
        <div class="funky-card" style="border-color:#00f0ff; box-shadow:0 0 20px rgba(0, 240, 255, 0.2);">
            <h1 style="margin:0;">📦</h1>
            <h4 style="color:#00f0ff; margin-top:8px;">EXPORTED DOSSIERS</h4>
            <p style="color:#94a3b8; font-size:13px;">Download packaged cinema production kits directly as PDF documents.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("ACCESS PDFS ➔", key="btn_exported", use_container_width=True):
            st.session_state["current_view"] = "EXPORTED"
            st.rerun()

# =============================================================
# 3. SCRIPT WRITING ACADEMY (LEVEL-BY-LEVEL MASTERCLASS)
# =============================================================
elif st.session_state["current_view"] == "ACADEMY":
    col_aback, col_ahead = st.columns([1, 4])
    with col_aback:
        if st.button("⬅️ COMMAND NEXUS"):
            st.session_state["current_view"] = "HUB"
            st.rerun()
    with col_ahead:
        st.markdown("<h2 style='font-family:Orbitron; color:#c084fc; margin:0;'>🎓 CINEMATEX SCREENWRITING ACADEMY</h2>", unsafe_allow_html=True)
        st.caption("From Raw Narrative Thought to Industry Mastercraft // Level-by-Level Curriculum")

    st.write("")

    # Level Selector Tabs
    lvl_tab1, lvl_tab2, lvl_tab3, lvl_tab4, lvl_tab5 = st.tabs([
        "LEVEL 1: SCRIPT ANATOMY",
        "LEVEL 2: 3-ACT ARCHITECTURE",
        "LEVEL 3: CHARACTER MOTIVES",
        "LEVEL 4: SCENE TENSION & SUBTEXT",
        "LEVEL 5: RAW PASSAGE VS COURIER SCRIPT"
    ])

    # LEVEL 1
    with lvl_tab1:
        st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
        st.markdown("""
        <div class="cyber-card cyber-card-purple">
            <h3 style="color:#c084fc; margin:0;">LEVEL 1: THE 5 SACRED ELEMENTS OF A SCREENPLAY</h3>
            <p style="color:#94a3b8; font-size:14px; margin-top:4px;">A script is not a novel; it is an architectural blueprint for camera, actors, and sound.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        ### 1. Scene Heading (Slugline)
        Tells the production crew **Where** and **When** the camera is rolling.
        * **INT.** (Interior) / **EXT.** (Exterior)
        * Location (e.g. `MADRAS CENTRAL PLATFORM 4`)
        * Time (e.g. `NIGHT`, `DAWN`, `CONTINUOUS`)
        > **Example:** `EXT. ABANDONED HARBOR WAREHOUSE - RAINY NIGHT`

        ### 2. Action Lines
        Visual and auditory descriptions only. **Rule: If the camera cannot capture it or the mic cannot record it, do NOT write it.**
        * ❌ *Wrong:* "Vikram is thinking about his mother's murder 10 years ago." *(Mind thoughts cannot be seen!)*
        * ✅ *Right:* "Vikram stares down at a tarnished gold watch, his knuckles white around the glass face. Rain lashes against his collar."

        ### 3. Character Cue
        The name of the character speaking, capitalized and centered before dialogue:
        > `VIKRAM` or `VIKRAM (V.O.)` for Voice-Over / `(O.S.)` for Off-Screen.

        ### 4. Parenthetical
        An actor directive indicating attitude or micro-action. Use sparingly:
        > `(whispering through clenched teeth)`

        ### 5. Dialogue
        What the character actually says out loud. Keep it distinct to their vocal rhythm.
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    # LEVEL 2
    with lvl_tab2:
        st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
        st.markdown("""
        <div class="cyber-card">
            <h3 style="color:#00f0ff; margin:0;">LEVEL 2: THE HOLLYWOOD & TAMIL CINEMA 3-ACT MATRIX</h3>
            <p style="color:#94a3b8; font-size:14px; margin-top:4px;">How 120 minutes of cinema maintains relentless pacing without losing audience attention.</p>
        </div>
        """, unsafe_allow_html=True)

        col_act1, col_act2, col_act3 = st.columns(3)
        with col_act1:
            st.markdown("""
            #### ACT I: THE SETUP (Pages 1-30)
            * **Ordinary World:** Show protagonist's daily routine & internal flaw.
            * **Inciting Incident (Minute 10-12):** The disruptive event that shatters peace (e.g., murder, heist call, impossible discovery).
            * **Plot Point 1 (Minute 25-30):** Point of No Return. Protagonist steps into the storm.
            """)
        with col_act2:
            st.markdown("""
            #### ACT II: CONFLICT & CRISIS (Pages 30-85)
            * **Fun & Games / Trials:** First battles, chasing leads.
            * **Midpoint Shift (Minute 55-60):** False victory or massive betrayal; stakes turn life-or-death.
            * **All Hope Lost / Dark Night of Soul:** Protagonist hits rock bottom. Mentor falls or resources exhausted.
            """)
        with col_act3:
            st.markdown("""
            #### ACT III: RESOLUTION (Pages 85-115)
            * **The Climax:** Final confrontation where external enemy and internal flaw are both conquered.
            * **Catharsis:** Emotional payoff.
            * **New Equilibrium:** The transformed world.
            """)
        st.markdown('</div>', unsafe_allow_html=True)

    # LEVEL 3
    with lvl_tab3:
        st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
        st.markdown("""
        <div class="cyber-card cyber-card-alt">
            <h3 style="color:#ff0055; margin:0;">LEVEL 3: CHARACTER PSYCHOLOGY & THE FATAL FLAW</h3>
            <p style="color:#94a3b8; font-size:14px; margin-top:4px;">Great characters are not born from cool costumes; they are defined by their internal contradiction.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        ### The Trinity Engine of Character Design:
        1. **The External WANT (Goal):** What the character chases consciously (e.g., Revenge against the drug cartel, finding stolen millions).
        2. **The Internal NEED (Spiritual Growth):** What the character actually needs to become whole (e.g., Forgiving themselves for past guilt, learning to trust others).
        3. **The Fatal Flaw (The Ghost):** The trauma or stubborn weakness that blinds them throughout Act I & II.
        
        > **Golden Pro-Tip:** A protagonist and antagonist should be two sides of the same coin. An ideal antagonist is the protagonist who made the wrong moral choice at their crossroad!
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    # LEVEL 4
    with lvl_tab4:
        st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
        st.markdown("""
        <div class="cyber-card cyber-card-gold">
            <h3 style="color:#ffe600; margin:0;">LEVEL 4: SUBTEXT & "SHOW, DON'T TELL"</h3>
            <p style="color:#94a3b8; font-size:14px; margin-top:4px;">Amateurs write what characters think; masters write what characters hide.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        ### What is Subtext?
        Subtext is the silent emotion flowing underneath dialogue lines. When people are angry or grieving, they rarely say "I am hurt." They attack something else.
        
        * **Flat Dialogue (Zero Subtext):**
          * *A:* "I am divorcing you because you don't love me anymore."
          * *B:* "I am sad and guilty."
        * **Cinematic Subtext Dialogue:**
          * *A sets down a cup of cold tea without drinking it.*
          * *A:* "You forgot the sugar again."
          * *B stares at the cup.*
          * *B:* "I've been remembering it for fifteen years, Priya."
          * *(Audience understands: It's not about the sugar; the marriage is dead.)*

        ### Micro-Tension in Scene Beats:
        Every scene MUST enter with one status and exit with a reversed status (e.g., Hopeful ➔ Crushed, or Dominant ➔ Trapped). If a scene ends the same way it began, **CUT IT OUT.**
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    # LEVEL 5
    with lvl_tab5:
        st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
        st.markdown("""
        <div class="cyber-card">
            <h3 style="color:#00f0ff; margin:0;">LEVEL 5: MASTERCLASS TRANSFORMATION LAB</h3>
            <p style="color:#94a3b8; font-size:14px; margin-top:4px;">Observe how a raw conversational story draft evolves into an authentic film blueprint.</p>
        </div>
        """, unsafe_allow_html=True)

        col_t_left, col_t_right = st.columns(2)
        with col_t_left:
            st.markdown("#### 📝 RAW CONVERSATIONAL PASSAGE")
            st.info("""
            "Oru tea shop irukku night mazhai la. Vikram tea குடிச்சிட்டு irukkan. Appo oru black car vandhu nilludhu. Adhula irundhu oru aal erangi varan. Vikram-ah paathu 'Innum nee uyiroda irukiya' nu kekuran. Vikram sirichite avana shoot pannidran."
            """)
        with col_t_right:
            st.markdown("#### 📜 INDUSTRY COURIER SCREENPLAY (STANDARDIZED)")
            st.markdown("""
            <div class="screenplay-box" style="font-size:0.85rem; padding:15px;">
EXT. ROADSIDE TEA STALL - NIGHT (RAINING)

Rain hammers against a rusted zinc sheet. Drops sizzle on a boiling milk kettle.

VIKRAM (30s), drenched khaki jacket, sips black tea from a cracked tumbler. Steam veils his eyes.

Headlights cut through the downpour. A matte-black Scorpio pulls up, engine purring like a caged beast.

The door creaks open. DURAISAMY (50s) steps into the mud, his white veshti speckled with grease. He pulls a brass lighter, sparks a cigarette.

DURAISAMY
(smirking through smoke)
Ten years in the swamp... innum uyiroda 
dhaan irukiya, Vikram?

Vikram doesn't blink. He slowly lowers the glass tumbler onto the wooden plank.

VIKRAM
(calm, flat)
Oru tea kudika kooda nimadhi illa.

UNDER THE BENCH --

Vikram's right hand smoothly uncocks a snub-nosed revolver.

BANG!

Muzzle flash illuminates the pouring rain. Duraisamy's smirk freezes.
            </div>
            """, unsafe_allow_html=True)
        
        st.write("")
        if st.button("🚀 READY TO FORGE MY STORY IN WORKSPACE ➔", use_container_width=True):
            st.session_state["current_view"] = "WORKSPACE"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# =============================================================
# 4. WORKSPACE (QUANTUM FORGE)
# =============================================================
elif st.session_state["current_view"] == "WORKSPACE":
    if st.button("⬅️ BACK TO COMMAND NEXUS"):
        st.session_state["current_view"] = "HUB"
        st.rerun()

    col_side, col_main = st.columns([1, 2.5], gap="medium")
    
    with col_side:
        st.markdown("### 🕹️ CONTROLS & ENGINE")
        
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        if api_key:
            st.markdown("<span class='time-badge' style='color:#00f0ff; border-color:#00f0ff;'>⚡ NEURAL ENGINE: LINKED & ACTIVE</span>", unsafe_allow_html=True)
        else:
            api_key = st.text_input("GEMINI API KEY (Optional Override)", type="password")

        project_title = st.text_input("PROJECT TITLE", value=st.session_state["active_project"]["title"])
        
        script_input = st.text_area(
            "INPUT STORY PASSAGE / SUMMARY / DIALOGUE:",
            value=st.session_state["active_project"]["script"],
            height=340,
            placeholder="Unkitta oru kadhai solra pola normal passage ezhudhunaalum seri, Tanglish or Tamil dialogues potalum seri... Engine idhai Hollywood/Tamil cinema standard script-a mathidum..."
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
                        "is_exported": False
                    }).execute()
                    st.success(f"Project safely preserved at {ts}")
                except Exception as err:
                    st.error(f"Database error: {err}")

    with col_main:
        st.markdown("### 📊 PRODUCTION MATRIX")
        tab_script, tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📜 INDUSTRY SCREENPLAY",
            "⚡ SCENE BEATS",
            "👤 CHARACTER BIBLE",
            "🎥 SHOT LIST",
            "🎨 STORYBOARD PROMPTS",
            "📄 EXPORT PDF DOSSIER"
        ])

        if forge_btn:
            if not api_key:
                st.error("Gemini API Key missing! Check Secrets or input.")
            elif not script_input.strip():
                st.warning("Provide a story passage to forge!")
            else:
                with st.spinner("Cinematex Neural Engine decomposing narrative & engineering deep production matrix..."):
                    prompt = f"""
                    You are an elite cinema director, script doctor, and cinematographer with mastery over both Indian/Tamil cinema (mass-class balance, subtext, high tension) and global Hollywood standards.
                    Input text (may be casual narrative passage, rough storyline, or dialogues in Tamil, Tanglish, or English):
                    ---
                    {script_input}
                    ---
                    YOUR MISSION: Generate deep, highly granular, production-ready cinema intelligence.
                    
                    REQUIREMENTS:
                    1. "formatted_script": Convert the passage into a flawless, industry-standard screenplay format (SLUGLINES e.g. INT. / EXT. - LOCATION - TIME, descriptive visual action paragraphs, CHARACTER NAMES centered in uppercase, parentheticals, sharp dialogue). Preserve the exact emotion, core story essence, and linguistic tone (Tamil/Tanglish/English) of the input.
                    2. "scene_beats": Highly detailed analysis of story beats. Return a list of items each having:
                       - "scene_title": Scene identifier
                       - "emotional_tone": Specific emotional rhythm
                       - "tension_rating": e.g., "88% Peak Climax"
                       - "micro_beats": Step-by-step conflict shifts and escalation within the scene
                       - "director_vision": Director's visual subtext, actor staging notes, and underlying thematic meaning
                    3. "characters": Deep character breakdown. Return a list of items each having:
                       - "name": Character name
                       - "role": Protagonist / Antagonist / Foil
                       - "appearance": Detailed physical description, costume textures, color palette psychology
                       - "quirks": Body language nuances, eye contact habits, vocal traits
                       - "core_conflict": Deep internal emotional struggle vs outer physical obstacle
                    4. "shot_list": Highly technical cinematic camera list. Return a list of items each having:
                       - "scene_no": Scene/Shot #
                       - "shot_type": e.g., "Extreme Low-Angle Dolly In (35mm Anamorphic)"
                       - "camera_angle": Precise angle & movement (Jib, Pan, Steadicam tracking)
                       - "lighting_setup": Specific lighting breakdown (Key light, low-key neon rim, volumetric fog, color temperature)
                       - "sound_cue": Foley textures, sub-bass pulse, dielectric score notes
                    5. "storyboard_prompts": ULTRA-DETAILED, photorealistic AI image generation prompts optimized for Midjourney v6 and Flux. 
                       Format each prompt with: Subject detail, framing & camera lens (e.g., 35mm Arri Alexa Mini LF, shallow depth of field), lighting style, environmental atmosphere, cinematic color grade, 8k resolution, photorealistic, cinematic movie still, --ar 16:9.

                    Return STRICT valid JSON only with this schema:
                    {{
                        "formatted_script": "string",
                        "scene_beats": [ {{"scene_title": "", "emotional_tone": "", "tension_rating": "", "micro_beats": "", "director_vision": ""}} ],
                        "characters": [ {{"name": "", "role": "", "appearance": "", "quirks": "", "core_conflict": ""}} ],
                        "shot_list": [ {{"scene_no": "", "shot_type": "", "camera_angle": "", "lighting_setup": "", "sound_cue": ""}} ],
                        "storyboard_prompts": [ "string" ]
                    }}
                    """
                    client = genai.Client(api_key=api_key)
                    models = ['gemini-3.5-flash-lite', 'gemini-3.7-flash', 'gemini-3.6-flash']
                    res = None
                    for m in models:
                        try:
                            res = client.models.generate_content(
                                model=m,
                                contents=prompt,
                                config={'response_mime_type': 'application/json'}
                            )
                            if res and res.text:
                                break
                        except Exception:
                            time.sleep(1)

                    if res and res.text:
                        clean_json = res.text.strip().replace("```json", "").replace("```", "")
                        parsed = json.loads(clean_json)
                        st.session_state["active_project"]["data"] = parsed
                        st.session_state["active_project"]["script"] = script_input
                        st.session_state["active_project"]["title"] = project_title
                        st.success("CINEMATEX FORGE SUCCESSFUL // ALL MATRICES SYNCHRONIZED")

        p_data = st.session_state["active_project"].get("data")
        if p_data:
            # TAB 0: SCREENPLAY
            with tab_script:
                st.caption("COURIER PRIME CINEMA STANDARD SCREENPLAY:")
                script_formatted = p_data.get("formatted_script", "Script not ready.")
                st.markdown(f'<div class="scroll-container"><div class="screenplay-box">{script_formatted}</div></div>', unsafe_allow_html=True)

            # TAB 1: SCENE BEATS
            with tab1:
                st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
                for b in p_data.get("scene_beats", []):
                    st.markdown(f"""
                    <div class="cyber-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h4 style="color:#00f0ff; margin:0;">⚡ {b.get('scene_title', 'SCENE')}</h4>
                            <span class="time-badge">{b.get('emotional_tone')} • TENSION: {b.get('tension_rating')}</span>
                        </div>
                        <p style="margin-top:10px; color:#e2e8f0; font-size:15px;"><b>Micro-Beats & Progression:</b><br>{b.get('micro_beats', '')}</p>
                        <p style="color:#94a3b8; font-size:14px; margin:0;"><b>Director Subtext & Staging:</b> {b.get('director_vision', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # TAB 2: CHARACTER BIBLE
            with tab2:
                st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
                for c in p_data.get("characters", []):
                    st.markdown(f"""
                    <div class="cyber-card cyber-card-alt">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h3 style="color:#ff0055; margin:0;">👤 {c.get('name', 'UNKNOWN')}</h3>
                            <span class="time-badge" style="color:#ff0055; border-color:#ff0055;">{c.get('role', '')}</span>
                        </div>
                        <div style="margin-top:8px; font-size:14px;"><b style="color:#00f0ff;">Visual Texture & Costumes:</b> {c.get('appearance', '')}</div>
                        <div style="margin-top:5px; font-size:14px;"><b style="color:#ffe600;">Mannerisms & Behavioral Quirks:</b> {c.get('quirks', '')}</div>
                        <div style="margin-top:5px; font-size:14px;"><b style="color:#ff0055;">Internal vs External Conflict:</b> {c.get('core_conflict', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # TAB 3: SHOT LIST
            with tab3:
                st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
                st.dataframe(p_data.get("shot_list", []), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # TAB 4: STORYBOARD PROMPTS
            with tab4:
                st.caption("ULTRA-DETAILED PROMPTS (READY TO COPY INTO MIDJOURNEY V6 / FLUX):")
                st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
                for i, p in enumerate(p_data.get("storyboard_prompts", []), 1):
                    st.markdown(f"**Shot {i} Production Frame:**")
                    st.code(p, language="text")
                st.markdown('</div>', unsafe_allow_html=True)

            # TAB 5: EXPORT PDF DOSSIER
            with tab5:
                st.markdown("### 📄 DIRECT PDF PRODUCTION DOSSIER")
                st.write("Full screenplay, narrative architecture, character dossiers, shot lists, and storyboard prompts compiled into an official PDF document.")
                
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
                        "is_exported": True
                    }).execute()
                    st.success("PDF exported and archived into Exported Dossiers!")

# =============================================================
# 5. SAVED VAULT (WITH LOAD & PERMANENT DELETE)
# =============================================================
elif st.session_state["current_view"] == "SAVED":
    if st.button("⬅️ BACK TO COMMAND NEXUS"):
        st.session_state["current_view"] = "HUB"
        st.rerun()

    st.markdown("<h2 style='font-family:Orbitron; color:#ffe600;'>📂 SAVED PROJECTS VAULT</h2>", unsafe_allow_html=True)
    st.caption("Projects preserved with exact timestamps")
    
    try:
        res = supabase.table("saved_scripts").select("*").eq("user_id", st.session_state["user"].id).order("created_at", desc=True).execute()
        items = res.data or []
        if not items:
            st.info("No saved drafts in the vault.")
        else:
            for item in items:
                col_i1, col_load, col_del = st.columns([3, 1, 0.6])
                with col_i1:
                    st.markdown(f"### 🎬 {item['title']}")
                    st.markdown(f"<span class='time-badge'>SAVED AT: {item.get('saved_at_formatted', 'N/A')}</span>", unsafe_allow_html=True)
                with col_load:
                    if st.button("LOAD SEQUENCE", key=f"load_{item['id']}", use_container_width=True):
                        st.session_state["active_project"] = {
                            "title": item["title"],
                            "script": item["script_content"],
                            "data": item["parsed_data"]
                        }
                        st.session_state["current_view"] = "WORKSPACE"
                        st.rerun()
                with col_del:
                    if st.button("🗑️", key=f"del_{item['id']}", help="Delete Project Permanently", use_container_width=True):
                        supabase.table("saved_scripts").delete().eq("id", item["id"]).execute()
                        st.rerun()
                st.divider()
    except Exception as e:
        st.error(f"Error accessing vault: {e}")

# =============================================================
# 6. EXPORTED DOSSIERS (PDF VAULT)
# =============================================================
elif st.session_state["current_view"] == "EXPORTED":
    if st.button("⬅️ BACK TO COMMAND NEXUS"):
        st.session_state["current_view"] = "HUB"
        st.rerun()

    st.markdown('<div class="faded-watermark">YOU CAN DOWNLOAD YOUR PROJECT FROM HERE</div>', unsafe_allow_html=True)
    st.markdown("<h2 style='font-family:Orbitron; color:#00f0ff; position:relative;'>📦 EXPORTED PDF DOSSIERS</h2>", unsafe_allow_html=True)
    st.caption("Download packaged PDF production dossiers")
    st.write("")

    try:
        res = supabase.table("saved_scripts").select("*").eq("user_id", st.session_state["user"].id).eq("is_exported", True).order("created_at", desc=True).execute()
        exported_items = res.data or []
        
        if not exported_items:
            st.info("No projects exported as PDF yet. Head to Workspace ➔ Export PDF Dossier tab!")
        else:
            for item in exported_items:
                col_e1, col_e2 = st.columns([3, 1])
                with col_e1:
                    st.markdown(f"### 📄 {item['title']} - Cinema PDF Kit")
                    st.markdown(f"<span class='time-badge'>EXPORTED AT: {item.get('saved_at_formatted', 'N/A')}</span>", unsafe_allow_html=True)
                with col_e2:
                    p_data = item.get('parsed_data', {})
                    pdf_data = generate_dossier_pdf(item['title'], item['script_content'], p_data, item.get('saved_at_formatted', ''))
                    st.download_button(
                        label="⬇️ DOWNLOAD PDF",
                        data=pdf_data,
                        file_name=f"{item['title'].replace(' ', '_')}_Dossier.pdf",
                        mime="application/pdf",
                        key=f"dl_pdf_{item['id']}",
                        use_container_width=True
                    )
                st.divider()
    except Exception as e:
        st.error(f"Error fetching exported files: {e}")
