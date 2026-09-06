import streamlit as st
from google import genai
import json

st.set_page_config(page_title="SceneForge - AI Pre-Production", layout="wide", page_icon="🎬")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stTextArea textarea { background-color: #1a1c24; color: #fff; }
</style>
""", unsafe_allow_html=True)

st.title("🎬 SceneForge: AI Pre-Production Engine")
st.caption("Forging Raw Tamil, Tanglish & English Scripts into Production-Ready Assets")

with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.markdown("[Get Free Gemini API Key](https://aistudio.google.com)")

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("📝 Screenplay Input")
    script_text = st.text_area("Paste your story / screenplay here (Tamil / Tanglish / English):", height=420)
    analyze_btn = st.button("🚀 Forge Production Assets", use_container_width=True, type="primary")

with col2:
    st.subheader("📦 Production Breakdown")
    tab1, tab2, tab3, tab4 = st.tabs(["⚡ Scene Beats", "🎭 Character Bible", "🎥 Shot List", "🎨 Storyboard Prompts"])

    if analyze_btn:
        if not api_key:
            st.error("Please enter your Gemini API Key in the left sidebar!")
        elif not script_text.strip():
            st.warning("Please paste a script first!")
        else:
            with st.spinner("Forging production assets from screenplay..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = f"""
                    You are an expert film pre-production assistant.
                    Analyze this screenplay/story (English, Tamil, or Tanglish):
                    ---
                    {script_text}
                    ---
                    Return a JSON object with these exact keys:
                    1. "scene_beats": List of objects with "scene_title", "emotional_tone", "description".
                    2. "characters": List of objects with "name", "role", "appearance", "quirks".
                    3. "shot_list": List of objects with "scene_no", "shot_type", "camera_angle", "sound_cue".
                    4. "storyboard_prompts": List of visual prompts for key scenes.
                    Output ONLY raw valid JSON.
                    """
                    response = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=prompt,
                        config={'response_mime_type': 'application/json'}
                    )
                    data = json.loads(response.text)
                    st.session_state['data'] = data
                except Exception as e:
                    st.error(f"Error: {e}")

    if 'data' in st.session_state:
        d = st.session_state['data']
        with tab1:
            for s in d.get("scene_beats", []):
                st.markdown(f"### {s.get('scene_title', 'Scene')}")
                st.markdown(f"**Tone:** `{s.get('emotional_tone')}`")
                st.write(s.get('description'))
                st.divider()
        with tab2:
            for c in d.get("characters", []):
                st.markdown(f"### 👤 {c.get('name')}")
                st.write(f"**Role:** {c.get('role')} | **Quirks:** {c.get('quirks')}")
                st.info(f"**Look:** {c.get('appearance')}")
        with tab3:
            st.dataframe(d.get("shot_list", []), use_container_width=True)
        with tab4:
            for p in d.get("storyboard_prompts", []):
                st.code(p, language="text")
