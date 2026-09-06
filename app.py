import streamlit as st
from google import genai
import json
import time

# -------------------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------------------
st.set_page_config(
    page_title="SCENEFORGE // PRODUCTION OS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# CYBERPUNK HUD STYLING
# -------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

    .stApp {
        background: radial-gradient(circle at 15% 15%, #0e1220 0%, #06080e 100%) !important;
        color: #e2e8f0;
        font-family: 'Rajdhani', sans-serif;
    }

    .stApp::before {
        content: " ";
        display: block;
        position: fixed;
        top: 0; left: 0; bottom: 0; right: 0;
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.02), rgba(0, 255, 0, 0.01), rgba(0, 255, 0, 0.02));
        z-index: 999;
        background-size: 100% 3px, 6px 100%;
        pointer-events: none;
        opacity: 0.5;
    }

    h1, h2, h3, h4, .cyber-font {
        font-family: 'Orbitron', monospace !important;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    .hero-glitch {
        font-family: 'Orbitron', monospace;
        font-size: 2.2rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00f0ff 0%, #ff0055 50%, #ffe600 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 25px rgba(0, 240, 255, 0.3);
    }

    .cyber-badge {
        display: inline-block;
        padding: 4px 10px;
        border: 1px solid #00f0ff;
        background: rgba(0, 240, 255, 0.08);
        color: #00f0ff;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 1px;
    }
    .cyber-badge-magenta {
        border-color: #ff0055;
        background: rgba(255, 0, 85, 0.1);
        color: #ff0055;
    }

    .auth-box {
        max-width: 460px;
        margin: 60px auto;
        padding: 30px;
        background: rgba(14, 18, 30, 0.85);
        border: 1px solid rgba(0, 240, 255, 0.3);
        border-radius: 12px;
        box-shadow: 0 0 30px rgba(0, 240, 255, 0.15);
        text-align: center;
    }

    .cyber-card {
        background: rgba(14, 18, 30, 0.75);
        border: 1px solid rgba(0, 240, 255, 0.18);
        border-left: 4px solid #00f0ff;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(10px);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 14px;
    }
    .cyber-card-alt {
        border-left: 4px solid #ff0055;
    }

    .stTextArea textarea {
        background-color: #090c14 !important;
        color: #00f0ff !important;
        border: 1px solid #1e293b !important;
        border-radius: 6px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 14px !important;
    }

    div.stButton > button:first-child {
        background: linear-gradient(135deg, #ff0055 0%, #7928ca 100%) !important;
        color: #ffffff !important;
        font-family: 'Orbitron', monospace !important;
        font-weight: 800 !important;
        letter-spacing: 1.5px !important;
        border: 1px solid #ff0055 !important;
        border-radius: 6px !important;
        padding: 10px 20px !important;
        box-shadow: 0 0 20px rgba(255, 0, 85, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# AUTHENTICATION STATE ENGINE
# -------------------------------------------------------------
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = ""

# -------------------------------------------------------------
# VIEW 1: GATEWAY LOGIN SCREEN
# -------------------------------------------------------------
if not st.session_state['authenticated']:
    st.markdown("""
        <div class="auth-box">
            <div class="hero-glitch" style="font-size:1.8rem; margin-bottom:10px;">⚡ SCENEFORGE</div>
            <div class="cyber-badge" style="margin-bottom:20px;">SECURITY CLEARANCE REQUIRED</div>
            <p style="color:#94a3b8; font-size:14px; margin-bottom:20px;">Access the neural pre-production engine with your credentials.</p>
        </div>
    """, unsafe_allow_html=True)

    auth_col1, auth_col2, auth_col3 = st.columns([1, 1.2, 1])
    with auth_col2:
        email_in = st.text_input("Gmail / User Identifier", placeholder="creator@gmail.com")
        pass_in = st.text_input("Security Passcode", type="password", placeholder="••••••••")
        
        login_btn = st.button("AUTHENTICATE & ENTER DECK", use_container_width=True)
        if login_btn:
            if email_in and pass_in:
                st.session_state['authenticated'] = True
                st.session_state['user_email'] = email_in
                st.rerun()
            else:
                st.error("ACCESS DENIED: Enter valid Gmail ID and Passcode.")
    st.stop()

# -------------------------------------------------------------
# VIEW 2: AUTHENTICATED STUDIO WORKSPACE
# -------------------------------------------------------------
col_h1, col_h2 = st.columns([2.5, 1])
with col_h1:
    st.markdown('<div class="hero-glitch">⚡ SCENEFORGE // PRODUCTION OS</div>', unsafe_allow_html=True)
    st.markdown(f"""
        <span class="cyber-badge">OPERATOR: {st.session_state['user_email']}</span>
        <span class="cyber-badge cyber-badge-magenta" style="margin-left:6px;">TERMINAL ONLINE</span>
    """, unsafe_allow_html=True)

with col_h2:
    if st.button("LOGOUT / LOCK DECK"):
        st.session_state['authenticated'] = False
        st.session_state['user_email'] = ""
        st.rerun()

st.divider()

# SIDEBAR CONTROLS
with st.sidebar:
    st.markdown("### 🕹️ TERMINAL CONTROLS")
    api_key = st.text_input("GEMINI API KEY", type="password", help="Enter free key from Google AI Studio")
    st.markdown("""
        <div style="font-size:12px; color:#64748b; font-family:'JetBrains Mono';">
            Free Key: <a href="https://aistudio.google.com" target="_blank" style="color:#00f0ff; text-decoration:none;">aistudio.google.com ↗</a>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.markdown("### 📂 RETRIEVE SAVED PROJECT")
    uploaded_file = st.file_uploader("Upload SceneForge JSON File", type=["json"])
    if uploaded_file is not None:
        try:
            saved_data = json.load(uploaded_file)
            st.session_state['data'] = saved_data
            st.success("PROJECT RETRIEVED!")
        except Exception as err:
            st.error(f"Invalid file: {err}")

# WORKSPACE GRID
col_in, col_out = st.columns([1.1, 1.3], gap="large")

with col_in:
    st.markdown("### 📥 SCRIPT BUFFER")
    if st.button("Load Cyber-Crime Sample Script"):
        st.session_state['demo_script'] = (
            "SCENE 1: ROYAPETTAH UNDERPASS - NIGHT\n"
            "Monsoon rain pours down. Neon sign reflects on wet asphalt. "
            "VIKRAM (30s, faded denim jacket, bruised knuckles) stares at his ticking smartwatch.\n\n"
            "VIKRAM\n"
            "(whispering into burner earpiece)\n"
            "Dei Shiva, delivery spot reach aayiten. Vault encryption unlock aacha illaya?\n\n"
            "SHIVA (V.O)\n"
            "Vikram, sensor trigger aayiduchu! Black Scorpio is entering the tunnel right behind you!\n\n"
            "Sound: Sudden tire screech cuts through rain."
        )

    script_input = st.text_area(
        "PASTE SCREENPLAY (Tamil / Tanglish / English):",
        value=st.session_state.get('demo_script', ''),
        height=350,
        placeholder="Drop raw script here..."
    )

    analyze_btn = st.button("⚡ EXECUTE NEURAL FORGE", use_container_width=True)

with col_out:
    st.markdown("### 📊 PRODUCTION ASSETS")
    tab1, tab2, tab3, tab4 = st.tabs(["⚡ SCENE BEATS", "👤 CHARACTER BIBLE", "🎥 SHOT LIST", "🎨 STORYBOARD CUES"])

    if analyze_btn:
        if not api_key:
            st.error("KEY REQUIRED: Paste your Gemini API Key in the left sidebar!")
        elif not script_input.strip():
            st.warning("BUFFER EMPTY: Provide script text first.")
        else:
            with st.spinner("QUANTUM FORGE ACTIVE: Synthesizing production breakdown..."):
                prompt = f"""
                You are an expert film pre-production assistant.
                Analyze this story or screenplay (English, Tamil, or Tanglish):
                ---
                {script_input}
                ---
                Strictly return a valid JSON object with these 4 keys:
                1. "scene_beats": List of objects with:
                   - "scene_title"
                   - "emotional_tone"
                   - "tension_rating"
                   - "description"
                2. "characters": List of objects with:
                   - "name"
                   - "role"
                   - "appearance"
                   - "quirks"
                3. "shot_list": List of objects with:
                   - "scene_no"
                   - "shot_type"
                   - "camera_angle"
                   - "sound_cue"
                4. "storyboard_prompts": List of detailed Midjourney/Flux visual strings.
                Output ONLY raw, valid JSON.
                """

                client = genai.Client(api_key=api_key)
                models_to_try = [
                    'gemini-3.5-flash-lite',
                    'gemini-3.7-flash',
                    'gemini-3.6-flash',
                    'gemini-3.5-flash'
                ]

                response = None
                last_error = None

                for model_name in models_to_try:
                    for attempt in range(2):
                        try:
                            res = client.models.generate_content(
                                model=model_name,
                                contents=prompt,
                                config={'response_mime_type': 'application/json'}
                            )
                            if res and res.text:
                                response = res
                                break
                        except Exception as e:
                            last_error = e
                            time.sleep(2)
                    if response:
                        break

                if response and response.text:
                    try:
                        clean_text = response.text.strip()
                        if clean_text.startswith("```json"):
                            clean_text = clean_text[7:]
                        if clean_text.endswith("```"):
                            clean_text = clean_text[:-3]
                        data = json.loads(clean_text)
                        st.session_state['data'] = data
                        st.success("FORGE COMPLETE // DATA READY")
                    except Exception as parse_err:
                        st.error(f"JSON Error: {parse_err}")
                else:
                    st.error(f"Execution Error: {last_error}")

    # RENDER DATA & SAVE BUTTON
    if 'data' in st.session_state:
        d = st.session_state['data']

        # SAVE/EXPORT PROJECT FILE
        json_string = json.dumps(d, indent=4)
        st.download_button(
            label="💾 SAVE & EXPORT PROJECT FILE (.JSON)",
            file_name="sceneforge_production_assets.json",
            mime="application/json",
            data=json_string,
            use_container_width=True
        )

        with tab1:
            for s in d.get("scene_beats", []):
                st.markdown(f"""
                <div class="cyber-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="color:#00f0ff; margin:0;">{s.get('scene_title', 'SCENE')}</h4>
                        <span class="cyber-badge">{s.get('emotional_tone', 'TENSE')} | {s.get('tension_rating', '80%')}</span>
                    </div>
                    <p style="margin-top:8px; color:#cbd5e1;">{s.get('description', '')}</p>
                </div>
                """, unsafe_allow_html=True)

        with tab2:
            for c in d.get("characters", []):
                st.markdown(f"""
                <div class="cyber-card cyber-card-alt">
                    <h3 style="color:#ff0055; margin:0;">👤 {c.get('name', 'UNKNOWN')}</h3>
                    <div style="font-size:14px; color:#94a3b8; margin-top:6px;">ROLE: <b style="color:#f8fafc;">{c.get('role', 'N/A')}</b></div>
                    <div style="font-size:14px; color:#94a3b8; margin-top:4px;">LOOK: <span style="color:#e2e8f0;">{c.get('appearance', '')}</span></div>
                    <div style="font-size:14px; color:#94a3b8; margin-top:4px;">DRIVE: <span style="color:#e2e8f0;">{c.get('quirks', '')}</span></div>
                </div>
                """, unsafe_allow_html=True)

        with tab3:
            st.markdown('<div class="cyber-card">', unsafe_allow_html=True)
            st.dataframe(d.get("shot_list", []), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with tab4:
            for p in d.get("storyboard_prompts", []):
                st.code(p, language="text")
