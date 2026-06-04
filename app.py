import anthropic
import streamlit as st
from pathlib import Path

# ── configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Revisor de Guiones · QUO",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── cuentas disponibles ───────────────────────────────────────────────────────
# Para agregar una cuenta nueva:
# 1. Crear el archivo de reglas en accounts/<nombre_archivo>.txt
# 2. Agregar una entrada acá con el nombre visible y el nombre del archivo

CUENTAS = {
    "Caminos de las Sierras": {
        "archivo": "caminos_de_las_sierras.txt",
        "icono": "🛣️",
        "descripcion": "Revisión institucional y seguridad vial",
        "color": "#2d6a4f",
    },
    # ── agregar cuentas nuevas acá ──
    # "Municipalidad de Córdoba": {
    #     "archivo": "municipalidad_cordoba.txt",
    #     "icono": "🏛️",
    #     "descripcion": "Comunicación municipal",
    #     "color": "#1a4a8a",
    # },
    # "Legalia": {
    #     "archivo": "legalia.txt",
    #     "icono": "⚖️",
    #     "descripcion": "Contenido legal y corporativo",
    #     "color": "#4a1a2a",
    # },
}

# ── estilos ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .stApp { background-color: #f8f6f2; }

  .cuenta-header {
    padding: 1rem 1.5rem;
    border-radius: 10px;
    margin-bottom: 1.5rem;
    color: white;
  }
  .cuenta-header h2 { margin: 0; font-size: 1.3rem; }
  .cuenta-header p  { margin: 0.2rem 0 0; font-size: 0.85rem; opacity: 0.85; }

  .stTextArea textarea {
    border: 1px solid #ccc;
    border-radius: 8px;
    font-size: 0.92rem;
    font-family: 'Georgia', serif;
    background: #ffffff;
  }

  .resultado-box {
    background: #ffffff;
    border: 1px solid #e0ddd8;
    border-radius: 10px;
    padding: 1.5rem 2rem;
    line-height: 1.75;
  }

  section[data-testid="stSidebar"] {
    background-color: #1a1a2e;
  }
  section[data-testid="stSidebar"] * { color: #f0f0f0 !important; }
  section[data-testid="stSidebar"] .stRadio label { font-size: 0.95rem; }

  .quo-logo {
    text-align: center;
    padding: 1.2rem 0 1.5rem;
    font-size: 1.4rem;
    font-weight: 700;
    letter-spacing: 4px;
    color: #ffffff !important;
    border-bottom: 1px solid #333;
    margin-bottom: 1.5rem;
  }

  .stButton > button {
    border: none;
    border-radius: 8px;
    padding: 0.6rem 2rem;
    font-size: 1rem;
    font-weight: 600;
    width: 100%;
    color: white !important;
    transition: opacity 0.2s;
  }
  .stButton > button:hover { opacity: 0.85; }

  .footer { color: #aaa; font-size: 0.75rem; text-align: center; margin-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# ── sidebar — selector de cuentas ────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="quo-logo">QUO</div>', unsafe_allow_html=True)
    st.markdown("**Revisor de Guiones**")
    st.markdown("---")
    st.markdown("##### Seleccioná la cuenta")

    cuenta_nombre = st.radio(
        label="",
        options=list(CUENTAS.keys()),
        key="cuenta_selector",
    )

    cuenta = CUENTAS[cuenta_nombre]

    st.markdown("---")
    st.markdown(f"""
    <div style='font-size:0.78rem; color:#aaa; line-height:1.6;'>
    {cuenta['icono']} <b style='color:#ddd'>{cuenta_nombre}</b><br>
    {cuenta['descripcion']}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:0.75rem; color:#666; line-height:1.6;'>
    <b style='color:#888'>Qué revisa:</b><br>
    ✔ Errores de nombre<br>
    ✔ Alcance institucional<br>
    ✔ Seguridad vial<br>
    ✔ Tono y lenguaje<br>
    ✔ Riesgo reputacional
    </div>
    """, unsafe_allow_html=True)

# ── carga del system prompt ───────────────────────────────────────────────────
@st.cache_resource
def load_system_prompt(archivo: str) -> str:
    prompt_path = Path(__file__).parent / "accounts" / archivo
    if not prompt_path.exists():
        return f"Archivo de reglas no encontrado: {archivo}"
    return prompt_path.read_text(encoding="utf-8")

@st.cache_resource
def get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic()

# ── función de revisión ───────────────────────────────────────────────────────
def revisar(guion: str, archivo_cuenta: str) -> str:
    client = get_client()
    system = load_system_prompt(archivo_cuenta)

    with client.messages.stream(
        model="claude-opus-4-8",
        max_tokens=4096,
        thinking={"type": "adaptive"},
        system=system,
        messages=[{"role": "user", "content": guion}],
    ) as stream:
        message = stream.get_final_message()
        # busca el primer bloque de texto (ignora ThinkingBlock)
        for block in message.content:
            if block.type == "text":
                return block.text
        return "No se pudo obtener una respuesta."

# ── encabezado de cuenta ──────────────────────────────────────────────────────
st.markdown(f"""
<div class="cuenta-header" style="background: linear-gradient(90deg, {cuenta['color']}dd, {cuenta['color']}99);">
  <h2>{cuenta['icono']} {cuenta_nombre}</h2>
  <p>{cuenta['descripcion']}</p>
</div>
""", unsafe_allow_html=True)

# ── layout principal ──────────────────────────────────────────────────────────
col_input, col_output = st.columns([1, 1], gap="large")

with col_input:
    st.markdown("#### 📄 Pegá el guion, copy o escaleta")
    guion = st.text_area(
        label="",
        height=480,
        placeholder="Pegá acá el texto a revisar: guion completo, escaleta, copy, diálogos, descripción de escena...",
        key=f"guion_{cuenta_nombre}",
    )

    btn_color = cuenta["color"]
    st.markdown(f"""
    <style>.stButton > button {{ background: {btn_color}; }}</style>
    """, unsafe_allow_html=True)

    revisar_btn = st.button(f"🔍 Revisar para {cuenta_nombre}", use_container_width=True)

with col_output:
    st.markdown("#### 📋 Resultado de la revisión")
    resultado_placeholder = st.empty()

    if revisar_btn:
        if not guion.strip():
            resultado_placeholder.warning("Necesitás pegar algún contenido antes de revisar.")
        else:
            with st.spinner("Revisando..."):
                try:
                    resultado = revisar(guion, cuenta["archivo"])
                    resultado_placeholder.markdown(
                        f'<div class="resultado-box">{resultado}</div>',
                        unsafe_allow_html=True,
                    )
                except anthropic.AuthenticationError:
                    resultado_placeholder.error("❌ API key inválida. Verificá que ANTHROPIC_API_KEY esté configurada.")
                except anthropic.RateLimitError:
                    resultado_placeholder.error("❌ Límite de uso alcanzado. Esperá unos segundos y volvé a intentar.")
                except Exception as e:
                    resultado_placeholder.error(f"❌ Error inesperado: {e}")
    else:
        resultado_placeholder.markdown(
            '<div class="resultado-box" style="color:#aaa; font-style:italic;">'
            'El resultado de la revisión aparecerá acá.'
            '</div>',
            unsafe_allow_html=True,
        )

# ── footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="footer">Revisor de Guiones · QUO Agencia · Powered by Claude Opus 4.8</div>',
    unsafe_allow_html=True,
)
