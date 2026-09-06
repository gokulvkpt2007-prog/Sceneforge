import streamlit as st
from google import genai
from supabase import create_client, Client
import json
import time
from datetime import datetime
import pytz

# -------------------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------------------
st.set_page_config(
    page_title="SCENEFORGE // FUNKY CYBER STUDIO",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------------------
# FUNKY CYBER-RETRO GAMING HUD STYLING
# -------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bungee&family=Orbitron:wght@600;900&family=Rajdhani:wght@600;700&family=JetBrains+Mono:wght@500;700&display=swap');

    .stApp {
        background: radial-gradient(circle at 10% 10%, #150928 0%, #06050b 100%) !important;
        color: #f1f5f9;
        font-family: 'Rajdhani', sans-serif;
    }

    /* Funky Glowing Typography */
    .funky-title {
        font-family: 'Bungee', cursive;
        font-size: 2.7rem;
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

    /* Ambient Background Watermark Text */
    .faded-watermark {
        position: relative;
        text-align: center;
        font-family: 'Bungee', sans-serif;
        font-size: 2.8rem;
        color: rgba(0, 240, 255, 0.04);
        text-transform: uppercase;
        letter-spacing: 3px;
        user-select: none;
        pointer-events: none;
        margin-bottom: -40px;
        margin-top: 10px;
    }

    /* Funky Action Cards */
    .funky-card {
        background: rgba(22, 16, 42, 0.75);
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

    /* Input Buffers */
    .stTextInput input, .stTextArea textarea {
        background-color: #0d0818 !important;
        color: #00f0ff !important;
        border: 1.5px solid #2e1e52 !important;
        border-radius: 8px !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #ff007f !important;
        box-shadow: 0 0 15px rgba(255, 0, 127, 0.5) !important;
    }

    /* Funky Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #ff007f 0%, #7928ca 100%) !important;
        color: #ffffff !important;
        font-family: 'Orbitron', monospace !important;
        font-weight: 800 !important;
        border: 1px solid #ff007f !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        box-shadow: 0 0 18px rgba(255, 0, 127, 0.4) !important;
        transition: transform 0.15s ease !important;
    }
    div.stButton > button:hover {
        transform: scale(1.03) !important;
        box-shadow: 0 0 28px rgba(0, 240, 255, 0.7) !important;
    }

    /* Status Pill */
    .time-badge {
        font-family: 'JetBrains Mono', monospace;
        color: #ffe600;
        background: rgba(255, 230, 0, 0.1);
        border: 1px solid rgba(255, 230, 0, 0.3);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# SUPABASE SETUP (Insert credentials here)
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

# Session State Controller
if "user" not in st.session_state:
    st.session_state["user"] = None
if "current_view" not in st.session_state:
    st.session_state["current_view"] = "HUB"  # HUB, WORKSPACE, SAVED, EXPORTED
if "active_project" not in st.session_state:
    st.session_state["active_project"] = {"title": "New Sequence", "script": "", "data": None}

def get_current_ist_time():
    tz = pytz.timezone('Asia/Kolkata')
    return datetime.now(tz).strftime("%d %b %Y • %I:%M:%S %p IST")

# =============================================================
# 1. FUNKY LOGIN / REGISTER GATEWAY
# =============================================================
if st.session_state["user"] is None:
    st.write("")
    st.markdown('<div class="funky-title" style="text-align:center;">⚡ SCENEFORGE // FUNKY ACCESS</div>', unsafe_allow_html=True)
    st.markdown('<div class="funky-subtitle" style="text-align:center;">AUTHENTICATE TO UNLOCK THE CINEMA CYBER-DECK</div>', unsafe_allow_html=True)
    st.write("")

    col_l1, col_center, col_l2 = st.columns([1, 1.3, 1])
    with col_center:
        st.markdown('<div class="funky-card" style="text-align:left;">', unsafe_allow_html=True)
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
                        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                        st.session_state["user"] = res.user
                        st.session_state["current_view"] = "HUB"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Login failed: {e}")
        else:
            if st.button("✨ FORGE MY CREATOR ACCOUNT", use_container_width=True):
                if not email or not password:
                    st.error("Please provide valid credentials!")
                else:
                    try:
                        res = supabase.auth.sign_up({"email": email, "password": password})
                        st.success("Account successfully created! Switch to LOGIN tab and enter.")
                    except Exception as e:
                        st.error(f"Registration error: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# =============================================================
# TOP GLOBAL NAVIGATION
# =============================================================
col_nav1, col_nav2, col_nav3 = st.columns([2.5, 2, 1])
with col_nav1:
    st.markdown('<div class="funky-title" style="font-size:1.8rem;">⚡ SCENEFORGE</div>', unsafe_allow_html=True)
with col_nav2:
    st.markdown(f"<div style='margin-top:12px; font-size:13px; color:#94a3b8;'>CREATOR: <b style='color:#00f0ff;'>{st.session_state['user'].email}</b></div>", unsafe_allow_html=True)
with col_nav3:
    if st.button("🚪 LOGOUT", use_container_width=True):
        supabase.auth.sign_out()
        st.session_state["user"] = None
        st.session_state["current_view"] = "HUB"
        st.rerun()

# =============================================================
# 2. THE COMMAND NEXUS (THE 3-DOOR HUB)
# =============================================================
if st.session_state["current_view"] == "HUB":
    st.write("")
    st.markdown("<h2 style='text-align:center; font-family:Orbitron; color:#ffe600;'>⚡ STUDIO COMMAND NEXUS</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#94a3b8;'>Choose your pre-production trajectory below</p>", unsafe_allow_html=True)
    st.write("")

    col_h1, col_h2, col_h3 = st.columns(3, gap="medium")
    
    # CARD 1: CREATE NEW PROJECT
    with col_h1:
        st.markdown("""
        <div class="funky-card">
            <h1 style="margin:0;">🚀</h1>
            <h3 style="color:#00f0ff; margin-top:10px;">CREATE NEW PROJECT</h3>
            <p style="color:#94a3b8; font-size:14px;">Ingest raw screenplays in Tamil, Tanglish, or English to forge production assets.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("ENTER WORKSPACE ➔", key="btn_new", use_container_width=True):
            st.session_state["active_project"] = {"title": "Untitled Scene", "script": "", "data": None}
            st.session_state["current_view"] = "WORKSPACE"
            st.rerun()

    # CARD 2: SAVED PROJECTS
    with col_h2:
        st.markdown("""
        <div class="funky-card" style="border-color:#ffe600; box-shadow:0 0 20px rgba(255, 230, 0, 0.2);">
            <h1 style="margin:0;">📂</h1>
            <h3 style="color:#ffe600; margin-top:10px;">SAVED PROJECTS</h3>
            <p style="color:#94a3b8; font-size:14px;">Access screenplay versions preserved with exact timestamps and breakdowns.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("OPEN VAULT ➔", key="btn_saved", use_container_width=True):
            st.session_state["current_view"] = "SAVED"
            st.rerun()

    # CARD 3: EXPORTED PROJECTS
    with col_h3:
        st.markdown("""
        <div class="funky-card" style="border-color:#00f0ff; box-shadow:0 0 20px rgba(0, 240, 255, 0.2);">
            <h1 style="margin:0;">📦</h1>
            <h3 style="color:#00f0ff; margin-top:10px;">EXPORTED PROJECTS</h3>
            <p style="color:#94a3b8; font-size:14px;">Download and grab packaged production dossiers and shot sheets.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("ACCESS DOWNLOADS ➔", key="btn_exported", use_container_width=True):
            st.session_state["current_view"] = "EXPORTED"
            st.rerun()

# =============================================================
# 3. WORKSPACE (THE QUANTUM FORGE)
# =============================================================
elif st.session_state["current_view"] == "WORKSPACE":
    if st.button("⬅️ BACK TO COMMAND NEXUS"):
        st.session_state["current_view"] = "HUB"
        st.rerun()

    col_side, col_main = st.columns([1, 2.5], gap="medium")
    
    with col_side:
        st.markdown("### 🕹️ CONTROLS & KEYS")
        api_key = st.text_input("GEMINI API KEY", type="password", help="Enter free key from Google AI Studio")
        project_title = st.text_input("PROJECT TITLE", value=st.session_state["active_project"]["title"])
        
        script_input = st.text_area(
            "SCREENPLAY BUFFER (TAMIL / TANGLISH / ENGLISH):",
            value=st.session_state["active_project"]["script"],
            height=320,
            placeholder="Paste raw script here..."
        )
        
        forge_btn = st.button("⚡ EXECUTE FORGE", use_container_width=True)
        save_db_btn = st.button("💾 SAVE WITH EXACT TIMESTAMP", use_container_width=True)

        if save_db_btn:
            if not script_input.strip():
                st.warning("Cannot save empty script!")
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
                    st.success(f"Preserved at exact time: {ts}")
                except Exception as err:
                    st.error(f"Save error: {err}")

    with col_main:
        st.markdown("### 📊 PRODUCTION MATRIX")
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["⚡ SCENE BEATS", "👤 CHARACTER BIBLE", "🎥 SHOT LIST", "🎨 STORYBOARD CUES", "📦 EXPORT DOSSIER"])

        if forge_btn:
            if not api_key:
                st.error("Please enter your Gemini API Key in the left panel!")
            elif not script_input.strip():
                st.warning("Buffer empty!")
            else:
                with st.spinner("AI parsing script and forging production assets..."):
                    prompt = f"""
                    Analyze this screenplay (English, Tamil, or Tanglish):
                    ---
                    {script_input}
                    ---
                    Strictly return valid JSON:
                    1. "scene_beats": [ {{"scene_title": "", "emotional_tone": "", "tension": "", "description": ""}} ]
                    2. "characters": [ {{"name": "", "role": "", "appearance": "", "quirks": ""}} ]
                    3. "shot_list": [ {{"scene_no": "", "shot_type": "", "camera_angle": "", "sound_cue": ""}} ]
                    4. "storyboard_prompts": [ "string" ]
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
                        st.success("FORGE COMPLETE // ASSETS READY")

        p_data = st.session_state["active_project"].get("data")
        if p_data:
            with tab1:
                for b in p_data.get("scene_beats", []):
                    st.markdown(f"#### ⚡ {b.get('scene_title')} [{b.get('emotional_tone')}]")
                    st.write(b.get("description"))
                    st.divider()
            with tab2:
                for c in p_data.get("characters", []):
                    st.markdown(f"### 👤 {c.get('name')} • `{c.get('role')}`")
                    st.write(f"**Look:** {c.get('appearance')}")
                    st.write(f"**Mannerisms & Drive:** {c.get('quirks')}")
                    st.divider()
            with tab3:
                st.dataframe(p_data.get("shot_list", []), use_container_width=True)
            with tab4:
                for p in p_data.get("storyboard_prompts", []):
                    st.code(p)
            with tab5:
                st.markdown("### 📥 EXPORT FULL PRODUCTION DOSSIER")
                # Compile complete dossier string
                dossier = f"# PRODUCTION DOSSIER: {project_title}\nForged on: {get_current_ist_time()}\n\n"
                dossier += f"## 1. RAW SCREENPLAY\n{script_input}\n\n"
                dossier += f"## 2. PRODUCTION BREAKDOWN (JSON)\n{json.dumps(p_data, indent=2)}\n"

                if st.download_button(
                    label="⬇️ DOWNLOAD DOSSIER (.TXT)",
                    data=dossier,
                    file_name=f"{project_title.replace(' ', '_')}_Dossier.txt",
                    mime="text/plain",
                    use_container_width=True
                ):
                    # Flag as exported in database
                    ts = get_current_ist_time()
                    supabase.table("saved_scripts").insert({
                        "user_id": st.session_state["user"].id,
                        "title": project_title,
                        "script_content": script_input,
                        "parsed_data": p_data,
                        "saved_at_formatted": ts,
                        "is_exported": True
                    }).execute()
                    st.success("Packaged and logged into Exported Projects!")

# =============================================================
# 4. SAVED PROJECTS VAULT
# =============================================================
elif st.session_state["current_view"] == "SAVED":
    if st.button("⬅️ BACK TO COMMAND NEXUS"):
        st.session_state["current_view"] = "HUB"
        st.rerun()

    st.markdown("<h2 style='font-family:Orbitron; color:#ffe600;'>📂 SAVED PROJECTS VAULT</h2>", unsafe_allow_html=True)
    st.caption("Screenplays preserved with exact historical timestamps")
    
    try:
        res = supabase.table("saved_scripts").select("*").eq("user_id", st.session_state["user"].id).order("created_at", desc=True).execute()
        items = res.data or []
        if not items:
            st.info("No projects saved yet. Create one in the workspace!")
        else:
            for item in items:
                col_i1, col_i2 = st.columns([3, 1])
                with col_i1:
                    st.markdown(f"### 🎬 {item['title']}")
                    st.markdown(f"<span class='time-badge'>SAVED AT: {item.get('saved_at_formatted', 'N/A')}</span>", unsafe_allow_html=True)
                with col_i2:
                    if st.button(f"LOAD PROJECT", key=f"load_{item['id']}"):
                        st.session_state["active_project"] = {
                            "title": item["title"],
                            "script": item["script_content"],
                            "data": item["parsed_data"]
                        }
                        st.session_state["current_view"] = "WORKSPACE"
                        st.rerun()
                st.divider()
    except Exception as e:
        st.error(f"Error reading vault: {e}")

# =============================================================
# 5. EXPORTED PROJECTS (WITH FADED BACKGROUND TEXT)
# =============================================================
elif st.session_state["current_view"] == "EXPORTED":
    if st.button("⬅️ BACK TO COMMAND NEXUS"):
        st.session_state["current_view"] = "HUB"
        st.rerun()

    # The faded background watermark requested by you:
    st.markdown('<div class="faded-watermark">YOU CAN DOWNLOAD YOUR PROJECT FROM HERE</div>', unsafe_allow_html=True)
    
    st.markdown("<h2 style='font-family:Orbitron; color:#00f0ff; position:relative;'>📦 EXPORTED PRODUCTION DOSSIERS</h2>", unsafe_allow_html=True)
    st.caption("Grab ready-to-use production kits downloaded by your team")
    st.write("")

    try:
        res = supabase.table("saved_scripts").select("*").eq("user_id", st.session_state["user"].id).eq("is_exported", True).order("created_at", desc=True).execute()
        exported_items = res.data or []
        
        if not exported_items:
            st.info("No projects exported yet. Go to Workspace ➔ Export Dossier tab to generate one!")
        else:
            for item in exported_items:
                col_e1, col_e2 = st.columns([3, 1])
                with col_e1:
                    st.markdown(f"### 📄 {item['title']} - Production Kit")
                    st.markdown(f"<span class='time-badge'>EXPORT TIMESTAMP: {item.get('saved_at_formatted', 'N/A')}</span>", unsafe_allow_html=True)
                with col_e2:
                    # Re-compile export file
                    dossier = f"# PRODUCTION DOSSIER: {item['title']}\nExported: {item.get('saved_at_formatted')}\n\n## SCRIPT\n{item['script_content']}\n\n## PARSED DATA\n{json.dumps(item['parsed_data'], indent=2)}"
                    st.download_button(
                        label="⬇️ DOWNLOAD AGAIN",
                        data=dossier,
                        file_name=f"{item['title'].replace(' ', '_')}_Export.txt",
                        key=f"dl_{item['id']}",
                        use_container_width=True
                    )
                st.divider()
    except Exception as e:
        st.error(f"Error fetching exports: {e}")
