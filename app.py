import streamlit as st
from google import genai
from supabase import create_client, Client
import json
import time
from datetime import datetime
import pytz
from fpdf import FPDF

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
# CYBERPUNK HUD & MASTERCLASS STYLING
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

    .hero-learn-card {
        background: linear-gradient(135deg, rgba(32, 14, 66, 0.9) 0%, rgba(13, 8, 28, 0.95) 100%);
        border: 2px solid #a855f7;
        box-shadow: 0 0 25px rgba(168, 85, 247, 0.4);
        border-radius: 14px;
        padding: 26px 30px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    .hero-learn-card:hover {
        border-color: #00f0ff;
        box-shadow: 0 0 35px rgba(0, 240, 255, 0.5);
    }

    .mini-card {
        background: rgba(18, 12, 34, 0.8);
        border: 1.5px solid #2e1d50;
        border-radius: 10px;
        padding: 16px 14px;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .mini-card:hover {
        transform: translateY(-4px);
        border-color: #00f0ff;
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.3);
    }

    .scroll-container {
        max-height: 560px;
        overflow-y: auto;
        padding-right: 14px;
        margin-top: 10px;
    }
    .scroll-container::-webkit-scrollbar { width: 7px; }
    .scroll-container::-webkit-scrollbar-track { background: #090613; border-radius: 4px; }
    .scroll-container::-webkit-scrollbar-thumb { background: #00f0ff; border-radius: 4px; box-shadow: 0 0 12px #00f0ff; }

    .screenplay-box {
        font-family: 'Courier Prime', Courier, monospace;
        background-color: #07090e;
        color: #f8fafc;
        border: 1.5px solid #00f0ff;
        border-radius: 8px;
        padding: 24px;
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

    .game-hud {
        background: rgba(10, 8, 20, 0.9);
        border: 1.5px solid #ffe600;
        border-radius: 10px;
        padding: 14px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        box-shadow: 0 0 15px rgba(255, 230, 0, 0.2);
    }

    .stTextInput input, .stTextArea textarea {
        background-color: #0c0817 !important;
        color: #00f0ff !important;
        border: 1.5px solid #2d1d4f !important;
        border-radius: 8px !important;
        font-family: 'JetBrains Mono', monospace !important;
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
if "game_xp" not in st.session_state:
    st.session_state["game_xp"] = 150
if "dojo_feedback" not in st.session_state:
    st.session_state["dojo_feedback"] = {}
if "dialogue_duel_chat" not in st.session_state:
    st.session_state["dialogue_duel_chat"] = [
        {"role": "mentor", "text": "Vanakkam Director! Script writing-na kadhai solradhu mattum illa, oru production blueprint create panradhu. Naan ungaloda Showrunner Mentor. Indha 6 missions mudicha neenga innorutharukku masterclass edukalaam. Ready-ah?"}
    ]

def get_current_ist_time():
    tz = pytz.timezone('Asia/Kolkata')
    return datetime.now(tz).strftime("%d %b %Y • %I:%M:%S %p IST")

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

# -------------------------------------------------------------
# SAFE PDF GENERATOR
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

# =============================================================
# 1. AUTHENTICATION GATEWAY
# =============================================================
if st.session_state["user"] is None:
    st.write("")
    st.markdown('<div class="funky-title" style="text-align:center;">⚡ CINEMATEX // ACCESS</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center; color:#00f0ff; font-family:Orbitron;">NEURAL PRE-PRODUCTION DECK & SCREENPLAY DOJO</div>', unsafe_allow_html=True)
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
                        st.session_state["current_view"] = "HUB"
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
                            st.session_state["current_view"] = "HUB"
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
    rank_title = "SCRIPT APPRENTICE" if st.session_state['game_xp'] < 300 else ("SCENE DOCTOR" if st.session_state['game_xp'] < 600 else "MASTER SHOWRUNNER")
    st.markdown(f"<div style='margin-top:12px; font-size:13px; color:#94a3b8;'>DIRECTOR: <b style='color:#00f0ff;'>{st.session_state['user'].email}</b> | RANK: <b style='color:#ff007f;'>{rank_title}</b> | XP: <b style='color:#ffe600;'>{st.session_state['game_xp']} XP</b></div>", unsafe_allow_html=True)
with col_nav3:
    if st.button("🚪 LOGOUT", use_container_width=True):
        supabase.auth.sign_out()
        st.session_state["user"] = None
        st.session_state["current_view"] = "HUB"
        st.rerun()

# =============================================================
# 2. STUDIO COMMAND NEXUS (HUB)
# =============================================================
if st.session_state["current_view"] == "HUB":
    st.write("")
    st.markdown("<h2 style='text-align:center; font-family:Orbitron; color:#ffe600;'>⚡ STUDIO COMMAND NEXUS</h2>", unsafe_allow_html=True)
    st.write("")

    # TOP BIG HERO: SCRIPTWRITING MASTERCLASS & DOJO
    st.markdown("""
    <div class="hero-learn-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <span class="time-badge" style="color:#c084fc; border-color:#c084fc;">COMPLETE SCREENPLAY CURRICULUM // ZERO TO SHOWRUNNER</span>
                <h2 style="font-family:Orbitron; color:#00f0ff; margin-top:8px; margin-bottom:4px;">🎓 SCRIPTWRITING MASTERCLASS & DOJO QUEST</h2>
                <p style="color:#e2e8f0; font-size:15px; margin:0;">In-depth 6-tier screenwriting academy. Master sluglines, foley camera actions, subtext psychology, 3-act tension, and battle the AI Showrunner live!</p>
            </div>
            <div style="font-size:3.5rem;">🎮</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("ENTER ACADEMY & WRITING DOJO ➔", use_container_width=True):
        st.session_state["current_view"] = "LEARN_DOJO"
        st.rerun()

    st.write("")
    st.markdown("<h4 style='font-family:Orbitron; color:#94a3b8;'>PRODUCTION ENGINES // 3 WORKSPACE DOMAINS</h4>", unsafe_allow_html=True)

    col_sub1, col_sub2, col_sub3 = st.columns(3, gap="medium")
    with col_sub1:
        st.markdown("""
        <div class="mini-card">
            <h2 style="margin:0;">🚀</h2>
            <h4 style="color:#00f0ff; margin-top:6px;">QUANTUM FORGE</h4>
            <p style="color:#94a3b8; font-size:12px;">Convert raw passages into Courier screenplay & shot lists.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("LAUNCH FORGE ➔", key="btn_forge", use_container_width=True):
            st.session_state["active_project"] = {"title": "Untitled Sequence", "script": "", "data": None}
            st.session_state["current_view"] = "WORKSPACE"
            st.rerun()

    with col_sub2:
        st.markdown("""
        <div class="mini-card">
            <h2 style="margin:0;">📂</h2>
            <h4 style="color:#ffe600; margin-top:6px;">SAVED VAULT</h4>
            <p style="color:#94a3b8; font-size:12px;">Access or delete stored projects with IST timestamps.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("OPEN VAULT ➔", key="btn_vault", use_container_width=True):
            st.session_state["current_view"] = "SAVED"
            st.rerun()

    with col_sub3:
        st.markdown("""
        <div class="mini-card">
            <h2 style="margin:0;">📦</h2>
            <h4 style="color:#ff007f; margin-top:6px;">EXPORTED DOSSIERS</h4>
            <p style="color:#94a3b8; font-size:12px;">Download compiled production packages as official PDF files.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("VIEW PDFS ➔", key="btn_dossier", use_container_width=True):
            st.session_state["current_view"] = "EXPORTED"
            st.rerun()

# =============================================================
# 3. COMPREHENSIVE SCRIPTWRITING DOJO (6 COMPLETE MISSIONS)
# =============================================================
elif st.session_state["current_view"] == "LEARN_DOJO":
    col_lback, col_lhead = st.columns([1, 4])
    with col_lback:
        if st.button("⬅️ COMMAND NEXUS"):
            st.session_state["current_view"] = "HUB"
            st.rerun()
    with col_lhead:
        st.markdown("<h2 style='font-family:Orbitron; color:#c084fc; margin:0;'>🎮 THE CINEMATEX SCREENPLAY DOJO</h2>", unsafe_allow_html=True)
        st.caption("Comprehensive 6-Tier Curriculum: Learn the deep theory, then conquer the interactive challenge to earn XP.")

    st.write("")

    # Player HUD Bar
    st.markdown(f"""
    <div class="game-hud">
        <div>
            <span style="color:#94a3b8; font-size:12px;">ACTIVE RANK:</span><br>
            <b style="color:#00f0ff; font-family:Orbitron; font-size:17px;">LEVEL {1 + st.session_state['game_xp']//100} • {rank_title}</b>
        </div>
        <div>
            <span style="color:#94a3b8; font-size:12px;">DIRECTOR XP:</span><br>
            <b style="color:#ffe600; font-family:Orbitron; font-size:17px;">⚡ {st.session_state['game_xp']} XP</b>
        </div>
        <div>
            <span style="color:#94a3b8; font-size:12px;">DOJO MASTERY:</span><br>
            <b style="color:#ff007f; font-family:Orbitron; font-size:17px;">{min(100, int((st.session_state['game_xp']/600)*100))}% SYNCHRONIZED</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4, m5, m6 = st.tabs([
        "LVL 1: SLUGLINE & GEOGRAPHY",
        "LVL 2: SHOW DON'T TELL",
        "LVL 3: SUBTEXT & STATUS",
        "LVL 4: 3-ACT TENSION GRAPH",
        "LVL 5: BLOCKING & TRANSITIONS",
        "LVL 6: SHOWRUNNER CAPSTONE"
    ])

    api_key = st.secrets.get("GEMINI_API_KEY", "")

    # ---------------- LEVEL 1 ----------------
    with m1:
        st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
        st.markdown("""
        <div class="cyber-card">
            <h3 style="color:#00f0ff; margin:0;">LEVEL 1 THEORY: THE ANATOMY OF SCENE HEADINGS (SLUGLINES)</h3>
            <p style="color:#f8fafc; font-size:15px; margin-top:6px;">
            A screenplay is not literature; it is an <b>engineering schematic</b> for 150 crew members (DOP, Gaffer, Art Director, Location Manager).
            The Slugline tells the team whether they are renting a studio or shooting in rain, and whether to bring daylight HMIs or night tungsten lights.
            </p>
            <hr style="border:0.5px solid #2d1d4f;">
            <h4>The 3 Invariant Laws of Sluglines:</h4>
            <ul>
                <li><b>Interior vs Exterior:</b> <code>INT.</code> means walls and roof; <code>EXT.</code> means open sky. For vehicles moving through streets, use <code>INT./EXT. CAR - CONTINUOUS</code>.</li>
                <li><b>Specific Specificity:</b> Never write <code>INT. HOUSE</code>. Write <code>INT. MAYA'S BEDROOM - WARDROBE CLOSET</code>. Camera needs exact geography.</li>
                <li><b>Temporal Lighting:</b> <code>DAY</code> and <code>NIGHT</code> are standard. Avoid 4:30 PM. Use <code>DUSK</code>, <code>DAWN</code>, <code>MAGIC HOUR</code> only if sunlight is narratively crucial.</li>
                <li><b>Flashback Tags:</b> Append <code>- FLASHBACK (1998)</code> at the end of the slugline so the production designer changes props.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 🧩 QUEST 1: The Production Location Rig")
        st.caption("Your Cinematographer is waiting. Formulate the precise slugline for a high-speed police chase inside a Chennai Metro train:")
        
        c_cam = st.selectbox("Camera Environment:", ["-- Select --", "INT.", "EXT.", "INT./EXT."], key="q1_cam")
        c_loc = st.text_input("Precise Geography (Specific Compartment & Line):", value="CHENNAI METRO - COACH 04 (BLUE LINE)", key="q1_loc")
        c_time = st.selectbox("Lighting Condition:", ["-- Select --", "NIGHT", "DAY", "DAWN", "CONTINUOUS"], key="q1_time")

        if st.button("LOCK SLUGLINE TO CALL SHEET (+40 XP) ➔", key="q1_btn"):
            if c_cam != "-- Select --" and c_time != "-- Select --":
                slug_res = f"{c_cam} {c_loc.upper().strip()} - {c_time}"
                st.success(f"🎯 CALL SHEET VALIDATED! Industry Slugline: `{slug_res}`")
                st.session_state["game_xp"] += 40
                st.balloons()
            else:
                st.error("Incomplete camera parameters! Select Environment and Time.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- LEVEL 2 ----------------
    with m2:
        st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
        st.markdown("""
        <div class="cyber-card cyber-card-alt">
            <h3 style="color:#ff0055; margin:0;">LEVEL 2 THEORY: THE "SHOW, DON'T TELL" CAMERA DISCIPLINE</h3>
            <p style="color:#f8fafc; font-size:15px; margin-top:6px;">
            <b>The Camera Eye Rule:</b> If a 35mm lens cannot photograph it, or an Arri directional mic cannot record it, it DOES NOT EXIST on a screenplay page.
            </p>
            <hr style="border:0.5px solid #2d1d4f;">
            <h4>Internal Thought vs Physical Foley Action:</h4>
            <ul>
                <li>❌ <b>Unfilmable Thought:</b> <i>"Rajesh is reminiscing about the guilt of stealing money from his sister 5 years ago."</i> (An actor cannot act '5 years ago' without a physical prop or gesture!)</li>
                <li>✅ <b>Cinematic Action:</b> <i>"Rajesh places a stack of rumpled hundred-rupee notes into his sister's open lunchbox. His knuckles graze a faded family photograph taped to the lid. He snatches his hand back."</i></li>
                <li><b>The 3-Sensory Rule:</b> Include visual gesture, acoustic foley (sound), and environmental weight (sweat, rain, ticking clocks).</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### ⚔️ QUEST 2: The Physicality Arena (AI Film-School Judge)")
        st.caption("Rewrite this amateur line into a pure 35mm visual action scene with Foley sound textures:")
        
        st.info("AMATEUR PASSAGE: 'Kathir is sitting in the dark room feeling betrayed and plotting revenge against his best friend who stole his business.'")
        user_a2 = st.text_area("Write the Physical Action Block (No Thoughts, Camera Only):", height=120, key="q2_in", placeholder="E.g. Kathir leans over a mahogany desk illuminated only by the flicker of a CRT monitor. A single ash drop falls from his beedi...")

        if st.button("SUBMIT TO AI FILM SCHOOL BOARD (+50 XP) ➔", key="q2_btn"):
            if not api_key:
                st.warning("API Key needed! Set in Secrets or Workspace.")
            elif not user_a2.strip():
                st.warning("Write your action description first!")
            else:
                with st.spinner("Screenplay Evaluator analyzing unfilmable words & foley dynamics..."):
                    judge_p = f"""
                    You are a legendary film school director evaluating a student's screenplay action description.
                    Challenge: Convert 'Kathir is sitting in the dark room feeling betrayed and plotting revenge against his best friend who stole his business' into PURE visual action, object interaction, and sound cues.
                    Student submission:
                    "{user_a2}"

                    Evaluate rigorously. Ban unfilmable thoughts. Return STRICT JSON:
                    {{
                        "score": 88,
                        "critique": "Crisp 2-sentence feedback analyzing physical props, camera framing viability, and micro-tension.",
                        "xp_awarded": 50
                    }}
                    """
                    raw_fb = call_cinematex_ai(api_key, judge_p, expect_json=True)
                    if raw_fb:
                        try:
                            clean_fb = json.loads(raw_fb.strip().replace("```json","").replace("```",""))
                            st.session_state["dojo_feedback"]["q2"] = clean_fb
                            st.session_state["game_xp"] += clean_fb.get("xp_awarded", 40)
                        except Exception as e:
                            st.error(f"Error parsing feedback: {e}")

        if "q2" in st.session_state["dojo_feedback"]:
            fb = st.session_state["dojo_feedback"]["q2"]
            st.markdown(f"""
            <div class="cyber-card">
                <h4 style="color:#00f0ff; margin:0;">AI JUDGE SCORE: {fb.get('score')}/100 ⚡ (+{fb.get('xp_awarded')} XP)</h4>
                <p style="color:#ffe600; margin-top:6px;"><b>Director Feedback:</b> {fb.get('critique')}</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- LEVEL 3 ----------------
    with m3:
        st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
        st.markdown("""
        <div class="cyber-card cyber-card-gold">
            <h3 style="color:#ffe600; margin:0;">LEVEL 3 THEORY: SUBTEXT, STATUS GAMES & REVERSE PSYCHOLOGY</h3>
            <p style="color:#f8fafc; font-size:15px; margin-top:6px;">
            In bad scripts, characters say what they mean. In masterpiece scripts, <b>characters use words as smoke grenades to hide their real objective.</b>
            </p>
            <hr style="border:0.5px solid #2d1d4f;">
            <h4>The 3 Pillars of Subtextual Dialogue:</h4>
            <ul>
                <li><b>Status Shifts:</b> In any 2-character dialogue, one holds the high ground (power/information) and the other holds low ground. Great scenes end with the status flipping upside down!</li>
                <li><b>The Third Object Rule:</b> Instead of talking about their love or hatred, characters talk about an ordinary object (a cup of tea, a watch, a pending bill). The emotion is transferred into the object.</li>
                <li><b>Rhythm of Omission:</b> What the character REFUSES to answer creates 10x more tension than what they say.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 🎭 QUEST 3: The Subtext Interrogation Duel")
        st.caption("Rewrite this blatant confession into an icy psychological status game:")
        st.error("BLUNT DIALOGUE: POLICE INSPECTOR: 'I have evidence that you poisoned the minister's food, so tell me where the money is.'")
        
        user_a3 = st.text_area("Rewrite using Misdirection, Pauses & Status Inversion:", height=120, key="q3_in", placeholder="Inspector sets down two glasses. Slides one forward. 'Sugar or honey, Doctor?'...")

        if st.button("EXECUTE SUBTEXT SURGERY (+50 XP) ➔", key="q3_btn"):
            if not api_key:
                st.warning("API Key needed!")
            elif not user_a3.strip():
                st.warning("Provide your subtext rewrite!")
            else:
                with st.spinner("Analyzing psychological leverage & verbal smoke..."):
                    sub_p = f"""
                    Analyze this screenplay subtext rewrite where an inspector corners a suspect without directly saying 'I know you did it'.
                    Student rewrite:
                    "{user_a3}"

                    Return STRICT JSON:
                    {{
                        "score": 92,
                        "critique": "Specific feedback on status games, weaponization of silence, and psychological power shifts.",
                        "xp_awarded": 50
                    }}
                    """
                    raw_sub = call_cinematex_ai(api_key, sub_p, expect_json=True)
                    if raw_sub:
                        try:
                            clean_sub = json.loads(raw_sub.strip().replace("```json","").replace("```",""))
                            st.session_state["dojo_feedback"]["q3"] = clean_sub
                            st.session_state["game_xp"] += clean_sub.get("xp_awarded", 45)
                        except Exception as e:
                            st.error(f"Error: {e}")

        if "q3" in st.session_state["dojo_feedback"]:
            fb3 = st.session_state["dojo_feedback"]["q3"]
            st.markdown(f"""
            <div class="cyber-card">
                <h4 style="color:#ffe600; margin:0;">SUBTEXT TENSION SCORE: {fb3.get('score')}/100 ⚡ (+{fb3.get('xp_awarded')} XP)</h4>
                <p style="color:#e2e8f0; margin-top:6px;">{fb3.get('critique')}</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- LEVEL 4 ----------------
    with m4:
        st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
        st.markdown("""
        <div class="cyber-card cyber-card-purple">
            <h3 style="color:#c084fc; margin:0;">LEVEL 4 THEORY: THE 3-ACT / 8-SEQUENCE NARRATIVE CLOCK</h3>
            <p style="color:#f8fafc; font-size:15px; margin-top:6px;">
            Why does an audience feel glued for 130 minutes without checking their watch? <b>Mathematical pacing of narrative reversals.</b>
            </p>
            <hr style="border:0.5px solid #2d1d4f;">
            <h4>The Universal Structural Clock:</h4>
            <ul>
                <li><b>Minute 0-10 (Ordinary World):</b> Baseline flaw established. What is the protagonist lacking?</li>
                <li><b>Minute 10-15 (Inciting Incident):</b> The meteor hits the planet. Peace is permanently broken.</li>
                <li><b>Minute 30 (Plot Point 1):</b> Protagonist crosses the threshold of no return. Can never go home.</li>
                <li><b>Minute 60 (Midpoint Reversal):</b> Stakes shift from reactive to proactive. A devastating truth is unveiled.</li>
                <li><b>Minute 85 (All is Lost / Dark Night):</b> Complete tactical defeat. The original plan is dead.</li>
                <li><b>Minute 100-115 (Climax Showdown):</b> Protagonist applies the psychological lesson to defeat the antagonist.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### ⏱️ QUEST 4: The 3-Beat Pacing Architect")
        st.caption("Map out the 3 critical turning points for this Cyberpunk Crime premise:")
        st.info("PREMISE: A retired neuro-surgeon in 2045 Neo-Madras discovers someone is stealing memories of street kids.")

        b_incite = st.text_input("1. The Inciting Incident (The trigger event that breaks his routine):", placeholder="E.g. A 10-year old tea-boy is brought in with an illegal cranial jack burnt into his skull...")
        b_mid = st.text_input("2. Midpoint Reversal (The massive shock that turns the tables):", placeholder="E.g. The doctor discovers the stolen neural data is being uploaded into his own daughter's comatose brain...")
        b_climax = st.text_input("3. Climax Reversal (The irreversible moral & physical resolution):", placeholder="E.g. He must wipe his own surgical muscle memory to overload the corrupt mainframe...")

        if st.button("LOCK ARCHITECTURAL BEATS (+60 XP) ➔", key="q4_btn"):
            if b_incite and b_mid and b_climax:
                st.session_state["game_xp"] += 60
                st.success(f"🔥 NARRATIVE ENGINE SYNCHRONIZED! +60 XP Awarded! Current XP: {st.session_state['game_xp']}")
                st.balloons()
            else:
                st.warning("Define all 3 narrative turning points!")
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- LEVEL 5 ----------------
    with m5:
        st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
        st.markdown("""
        <div class="cyber-card">
            <h3 style="color:#00f0ff; margin:0;">LEVEL 5 THEORY: ACTOR BLOCKING, PARENTHETICALS & CINEMATIC CUTS</h3>
            <p style="color:#f8fafc; font-size:15px; margin-top:6px;">
            A script is read by veteran actors and award-winning editors. Amateur mistakes in parentheticals and cut cues will get a script tossed into the trash!
            </p>
            <hr style="border:0.5px solid #2d1d4f;">
            <h4>Rules of Blocking & Pacing:</h4>
            <ul>
                <li><b>The Parenthetical Trap:</b> Do NOT use parentheticals to direct acting: <code>(angrily)</code> or <code>(sadly)</code>. Actors hate this. Use parentheticals ONLY for physical direction: <code>(into mirror)</code> or <code>(coughing blood)</code>.</li>
                <li><b>V.O. vs O.S.:</b> <code>(V.O.)</code> is Voice-Over recorded in a booth (narrator / internal voice). <code>(O.S.)</code> is Off-Screen (a character shouting from inside the bathroom while camera is in the hall).</li>
                <li><b>Pacing Transitions:</b> Use <code>SMASH CUT TO:</code> for sudden shocks, <code>MATCH CUT TO:</code> for thematic graphic continuity, and <code>INTERCUT:</code> for simultaneous parallel phone calls or heists.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 🎬 QUEST 5: The Master Scene Surgeon")
        st.caption("Choose the accurate technical tag for each directorial scenario:")
        
        q5_1 = st.selectbox("1. A character shouting instructions from inside a bank vault while camera watches police outside:", ["-- Select --", "VIKRAM (V.O.)", "VIKRAM (O.S.)", "VIKRAM (M.O.S.)"])
        q5_2 = st.selectbox("2. Switching violently from a romantic wedding laugh to a car crash explosion:", ["-- Select --", "DISSOLVE TO:", "SMASH CUT TO:", "FADE OUT."])
        q5_3 = st.selectbox("3. Showing both sides of an intense phone wiretap simultaneously without writing 20 sluglines:", ["-- Select --", "SPLIT SCREEN FOREVER", "INTERCUT PHONE CONVERSATION", "CUT TO CAR"])

        if st.button("SUBMIT TECHNICAL CALLS (+50 XP) ➔", key="q5_btn"):
            if "O.S." in q5_1 and "SMASH CUT" in q5_2 and "INTERCUT" in q5_3:
                st.session_state["game_xp"] += 50
                st.success("🎯 100% TECHNICAL ACCURACY! You think like a veteran Showrunner & Editor! (+50 XP)")
                st.balloons()
            else:
                st.error("Incorrect technical calls! Review the O.S., Smash Cut, and Intercut rules above.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- LEVEL 6 (FINAL BOSS) ----------------
    with m6:
        st.markdown("""
        <div class="cyber-card cyber-card-gold">
            <h3 style="color:#ffe600; margin:0;">LEVEL 6 CAPSTONE: THE LIVE TALKING DUEL WITH THE SHOWRUNNER</h3>
            <p style="color:#f8fafc; font-size:15px; margin-top:6px;">
            Here, you chat live with your AI Director Mentor. Propose an original 1-page scene idea, draft dialogues with subtext, and receive line-by-line script doctoring!
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="scroll-container" style="max-height: 380px;">', unsafe_allow_html=True)
        for msg in st.session_state["dialogue_duel_chat"]:
            if msg["role"] == "mentor":
                st.markdown(f"""
                <div class="cyber-card" style="border-left: 5px solid #a855f7;">
                    <b style="color:#c084fc;">🎬 SHOWRUNNER MENTOR:</b><br>
                    <span style="color:#f8fafc; font-size:15px;">{msg['text']}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="cyber-card cyber-card-gold" style="text-align:right;">
                    <b style="color:#ffe600;">YOU (SCRIPT DOCTOR):</b><br>
                    <span style="color:#f8fafc; font-size:15px;">{msg['text']}</span>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        col_c_in, col_c_btn = st.columns([4, 1])
        with col_c_in:
            user_msg = st.text_input(
                "Converse with your Showrunner Mentor / Pitch your scene line:",
                placeholder="E.g. Mentor, I want to write a scene where two brothers meet after 10 years at their father's funeral...",
                label_visibility="collapsed",
                key="capstone_chat_input"
            )
        with col_c_btn:
            send_btn = st.button("PITCH TO MENTOR ➔", use_container_width=True, key="capstone_send_btn")

        if send_btn and user_msg.strip():
            if not api_key:
                st.warning("Gemini API Key missing! Configure in Workspace or Secrets.")
            else:
                st.session_state["dialogue_duel_chat"].append({"role": "user", "text": user_msg})
                with st.spinner("Showrunner analyzing subtext, pacing, and camera viability..."):
                    chat_history = "\n".join([f"{m['role']}: {m['text']}" for m in st.session_state["dialogue_duel_chat"][-5:]])
                    capstone_prompt = f"""
                    You are a world-class Showrunner and Script Doctor with mastery in both Indian (Tamil/Pan-India) cinema and international Hollywood screenplay standards.
                    You are mentoring a student in an interactive, high-energy talking duel.
                    Language: Cool, razor-sharp Tanglish (mix of professional cinema English and natural Tamil).
                    Tasks:
                    1. Critique their scene structure, subtext, and 'Show, Don't Tell' camera dynamics.
                    2. Point out any lazy dialogue or unfilmable thoughts. Give a rewrite demonstration when necessary.
                    3. Award XP enthusiastically (e.g. '+35 XP!').
                    4. Challenge them with the next beat to keep the dialogue duel alive.

                    Recent Dialogue:
                    {chat_history}

                    Reply directly as Showrunner Mentor:
                    """
                    mentor_res = call_cinematex_ai(api_key, capstone_prompt, expect_json=False)
                    if mentor_res:
                        st.session_state["dialogue_duel_chat"].append({"role": "mentor", "text": mentor_res})
                        st.session_state["game_xp"] += 35
                        st.rerun()

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
            placeholder="Kadhai summary / rough passage inga paste pannunga. Engine adha Hollywood/Tamil cinema standard script-a mathidum..."
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
                    You are an elite cinema director, script doctor, and cinematographer specializing in Indian/Tamil cinema as well as global Hollywood standards.
                    Input text:
                    ---
                    {script_input}
                    ---
                    TASK REQUIREMENTS:
                    1. "formatted_script": Convert into flawless industry standard screenplay (SLUGLINES, visual action lines, centered UPPERCASE character names, parentheticals, sharp dialogue). Preserve core story essence and language flavor (Tamil/Tanglish/English).
                    2. "scene_beats": Deep breakdown with "scene_title", "emotional_tone", "tension_rating", "micro_beats", "director_vision".
                    3. "characters": "name", "role", "appearance", "quirks", "core_conflict".
                    4. "shot_list": "scene_no", "shot_type", "camera_angle", "lighting_setup", "sound_cue".
                    5. "storyboard_prompts": ULTRA-DETAILED prompts for Midjourney v6 / Flux with framing, lens, lighting, color grade, mood, --ar 16:9.

                    Return STRICT valid JSON only:
                    {{
                        "formatted_script": "string",
                        "scene_beats": [ {{"scene_title": "", "emotional_tone": "", "tension_rating": "", "micro_beats": "", "director_vision": ""}} ],
                        "characters": [ {{"name": "", "role": "", "appearance": "", "quirks": "", "core_conflict": ""}} ],
                        "shot_list": [ {{"scene_no": "", "shot_type": "", "camera_angle": "", "lighting_setup": "", "sound_cue": ""}} ],
                        "storyboard_prompts": [ "string" ]
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
                    else:
                        st.error("AI Neural engine connection timed out. Please retry.")

        p_data = st.session_state["active_project"].get("data")
        if p_data:
            with tab_script:
                st.caption("COURIER PRIME CINEMA STANDARD SCREENPLAY:")
                script_formatted = p_data.get("formatted_script", "Script not ready.")
                st.markdown(f'<div class="scroll-container"><div class="screenplay-box">{script_formatted}</div></div>', unsafe_allow_html=True)

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
                        <p style="color:#94a3b8; font-size:14px; margin:0;"><b>Director Subtext & Staging:</b> {b.get('director_vision', '')}</p>
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
                        <div style="margin-top:8px; font-size:14px;"><b style="color:#00f0ff;">Visual & Costumes:</b> {c.get('appearance', '')}</div>
                        <div style="margin-top:5px; font-size:14px;"><b style="color:#ffe600;">Mannerisms & Quirks:</b> {c.get('quirks', '')}</div>
                        <div style="margin-top:5px; font-size:14px;"><b style="color:#ff0055;">Internal Conflict:</b> {c.get('core_conflict', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with tab3:
                st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
                st.dataframe(p_data.get("shot_list", []), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with tab4:
                st.caption("ULTRA-DETAILED PROMPTS (MIDJOURNEY V6 / FLUX):")
                st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
                for i, p in enumerate(p_data.get("storyboard_prompts", []), 1):
                    st.markdown(f"**Shot {i} Production Frame:**")
                    st.code(p, language="text")
                st.markdown('</div>', unsafe_allow_html=True)

            with tab5:
                st.markdown("### 📄 DIRECT PDF PRODUCTION DOSSIER")
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
                    st.success("PDF exported and recorded into database!")

# =============================================================
# 5. SAVED VAULT (WITH LOAD & DELETE)
# =============================================================
elif st.session_state["current_view"] == "SAVED":
    if st.button("⬅️ BACK TO COMMAND NEXUS"):
        st.session_state["current_view"] = "HUB"
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
                    if st.button("🗑️", key=f"del_{item['id']}", use_container_width=True):
                        supabase.table("saved_scripts").delete().eq("id", item["id"]).execute()
                        st.rerun()
                st.divider()
    except Exception as e:
        st.error(f"Error: {e}")

# =============================================================
# 6. EXPORTED DOSSIERS (PDF VAULT)
# =============================================================
elif st.session_state["current_view"] == "EXPORTED":
    if st.button("⬅️ BACK TO COMMAND NEXUS"):
        st.session_state["current_view"] = "HUB"
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
