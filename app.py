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

    /* Big Hero Learning Card */
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

    /* Sub Action Cards */
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
    st.session_state["game_xp"] = 100
if "dialogue_duel_chat" not in st.session_state:
    st.session_state["dialogue_duel_chat"] = [
        {"role": "mentor", "text": "Vanakkam Director! Script writing-na verum kadhai solradhu illa. Camera-ku oru visual sketch ezhudhuradhu. Naan ungaloda Screenplay Master. Start panlaama?"}
    ]

def get_current_ist_time():
    tz = pytz.timezone('Asia/Kolkata')
    return datetime.now(tz).strftime("%d %b %Y • %I:%M:%S %p IST")

# Robust Gemini API Caller with 2026 Recommended Model Pool
def call_cinematex_ai(api_key, prompt, expect_json=True):
    # Models ordered by availability: 3.6-flash is primary, fallback to 3.7-flash, 3.5-flash-lite
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
    st.markdown('<div style="text-align:center; color:#00f0ff; font-family:Orbitron;">NEURAL PRE-PRODUCTION DECK & SCRIPT DOJO</div>', unsafe_allow_html=True)
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
# 2. STUDIO COMMAND NEXUS (HUB: BIG HERO LEARN + 3 SUB-DOMAINS)
# =============================================================
if st.session_state["current_view"] == "HUB":
    st.write("")
    st.markdown("<h2 style='text-align:center; font-family:Orbitron; color:#ffe600;'>⚡ STUDIO COMMAND NEXUS</h2>", unsafe_allow_html=True)
    st.write("")

    # TOP BIG HERO: SCRIPT WRITING ACADEMY & INTERACTIVE GAME
    st.markdown("""
    <div class="hero-learn-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <span class="time-badge" style="color:#c084fc; border-color:#c084fc;">MASTER THE CINEMA CRAFT</span>
                <h2 style="font-family:Orbitron; color:#00f0ff; margin-top:8px; margin-bottom:4px;">🎓 SCRIPTWRITING MASTERCLASS & DOJO QUEST</h2>
                <p style="color:#e2e8f0; font-size:15px; margin:0;">Learn screenplay architecture from scratch — what makes a script filmable, then level up through real-time dialogue duels and RPG missions!</p>
            </div>
            <div style="font-size:3.5rem;">🎮</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("ENTER ACADEMY & WRITING DOJO ➔", use_container_width=True):
        st.session_state["current_view"] = "LEARN_DOJO"
        st.rerun()

    st.write("")
    st.markdown("<h4 style='font-family:Orbitron; color:#94a3b8;'>PRODUCTION ENGINES // 3 DOMAINS</h4>", unsafe_allow_html=True)

    # 3 LOWER SUB-DOMAINS (KUTTI CARDS)
    col_sub1, col_sub2, col_sub3 = st.columns(3, gap="medium")
    
    with col_sub1:
        st.markdown("""
        <div class="mini-card">
            <h2 style="margin:0;">🚀</h2>
            <h4 style="color:#00f0ff; margin-top:6px;">QUANTUM FORGE</h4>
            <p style="color:#94a3b8; font-size:12px;">Convert raw story passages into Courier screenplay & shot lists.</p>
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
# 3. SCRIPTWRITING MASTERCLASS + TALKING CHAT DUEL GAME
# =============================================================
elif st.session_state["current_view"] == "LEARN_DOJO":
    col_lback, col_lhead = st.columns([1, 4])
    with col_lback:
        if st.button("⬅️ COMMAND NEXUS"):
            st.session_state["current_view"] = "HUB"
            st.rerun()
    with col_lhead:
        st.markdown("<h2 style='font-family:Orbitron; color:#c084fc; margin:0;'>🎓 SCRIPT ACADEMY & INTERACTIVE DUEL</h2>", unsafe_allow_html=True)
        st.caption("First: Discover the foundation of screenplay. Second: Step into the Talking Quest with your AI Mentor!")

    st.write("")

    tab_learn, tab_game = st.tabs([
        "📖 STEP 1: SCRIPT WRITING-NA ENNA? (CORE LESSONS)",
        "⚔️ STEP 2: INTERACTIVE WRITING QUEST (TALKING DUEL GAME)"
    ])

    api_key = st.secrets.get("GEMINI_API_KEY", "")

    # STEP 1: THE FOUNDATION LESSONS
    with tab_learn:
        st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
        st.markdown("""
        <div class="cyber-card cyber-card-purple">
            <h3 style="color:#c084fc; margin:0;">💡 SCRIPT WRITING-NA UNMAIYILE ENNA?</h3>
            <p style="color:#f8fafc; font-size:15px; margin-top:6px;">
            Oru novel padikumbodhu manasula imagine pannuvom. Aana <b>Screenplay nguradhu oru building kattura blueprint maadhiri!</b><br>
            Camera lens enna paakudhu, mic enna kekkudhu, actors enna physical-ah panraanga ngra 3 vishayatha mattum dhaan script-la ezhudha mudiyum.
            </p>
        </div>
        """, unsafe_allow_html=True)

        col_less1, col_less2 = st.columns(2)
        with col_less1:
            st.markdown("""
            #### 1. Sluglines (Where & When)
            Camera enga set pannanum nu production crew-ku solradhu:
            * `INT.` (Interior - Kulla) / `EXT.` (Exterior - Veliya)
            * `LOCATION` (Eg: METRO TRAIN COACH 3)
            * `TIME` (NIGHT / DAY / DAWN)
            > **Rule:** `INT. METRO TRAIN COACH 3 - NIGHT`

            #### 2. Visual Action ("Show, Don't Tell")
            Manasula ninikuradha camera paaka mudiyadhu!
            * ❌ *Thappu:* "Vikram is sad about his father."
            * ✅ *Sari:* "Vikram stares at his father's dusty spectacles on the desk. He doesn't wipe the tear dripping down his jaw."
            """)
        with col_less2:
            st.markdown("""
            #### 3. Subtext in Dialogue
            Direct-ah solra dialogue boring! True drama hides in what people HIDE.
            * ❌ *Flat:* "I am angry that you cheated me in money."
            * ✅ *Subtext:* "Tea-ku innum bill kudukalayae bro? Namma partnership maadhiriye idhuvum free-ah?"

            #### 4. The 3-Act Tension Graph
            * **Act 1:** Character routine & Inciting Incident (Problem starts).
            * **Act 2:** Conflict rises, Midpoint shock, Darkest hour.
            * **Act 3:** High-stakes Climax showdown.
            """)
        st.markdown('</div>', unsafe_allow_html=True)

    # STEP 2: TALKING DUEL / CHAT QUEST WITH AI MENTOR
    with tab_game:
        st.markdown("""
        <div class="game-hud">
            <div>
                <span style="color:#94a3b8; font-size:12px;">DIRECTOR XP:</span><br>
                <b style="color:#ffe600; font-family:Orbitron; font-size:18px;">⚡ {xp} XP</b>
            </div>
            <div>
                <span style="color:#94a3b8; font-size:12px;">MISSION OBJECTIVE:</span><br>
                <b style="color:#00f0ff; font-family:Orbitron; font-size:16px;">CONVERSE & COMPLETE WRITING CHALLENGES</b>
            </div>
        </div>
        """.format(xp=st.session_state["game_xp"]), unsafe_allow_html=True)

        # Chat display container
        st.markdown('<div class="scroll-container" style="max-height: 380px;">', unsafe_allow_html=True)
        for msg in st.session_state["dialogue_duel_chat"]:
            if msg["role"] == "mentor":
                st.markdown(f"""
                <div class="cyber-card" style="border-left: 5px solid #a855f7;">
                    <b style="color:#c084fc;">🎬 DIRECTOR MENTOR:</b><br>
                    <span style="color:#f8fafc; font-size:15px;">{msg['text']}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="cyber-card cyber-card-gold" style="text-align:right;">
                    <b style="color:#ffe600;">YOU (SCREENWRITER):</b><br>
                    <span style="color:#f8fafc; font-size:15px;">{msg['text']}</span>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # User input box for talking game
        col_c_in, col_c_btn = st.columns([4, 1])
        with col_c_in:
            user_msg = st.text_input(
                "Reply to your Mentor / Submit your scene line:",
                placeholder="E.g. Mentor, na ready! Enaku oru police chase scene ku visual action challenge kudu...",
                label_visibility="collapsed"
            )
        with col_c_btn:
            send_btn = st.button("SEND TO MENTOR ➔", use_container_width=True)

        if send_btn and user_msg.strip():
            if not api_key:
                st.warning("Please configure Gemini API Key in Secrets or Workspace panel!")
            else:
                st.session_state["dialogue_duel_chat"].append({"role": "user", "text": user_msg})
                with st.spinner("Director Mentor evaluating and firing back..."):
                    chat_context = "\n".join([f"{m['role']}: {m['text']}" for m in st.session_state["dialogue_duel_chat"][-4:]])
                    mentor_prompt = f"""
                    You are a witty, world-class Tamil & Hollywood cinema director mentoring a student screenwriter in an interactive text-based RPG game.
                    Converse in cool, engaging Tanglish (Tamil + English mixture like Chennai film industry).
                    Rules:
                    1. If the student answers a screenplay challenge, review their visual description or subtext, give feedback, and award XP (e.g., '+30 XP!').
                    2. Give them exciting mini-challenges (e.g., 'Ipo oru tea shop-la silent-a murder plan panra 2 lines dialogue ezhudhu', 'Convert this feeling into pure visual action').
                    3. Keep it interactive, punchy, and super fun like talking to an experienced director friend.

                    Recent Conversation:
                    {chat_context}

                    Reply directly as Director Mentor:
                    """
                    reply = call_cinematex_ai(api_key, mentor_prompt, expect_json=False)
                    if reply:
                        st.session_state["dialogue_duel_chat"].append({"role": "mentor", "text": reply})
                        st.session_state["game_xp"] += 25
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
                    Input text (rough story passage or dialogues):
                    ---
                    {script_input}
                    ---
                    TASK REQUIREMENTS:
                    1. "formatted_script": Convert into flawless industry standard screenplay (SLUGLINES e.g. INT. / EXT. - LOCATION - TIME, descriptive visual action paragraphs, centered uppercase CHARACTER NAMES, parentheticals, sharp dialogue). Preserve core story essence and language flavor (Tamil/Tanglish/English).
                    2. "scene_beats": Deep breakdown with "scene_title", "emotional_tone", "tension_rating", "micro_beats", "director_vision".
                    3. "characters": "name", "role", "appearance", "quirks", "core_conflict".
                    4. "shot_list": "scene_no", "shot_type", "camera_angle", "lighting_setup", "sound_cue".
                    5. "storyboard_prompts": ULTRA-DETAILED prompts for Midjourney v6 / Flux with framing, lens, lighting, color grade, mood, --ar 16:9.

                    Return STRICT valid JSON only with this schema:
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
