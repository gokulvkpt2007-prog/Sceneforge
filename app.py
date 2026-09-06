import streamlit as st
from google import genai
import json

st.set_page_config(
    page_title="SCENEFORGE // AI ENGINE",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎮 CYBER-CINEMATIC GAMING HUD STYLING
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600;700&display=swap');

    .stApp {
        background: radial-gradient(circle at 10% 20%, #0d0f18 0%, #050608 90%) !important;
        color: #e2e8f0;
        font-family: 'Rajdhani', sans-serif;
    }
    
    h1, h2, h3, .hud-title {
        font-family: 'Orbitron', monospace !important;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    .hero-glow {
        background: linear-gradient(90deg, #00f0ff 0%, #ff0055 50%, #ffe600 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.4rem;
        font-weight: 900;
        text-shadow: 0 0 20px rgba(0, 240, 255, 0.2);
    }

    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border: 1px solid #00f0ff;
        background: rgba(0, 240, 255, 0.08);
        color: #00f0ff;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 1px;
    }

    .hud-card {
        background: rgba(18, 22, 36, 0.7);
        border: 1px solid rgba(0, 240, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(8px);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 14px;
        transition: all 0.2s ease-in-out;
    }
    .hud-card:hover {
        border-color: #00f0ff;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.3);
    }

    .stTextArea textarea {
        background-color: #0c0e17 !important;
        color: #00f0ff !important;
        border: 1px solid #2a314d !important;
        border-radius: 6px !important;
        font-family: 'Rajdhani', monospace !important;
        font-size: 15px !important;
    }
    .stTextArea textarea:focus {
        border-color: #00f0ff !important;
        box-shadow: 0 0 10px rgba(0, 240, 255, 0.4) !important;
    }

    div.stButton > button:first-child {
        background: linear-gradient(135deg, #ff0055 0%, #7928ca 100%) !important;
        color: #ffffff !important;
        font-family: 'Orbitron', monospace !important;
        font-weight: 700 !important;
        letter-spacing: 1px !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 12px 24px !important;
        box-shadow: 0 0 20px rgba(255, 0, 85, 0.4) !important;
        transition: transform 0.1s ease !important;
    }
    div.stButton > button:first-child:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 0 25px rgba(255, 0, 85, 0.7) !important;
    }

    /* Tabs Gaming Styling */
    button[data-baseweb="tab"] {
        font-family: 'Orbitron', monospace !important;
        color: #94a3b8 !important;
        font-size: 13px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #00f0ff !important;
        border-bottom-color: #00f0ff !important;
    }
</style>
""", unsafe_allow_html=True)

# TOP HUD HEADER
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<div class="hero-glow">⚡ SCENEFORGE // PRE-PRO HUD</div>', unsafe_allow_html=True)
    st.markdown('<span class="status-badge">PROTOCOL ONLINE</span> <span style="color:#64748b; font-size:13px; margin-left:8px;">TAMIL • TANGLISH • ENGLISH SCRIPTS AUTO-PARSER</span>', unsafe_allow_html=True)
with col_h2:
    st.caption("CORE ENGINE: MULTI-TIER FALLBACK (ACTIVE)")

st.write("")

# SIDEBAR TERMINAL
with st.sidebar:
    st.markdown("### 🕹️ TERMINAL ACCESS")
    api_key = st.text_input("GEMINI API KEY", type="password", help="Enter key from AI Studio")
    st.markdown("""
    <div style="font-size:12px; color:#64748b; margin-top:5px;">
        Key illana: <a href="https://aistudio.google.com" target="_blank" style="color:#00f0ff;">aistudio.google.com</a> la eduthuko machi.
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.markdown("### 📡 ENGINE TELEMETRY")
    st.markdown("• Auto-Detect: **Tamil / Tanglish**")
    st.markdown("• Architecture: **Multi-Model Queue**")
    st.markdown("• Output Matrix: **4-Way Breakdown**")

# MAIN WORKSPACE
col_in, col_out = st.columns([1.1, 1.3], gap="large")

with col_in:
    st.markdown("### 📥 SCRIPT INGESTION TERMINAL")
    sample_btn = st.button("Load Cyberpunk Sample Scene", help="Click to load instant demo script")
    default_text = ""
    if sample_btn:
        default_text = "SCENE 1: KODAMBAKKAM STREET - NIGHT\nRain pours down. Neon blue light reflects on wet asphalt. ARJUN (28, worn leather jacket, cybernetic prosthetic arm) stands watching a tea stall.\n\nARJUN\n(phone la pesuran)\nMachi, delivery spot vandhutten. Tracking chip status enna?\n\nKAVYA (V.O)\nSignal drop aagudhu Arjun! Left lane la irundhu black car varudhu, move now!\n\nSound: Heavy tire screech cuts through rain."

    script_text = st.text_area(
        "PASTE SCREENPLAY / RAW STORY:",
        value=default_text,
        height=400,
        placeholder="Drop raw scripts in Tamil, Tanglish or English here..."
    )
    
    analyze_btn = st.button("⚡ EXECUTE NEURAL PARSING", use_container_width=True)

with col_out:
    st.markdown("### 📊 PRODUCTION MATRIX")
    tab1, tab2, tab3, tab4 = st.tabs(["⚡ SCENE BEATS", "👤 CHARACTER BIBLE", "🎥 CAMERA SHOT LIST", "🎨 STORYBOARD CUES"])

    if analyze_btn:
        if not api_key:
            st.error("SYSTEM HALTED: Enter your Gemini API Key in the left terminal!")
        elif not script_text.strip():
            st.warning("WARNING: Script buffer is empty. Ingest text first.")
        else:
            with st.spinner("PROCESSING SCRIPT THROUGH NEURAL MATRIX..."):
                prompt = f"""
                You are a master film pre-production assistant specialized in Tamil cinema and international filmmaking.
                Analyze this screenplay/story (written in English, Tamil, or Tanglish):
                ---
                {script_text}
                ---
                Extract structured data and return STRICT JSON with these exact keys:
                1. "scene_beats": List of objects with:
                   - "scene_title": Short title
                   - "emotional_tone": e.g., Tense, High-Octane, Melancholic
                   - "tension_level": e.g., 85%
                   - "description": Key narrative beats and progression
                2. "characters": List of objects with:
                   - "name": Character name
                   - "role": Protagonist, Antagonist, etc.
                   - "appearance": Physical description, costume colors, key accessories
                   - "quirks": Body language, tone of voice, psychological drive
                3. "shot_list": List of objects with:
                   - "scene_no": Scene #
                   - "shot_type": e.g., Extreme Close Up, Tracking Wide, Dutch Angle
                   - "camera_angle": Eye level, Low Angle, Crane
                   - "sound_cue": Sound design, Foley, BGM tone
                4. "storyboard_prompts": List of visual image generation prompts for key scenes (Midjourney/Flux style).

                Output ONLY valid JSON.
                """

                client = genai.Client(api_key=api_key)
                # Failover sequence: 3.5-flash-lite (fast) -> 3.8-flash -> 3.6-flash
                models_to_try = ['gemini-3.5-flash-lite', 'gemini-3.8-flash', 'gemini-3.6-flash']
                response = None
                last_error = None

                for m in models_to_try:
                    try:
                        response = client.models.generate_content(
                            model=m,
                            contents=prompt,
                            config={'response_mime_type': 'application/json'}
                        )
                        if response and response.text:
                            break
                    except Exception as e:
                        last_error = e
                        continue

                if response and response.text:
                    try:
                        data = json.loads(response.text)
                        st.session_state['data'] = data
                        st.success("PARSING COMPLETE // MATRIX SYNCHRONIZED")
                    except Exception as parse_err:
                        st.error(f"JSON Parsing Error: {parse_err}")
                else:
                    st.error(f"Execution Error: {last_error}")

    if 'data' in st.session_state:
        d = st.session_state['data']
        
        with tab1:
            for s in d.get("scene_beats", []):
                st.markdown(f"""
                <div class="hud-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="color:#00f0ff; margin:0;">{s.get('scene_title', 'SCENE')}</h4>
                        <span class="status-badge">{s.get('emotional_tone', 'TENSE')}</span>
                    </div>
                    <p style="margin-top:8px; color:#cbd5e1;">{s.get('description', '')}</p>
                </div>
                """, unsafe_allow_html=True)

        with tab2:
            for c in d.get("characters", []):
                st.markdown(f"""
                <div class="hud-card" style="border-left: 4px solid #ff0055;">
                    <h3 style="color:#ff0055; margin-bottom:4px;">👤 {c.get('name', 'UNKNOWN')}</h3>
                    <div style="font-size:14px; color:#94a3b8; margin-bottom:6px;">ROLE: <b style="color:#f8fafc;">{c.get('role', 'N/A')}</b></div>
                    <div style="font-size:14px; color:#94a3b8;">LOOK & COSTUME: <span style="color:#e2e8f0;">{c.get('appearance', '')}</span></div>
                    <div style="font-size:14px; color:#94a3b8; margin-top:4px;">TRAITS / DRIVE: <span style="color:#e2e8f0;">{c.get('quirks', '')}</span></div>
                </div>
                """, unsafe_allow_html=True)

        with tab3:
            st.markdown('<div class="hud-card">', unsafe_allow_html=True)
            st.dataframe(d.get("shot_list", []), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with tab4:
            st.caption("READY-TO-USE VISUAL PROMPTS FOR MIDJOURNEY / FLUX:")
            for p in d.get("storyboard_prompts", []):
                st.code(p, language="text")
