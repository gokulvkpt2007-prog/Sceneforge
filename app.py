import streamlit as st
from google import genai
from supabase import create_client, Client
import json
import time
from datetime import datetime
import pytz
from fpdf import FPDF

# -------------------------------------------------------------
# PAGE CONFIGURATION (LIGHTNING LOGO REVERTED)
# -------------------------------------------------------------
st.set_page_config(
    page_title="CINEMATEX // NEURAL CINEMA DECK",
    page_icon="⚡",
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

    .game-hud {
        background: rgba(10, 8, 20, 0.9);
        border: 1.5px solid #ffe600;
        border-radius: 10px;
        padding: 15px 20px;
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
if "game_xp" not in st.session_state:
    st.session_state["game_xp"] = 150
if "dojo_feedback" not in st.session_state:
    st.session_state["dojo_feedback"] = {}

def get_current_ist_time():
    tz = pytz.timezone('Asia/Kolkata')
    return datetime.now(tz).strftime("%d %b %Y • %I:%M:%S %p IST")

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
    st.markdown('<div style="text-align:center; color:#00f0ff; font-family:Orbitron;">NEURAL PRE-PRODUCTION & SCREENPLAY DOJO</div>', unsafe_allow_html=True)
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
    st.markdown(f"<div style='margin-top:12px; font-size:13px; color:#94a3b8;'>DIRECTOR: <b style='color:#00f0ff;'>{st.session_state['user'].email}</b> | XP: <b style='color:#ffe600;'>{st.session_state['game_xp']} XP</b></div>", unsafe_allow_html=True)
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
    st.markdown("<p style='text-align:center; color:#94a3b8;'>Select your pre-production trajectory or level-up in the Writing Dojo</p>", unsafe_allow_html=True)
    st.write("")

    col_h1, col_h2, col_h3, col_h4 = st.columns(4, gap="small")
    
    with col_h1:
        st.markdown("""
        <div class="funky-card">
            <h1 style="margin:0;">🚀</h1>
            <h4 style="color:#00f0ff; margin-top:8px;">QUANTUM FORGE</h4>
            <p style="color:#94a3b8; font-size:13px;">Convert rough passages into Courier scripts & breakdown matrices.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("ENTER WORKSPACE ➔", key="btn_new", use_container_width=True):
            st.session_state["active_project"] = {"title": "Untitled Sequence", "script": "", "data": None}
            st.session_state["current_view"] = "WORKSPACE"
            st.rerun()

    with col_h2:
        st.markdown("""
        <div class="funky-card" style="border-color:#a855f7; box-shadow:0 0 20px rgba(168, 85, 247, 0.25);">
            <h1 style="margin:0;">🎮</h1>
            <h4 style="color:#c084fc; margin-top:8px;">WRITING DOJO</h4>
            <p style="color:#94a3b8; font-size:13px;">Interactive RPG Quest! Practice scriptwriting, battle AI judge & earn XP.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("ENTER DOJO QUEST ➔", key="btn_dojo", use_container_width=True):
            st.session_state["current_view"] = "DOJO"
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
# 3. INTERACTIVE SCRIPTWRITING DOJO (GAMIFIED PRACTICE ARENA)
# =============================================================
elif st.session_state["current_view"] == "DOJO":
    col_dback, col_dhead = st.columns([1, 4])
    with col_dback:
        if st.button("⬅️ COMMAND NEXUS"):
            st.session_state["current_view"] = "HUB"
            st.rerun()
    with col_dhead:
        st.markdown("<h2 style='font-family:Orbitron; color:#c084fc; margin:0;'>🎮 CINEMATEX WRITING DOJO</h2>", unsafe_allow_html=True)
        st.caption("Interactive Screenwriting Quests // AI Battle Arena // Level Up Your Director Rank")

    st.write("")

    # Player HUD Bar
    st.markdown(f"""
    <div class="game-hud">
        <div>
            <span style="color:#94a3b8; font-size:12px;">DIRECTOR STATUS:</span><br>
            <b style="color:#00f0ff; font-family:Orbitron; font-size:18px;">LEVEL {1 + st.session_state['game_xp']//100} SCRIPT APPRENTICE</b>
        </div>
        <div>
            <span style="color:#94a3b8; font-size:12px;">TOTAL ACCUMULATED XP:</span><br>
            <b style="color:#ffe600; font-family:Orbitron; font-size:18px;">⚡ {st.session_state['game_xp']} XP</b>
        </div>
        <div>
            <span style="color:#94a3b8; font-size:12px;">CURRENT BADGE:</span><br>
            <b style="color:#ff007f; font-family:Orbitron; font-size:18px;">🎖️ VISUAL WEAPON</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    quest1, quest2, quest3, quest4 = st.tabs([
        "QUEST 1: SLUGLINE PUZZLE",
        "QUEST 2: SHOW DON'T TELL (AI ARENA)",
        "QUEST 3: SUBTEXT SURGERY",
        "QUEST 4: 60-SEC CLIMAX FORGE"
    ])

    api_key = st.secrets.get("GEMINI_API_KEY", "")

    # QUEST 1: SLUGLINE PUZZLE
    with quest1:
        st.markdown("### 🧩 Mission 1: Assemble the Industry Slugline")
        st.caption("A director arrives on set. Choose the correct pieces to formulate a standard camera heading.")
        
        c_env = st.selectbox("1. Camera Location Type:", ["-- Select --", "INT. (Interior)", "EXT. (Exterior)"])
        c_place = st.text_input("2. Specific Scene Location:", value="MADRAS HIGH COURT - STAIRCASE")
        c_time = st.selectbox("3. Production Lighting Time:", ["-- Select --", "NIGHT", "DAY", "DAWN", "CONTINUOUS"])

        if st.button("SUBMIT SLUGLINE TO AD ➔"):
            if c_env != "-- Select --" and c_time != "-- Select --":
                env_clean = "INT." if "INT" in c_env else "EXT."
                slug = f"{env_clean} {c_place.upper().strip()} - {c_time}"
                st.success(f"🎯 CORRECT BLUEPRINT! Formatted Slugline: `{slug}`")
                st.session_state["game_xp"] += 25
                st.balloons()
            else:
                st.error("Select both Camera Location Type and Time!")

    # QUEST 2: SHOW DON'T TELL (REAL-TIME AI BATTLE)
    with quest2:
        st.markdown("### ⚔️ Mission 2: The 'Show, Don't Tell' Battleground")
        st.caption("Amateurs write character thoughts; Masters write visual actions for the lens. Rewrite this amateur novel sentence:")
        
        st.markdown("""
        <div class="cyber-card cyber-card-alt">
            <h4 style="color:#ff0055; margin:0;">AMATEUR NOVEL LINE:</h4>
            <p style="font-size:16px; margin-top:6px; color:#f8fafc;"><i>"Vikram is feeling extremely terrified and guilty after hearing the police siren outside his apartment."</i></p>
        </div>
        """, unsafe_allow_html=True)

        user_action_input = st.text_area(
            "WRITE THE VISUAL ACTION BLOCK (CAMERA & FOLEY ONLY):",
            placeholder="E.g. Vikram freezes. His trembling hand drops the glass tumbler... Red-blue light pulses through the blinds...",
            height=130
        )

        if st.button("SUBMIT TO CINEMA JUDGE (AI REVIEW) ➔"):
            if not api_key:
                st.warning("Neural Engine API Key missing! Add key in Workspace panel or secrets.")
            elif not user_action_input.strip():
                st.warning("Write your action description first!")
            else:
                with st.spinner("Cinema Judge reviewing camera viability & visual score..."):
                    judge_prompt = f"""
                    You are a strict, world-class film school director judging a student's screenplay action description.
                    Challenge: Rewrite 'Vikram is feeling extremely terrified and guilty after hearing the police siren outside his apartment' using pure 'Show, Don't Tell' visual actions and foley sounds only (no unfilmable thoughts).
                    Student submission:
                    "{user_action_input}"

                    Evaluate and return STRICT JSON:
                    {{
                        "score": 85,
                        "badge": "CINEMATIC MASTER / PROMISING SHOT",
                        "verdict": "2-line razor sharp critique on camera movement, sensory details, and tension.",
                        "xp_awarded": 40
                    }}
                    """
                    try:
                        client = genai.Client(api_key=api_key)
                        res = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=judge_prompt,
                            config={'response_mime_type': 'application/json'}
                        )
                        data = json.loads(res.text.strip().replace("```json","").replace("```",""))
                        st.session_state["dojo_feedback"]["q2"] = data
                        st.session_state["game_xp"] += data.get("xp_awarded", 30)
                    except Exception as err:
                        st.error(f"Judging error: {err}")

        if "q2" in st.session_state["dojo_feedback"]:
            fb = st.session_state["dojo_feedback"]["q2"]
            st.markdown(f"""
            <div class="cyber-card">
                <h3 style="color:#00f0ff; margin:0;">AI JUDGE SCORE: {fb.get('score')}/100 ⚡ (+{fb.get('xp_awarded')} XP EARNED)</h3>
                <p style="color:#ffe600; margin-top:5px;"><b>Verdict:</b> {fb.get('verdict')}</p>
            </div>
            """, unsafe_allow_html=True)

    # QUEST 3: SUBTEXT SURGERY
    with quest3:
        st.markdown("### 🎭 Mission 3: The Subtext Surgery Room")
        st.caption("Direct dialogue is boring. True tension hides in what characters refuse to say out loud.")
        
        st.markdown("""
        <div class="cyber-card cyber-card-gold">
            <h4 style="color:#ffe600; margin:0;">THE BAD DIALOGUE:</h4>
            <p style="color:#f8fafc; margin-top:6px;"><b>POLICE OFFICER:</b> "I know you murdered your partner for the 10 crore diamond, and I will arrest you right now!"</p>
        </div>
        """, unsafe_allow_html=True)

        user_subtext = st.text_area(
            "REWRITE USING DEADLY SUBTEXT & BEHAVIORAL GESTURES:",
            placeholder="Officer slowly pulls out a chair, sits opposite... taps his pen on the desk...",
            height=130
        )

        if st.button("TEST SUBTEXT TENSION (AI EVALUATION) ➔"):
            if not api_key:
                st.warning("API Key needed!")
            elif not user_subtext.strip():
                st.warning("Provide your dialogue rewrite!")
            else:
                with st.spinner("Analyzing subtext and psychological intimidation..."):
                    subtext_prompt = f"""
                    Evaluate this screenplay subtext attempt where an officer questions a suspect without blatantly stating 'I know you killed him'.
                    Student attempt:
                    "{user_subtext}"

                    Return JSON:
                    {{
                        "score": 90,
                        "verdict": "Detailed feedback on silence, power dynamics, and double meanings.",
                        "xp_awarded": 50
                    }}
                    """
                    try:
                        client = genai.Client(api_key=api_key)
                        res = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=subtext_prompt,
                            config={'response_mime_type': 'application/json'}
                        )
                        fb_data = json.loads(res.text.strip().replace("```json","").replace("```",""))
                        st.session_state["dojo_feedback"]["q3"] = fb_data
                        st.session_state["game_xp"] += fb_data.get("xp_awarded", 35)
                    except Exception as err:
                        st.error(f"Evaluation error: {err}")

        if "q3" in st.session_state["dojo_feedback"]:
            fb = st.session_state["dojo_feedback"]["q3"]
            st.markdown(f"""
            <div class="cyber-card">
                <h3 style="color:#ffe600; margin:0;">TENSION RATING: {fb.get('score')}/100 ⚡ (+{fb.get('xp_awarded')} XP)</h3>
                <p style="color:#e2e8f0; margin-top:5px;">{fb.get('verdict')}</p>
            </div>
            """, unsafe_allow_html=True)

    # QUEST 4: 60-SEC CLIMAX FORGE
    with quest4:
        st.markdown("### ⏱️ Mission 4: The 60-Second Climax Beats Forge")
        st.caption("Every great scene ends with a reversal of power. Construct 3 micro-beats for this standoff:")
        
        st.info("SCENARIO: A sniper has 3 bullets left. His target is shielded behind bulletproof glass holding the detonator.")
        
        b1 = st.text_input("Micro-Beat 1 (The Immediate Physical Complication):", placeholder="E.g. The sniper's thermal scope battery flickers and dies...")
        b2 = st.text_input("Micro-Beat 2 (The Deceptive Tactic / Pivot):", placeholder="E.g. He aims at the overhead steel crane hook instead of the glass...")
        b3 = st.text_input("Micro-Beat 3 (The Irreversible Shock / Power Reversal):", placeholder="E.g. The 2-ton hook crushes the console seconds before trigger pull...")

        if st.button("LOCK CLIMAX BEATS & ASCEND RANK ➔"):
            if b1 and b2 and b3:
                st.session_state["game_xp"] += 60
                st.success(f"🔥 CLIMAX SEQUENCE LOCKED! You earned 60 XP! Total XP: {st.session_state['game_xp']}")
                st.balloons()
            else:
                st.warning("Fill all 3 micro-beats to complete the sequence!")

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
                    You are an elite cinema director, script doctor, and cinematographer with mastery over Indian/Tamil cinema and global Hollywood standards.
                    Input text:
                    ---
                    {script_input}
                    ---
                    TASK REQUIREMENTS:
                    1. "formatted_script": Convert into flawless industry standard screenplay (SLUGLINES, visual action lines, centered CHARACTER NAMES, parentheticals, sharp dialogue). Preserve core story essence and language flavor (Tamil/Tanglish/English).
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
                    try:
                        client = genai.Client(api_key=api_key)
                        res = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt,
                            config={'response_mime_type': 'application/json'}
                        )
                        if res and res.text:
                            clean_json = res.text.strip().replace("```json", "").replace("```", "")
                            parsed = json.loads(clean_json)
                            st.session_state["active_project"]["data"] = parsed
                            st.session_state["active_project"]["script"] = script_input
                            st.session_state["active_project"]["title"] = project_title
                            st.success("CINEMATEX FORGE SUCCESSFUL // ALL MATRICES SYNCHRONIZED")
                    except Exception as e:
                        st.error(f"Forge error: {e}")

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
                        <p style="margin-top:10px; color:#e2e8f0; font-size:15px;"><b>Micro-Beats & Progression:</b><br>{b.get('micro_beats', '')}</p>
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
                        <div style="margin-top:8px; font-size:14px;"><b style="color:#00f0ff;">Visual Texture & Costumes:</b> {c.get('appearance', '')}</div>
                        <div style="margin-top:5px; font-size:14px;"><b style="color:#ffe600;">Mannerisms & Quirks:</b> {c.get('quirks', '')}</div>
                        <div style="margin-top:5px; font-size:14px;"><b style="color:#ff0055;">Internal vs External Conflict:</b> {c.get('core_conflict', '')}</div>
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
                    st.success("PDF saved to database and exported!")

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
        items = res.data or []
        if not items:
            st.info("No exported PDFs found.")
        else:
            for item in items:
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
