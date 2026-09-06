
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
# PAGE CONFIGURATION
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
        padding: 24px;
        text-align: center;
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
SUPABASE_URL = "https://xiicgxqmmrvvvgdvkbej.supabase.co"
SUPABASE_KEY = "sb_publishable_l3TcwbLc7Dm9X-Ji-7bJdw_M0ey36-8"

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
    # Safe ASCII sanitization to prevent unicode exceptions
    return str(text).encode('ascii', 'ignore').decode('ascii')

def generate_dossier_pdf(title, raw_text, p_data, timestamp):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    pdf.add_page()
    
    # Effective printable width
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
    st.markdown('<div class="funky-title" style="text-align:center;"> ⚡CINEMATEX </div>', unsafe_allow_html=True)
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
# 2. STUDIO COMMAND NEXUS (HUB)
# =============================================================
if st.session_state["current_view"] == "HUB":
    st.write("")
    st.markdown("<h2 style='text-align:center; font-family:Orbitron; color:#ffe600;'>⚡ STUDIO COMMAND NEXUS</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#94a3b8;'>Select your pre-production trajectory below</p>", unsafe_allow_html=True)
    st.write("")

    col_h1, col_h2, col_h3 = st.columns(3, gap="medium")
    with col_h1:
        st.markdown("""
        <div class="funky-card">
            <h1 style="margin:0;">🚀</h1>
            <h3 style="color:#00f0ff; margin-top:10px;">CREATE NEW PROJECT</h3>
            <p style="color:#94a3b8; font-size:14px;">Ingest raw story passages, casual narrations, or dialogues in Tamil, Tanglish, or English.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("ENTER WORKSPACE ➔", key="btn_new", use_container_width=True):
            st.session_state["active_project"] = {"title": "Untitled Sequence", "script": "", "data": None}
            st.session_state["current_view"] = "WORKSPACE"
            st.rerun()

    with col_h2:
        st.markdown("""
        <div class="funky-card" style="border-color:#ffe600; box-shadow:0 0 20px rgba(255, 230, 0, 0.2);">
            <h1 style="margin:0;">📂</h1>
            <h3 style="color:#ffe600; margin-top:10px;">SAVED VAULT</h3>
            <p style="color:#94a3b8; font-size:14px;">Screenplays and breakdown matrix preserved with accurate timestamps.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("OPEN VAULT ➔", key="btn_saved", use_container_width=True):
            st.session_state["current_view"] = "SAVED"
            st.rerun()

    with col_h3:
        st.markdown("""
        <div class="funky-card" style="border-color:#00f0ff; box-shadow:0 0 20px rgba(0, 240, 255, 0.2);">
            <h1 style="margin:0;">📦</h1>
            <h3 style="color:#00f0ff; margin-top:10px;">EXPORTED DOSSIERS</h3>
            <p style="color:#94a3b8; font-size:14px;">Download packaged cinema production kits directly as PDF documents.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("ACCESS PDFS ➔", key="btn_exported", use_container_width=True):
            st.session_state["current_view"] = "EXPORTED"
            st.rerun()

# =============================================================
# 3. WORKSPACE (QUANTUM FORGE)
# =============================================================
elif st.session_state["current_view"] == "WORKSPACE":
    if st.button("⬅️ BACK TO COMMAND NEXUS"):
        st.session_state["current_view"] = "HUB"
        st.rerun()

    col_side, col_main = st.columns([1, 2.5], gap="medium")
    
    with col_side:
        st.markdown("### 🕹️ CONTROLS & ENGINE")
        
        # Background Key Integration
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

            # TAB 4: STORYBOARD PROMPTS (MIDJOURNEY/FLUX)
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
# 4. SAVED VAULT
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
# 5. EXPORTED DOSSIERS (PDF VAULT)
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
