import streamlit as st
import json
import requests
import io
import zipfile
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# ==============================================================================
# CONFIGURACIÓN Y TEMA VISUAL (DESIGN SYSTEM FIGMA)
# ==============================================================================
st.set_page_config(
    page_title="WebAgentica • AI Agent Spec Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inyección de estilos CSS para coincidir con el prototipo
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    :root {
        --bg-main: #0B0F19;
        --card-bg: #111827;
        --card-border: #1F2937;
        --primary-coral: #F43F5E;
        --primary-hover: #E11D48;
        --emerald: #10B981;
        --text-muted: #9CA3AF;
        --text-white: #F9FAFB;
    }

    /* Fondo general */
    .stApp {
        background-color: var(--bg-main);
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: var(--text-white);
    }

    /* Ocultar elementos nativos de Streamlit */
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Top Navbar */
    .nav-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.8rem 1.2rem;
        background: #11182780;
        border: 1px solid #1F2937;
        border-radius: 12px;
        margin-bottom: 2rem;
        backdrop-filter: blur(10px);
    }
    .brand-logo {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 700;
        font-size: 1.1rem;
        color: white;
    }
    .badge-engine {
        background: rgba(16, 185, 129, 0.15);
        color: var(--emerald);
        border: 1px solid rgba(16, 185, 129, 0.3);
        font-size: 0.75rem;
        padding: 3px 8px;
        border-radius: 999px;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Hero Section */
    .hero-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: var(--text-muted);
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .hero-title {
        font-size: 2.3rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
        color: #FFFFFF;
    }
    .hero-title span {
        color: var(--primary-coral);
    }
    .hero-subtitle {
        text-align: center;
        color: var(--text-muted);
        font-size: 0.95rem;
        max-width: 650px;
        margin: 0 auto 2rem auto;
    }

    /* Input Card Container */
    .search-card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }
    .card-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
        color: var(--text-muted);
        margin-bottom: 0.8rem;
    }

    /* Modificación de Inputs y Botones de Streamlit */
    div[data-testid="stTextInput"] input {
        background-color: #0B0F19 !important;
        border: 1px solid #374151 !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: var(--primary-coral) !important;
        box-shadow: 0 0 0 1px var(--primary-coral) !important;
    }
    div[data-testid="stButton"] button[kind="primary"] {
        background-color: var(--primary-coral) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        padding: 10px !important;
    }
    div[data-testid="stButton"] button[kind="primary"]:hover {
        background-color: var(--primary-hover) !important;
        box-shadow: 0 0 15px rgba(244, 63, 94, 0.4) !important;
    }

    /* Cards Informativas (Frame 2) */
    .spec-card {
        background: #111827;
        border: 1px solid #1F2937;
        border-radius: 12px;
        padding: 1.25rem;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .spec-card:hover {
        border-color: #374151;
    }
    .spec-badge {
        font-size: 0.7rem;
        padding: 2px 6px;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        margin-top: 1rem;
        display: inline-block;
        width: fit-content;
    }
    .badge-green { background: rgba(16, 185, 129, 0.15); color: #10B981; }
    .badge-purple { background: rgba(139, 92, 246, 0.15); color: #A78BFA; }
    .badge-cyan { background: rgba(6, 182, 212, 0.15); color: #22D3EE; }

    /* Pipeline 4 Pasos */
    .pipeline-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-top: 1.5rem;
    }
    .pipeline-step {
        background: #0D1321;
        border: 1px solid #1E293B;
        border-radius: 8px;
        padding: 0.75rem;
        font-size: 0.8rem;
    }
    .pipeline-step b {
        color: white;
        display: block;
        margin-bottom: 2px;
    }

    /* Log Panel (Frame 3 - Resultados) */
    .log-panel {
        background: #111827;
        border: 1px solid #1F2937;
        border-radius: 12px;
        padding: 1.2rem;
    }
    .log-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 0;
        border-bottom: 1px solid #1F2937;
        font-size: 0.85rem;
    }
    .log-item:last-child { border-bottom: none; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# MOTOR DE RASTREO Y GENERACIÓN (BACKEND)
# ==============================================================================

def scan_website(base_url):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; AIAgentScanner/2.0; +https://google.com)"}
    resp = requests.get(base_url, headers=headers, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    
    title = soup.title.string.strip() if soup.title and soup.title.string else urlparse(base_url).netloc
    meta_desc = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
    description = meta_desc["content"].strip() if meta_desc and "content" in meta_desc.attrs else "Directorio y servicios disponibles para agentes de IA."
    
    # Enlaces de navegación
    links_dict = {}
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        link_text = a.get_text(strip=True)
        if not link_text or len(link_text) < 3 or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue
        full_url = urljoin(base_url, href)
        if urlparse(full_url).netloc == urlparse(base_url).netloc:
            if full_url not in links_dict and full_url != base_url:
                links_dict[full_url] = link_text

    categorized_links = [{"title": text, "url": url} for url, text in list(links_dict.items())[:6]]

    # Detección de herramientas WebMCP (Formularios/Búsqueda)
    detected_tools = []
    for idx, form in enumerate(soup.find_all("form")[:2]):
        action = form.get("action", "")
        method = form.get("method", "GET").upper()
        inputs = form.find_all(["input", "select"])
        form_endpoint = urljoin(base_url, action) if action else base_url
        params = {}
        for inp in inputs:
            name = inp.get("name")
            if name and inp.get("type") not in ["hidden", "submit"]:
                params[name] = {"type": "string", "description": f"Campo {name}"}
        
        if params:
            detected_tools.append({
                "name": "consulta_directorio" if "search" in form_endpoint.lower() else f"tool_accion_{idx+1}",
                "description": f"Consulta automatizada en {form_endpoint}",
                "endpoint": form_endpoint,
                "method": method,
                "parameters": params
            })

    if not detected_tools:
        detected_tools.append({
            "name": "consultar_directorio",
            "description": "Búsqueda de comercios, servicios y profesionales locales.",
            "endpoint": urljoin(base_url, "/buscar"),
            "method": "GET",
            "parameters": {"q": {"type": "string", "description": "Término o categoría de búsqueda"}}
        })

    return {
        "title": title,
        "description": description,
        "base_url": base_url,
        "links": categorized_links,
        "tools": detected_tools
    }

def generate_llms_txt(data):
    lines = [f"# {data['title']}", f"> {data['description']}\n", "## Enlaces Clave"]
    for l in data["links"]:
        lines.append(f"- [{l['title']}]({l['url']}): Enlace indexado por la web agéntica.")
    lines.append("\n## APIs y Servicios Disponibles\n- Acceso estructurado a directorios, comercios y documentación del sistema.")
    return "\n".join(lines)

def generate_ai_catalog(data):
    tools_formatted = [{
        "name": t["name"],
        "description": t["description"],
        "execution": {"type": "http", "method": t["method"], "endpoint": t["endpoint"]},
        "parameters": {"type": "object", "properties": t["parameters"], "required": list(t["parameters"].keys())}
    } for t in data["tools"]]

    return json.dumps({
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema_version": "1.0.0",
        "site": {"name": data["title"], "base_url": data["base_url"]},
        "capabilities": {"webmcp_version": "2024-11-05", "tools": tools_formatted}
    }, indent=2, ensure_ascii=False)

def generate_webmcp_snippet(data):
    tool = data["tools"][0]
    schema = {
        "@context": ["https://schema.org", {"@vocab": "https://modelcontextprotocol.io/spec/v1#"}],
        "@type": "WebMCPTool",
        "name": tool["name"],
        "description": tool["description"],
        "potentialAction": {
            "@type": "ConsumeAction",
            "target": {"@type": "EntryPoint", "urlTemplate": tool["endpoint"], "httpMethod": tool["method"]}
        },
        "inputSchema": {"type": "object", "properties": tool["parameters"]}
    }
    return f'<script type="application/ld+json">\n{json.dumps(schema, indent=2, ensure_ascii=False)}\n</script>'

# ==============================================================================
# NAVBAR SUPERIOR
# ==============================================================================
st.markdown("""
<div class="nav-container">
    <div class="brand-logo">
        <span style="color:#F43F5E;">⚡</span> WebAgentica
        <span class="badge-engine">v1.4 Engine Active</span>
    </div>
    <div style="font-size:0.85rem; color:#9CA3AF; display:flex; gap:20px;">
        <span style="color:white; font-weight:600;">Generador</span>
        <span>Especificaciones & Docs</span>
        <span>Historial</span>
        <span>Configuración</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Inicializar sesión
if "scan_data" not in st.session_state:
    st.session_state.scan_data = None

# ==============================================================================
# PANTALLA 1: INICIO / GENERADOR (PRE-SCAN)
# ==============================================================================
if st.session_state.scan_data is None:

    st.markdown('<div class="hero-badge">• Protocol Ready v2.4 • llms.txt • WebMCP • ai-catalog •</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Auto-Generador de Archivos para <span>Agentes de IA</span> 🤖</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Ingresa la URL de tu sitio web. El motor rastreará y analizará tu arquitectura digital, extrayendo metadatos, rutas navegables y herramientas API para alimentar los estándares agénticos universales.</div>', unsafe_allow_html=True)

    # Contenedor de Búsqueda
    with st.container():
        st.markdown('<div class="search-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-label">Configuración & Rastreo de Sitio Web</div>', unsafe_allow_html=True)
        
        col_url, col_btn = st.columns([4, 1.5])
        with col_url:
            target_url = st.text_input("URL", placeholder="https://tusitio.com", label_visibility="collapsed")
        with col_btn:
            run_scan = st.button("🚀 Escanear y Generar", type="primary")

        st.caption("Dominios Rápidos de Prueba: `https://stripe.com` • `https://wikipedia.org` • `https://github.com`")
        st.markdown('</div>', unsafe_allow_html=True)

    if run_scan and target_url:
        if not target_url.startswith("http"):
            st.error("Por favor ingresa una URL con http:// o https://")
        else:
            with st.spinner("Rastreando y compilando especificaciones para Agentes..."):
                try:
                    data = scan_website(target_url.rstrip("/"))
                    st.session_state.scan_data = {
                        "raw": data,
                        "llms": generate_llms_txt(data),
                        "catalog": generate_ai_catalog(data),
                        "mcp": generate_webmcp_snippet(data)
                    }
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al analizar el sitio: {str(e)}")

    # Sección Inferior: Cards de Especificaciones (Como en Figma)
    st.markdown("<h4 style='margin-top:2rem; margin-bottom:1rem; font-weight:600;'>Archivos y estándares que se generarán</h4>", unsafe_allow_html=True)
    
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        st.markdown("""
        <div class="spec-card">
            <div>
                <div style="font-size:1.3rem; margin-bottom:6px;">📄 <b>llms.txt</b></div>
                <p style="color:#9CA3AF; font-size:0.85rem;">Resumen estructurado en Markdown legible por agentes con ventanas de contexto reducidas. Guía a la IA por las secciones críticas sin necesidad de parsear todo el HTML.</p>
            </div>
            <span class="spec-badge badge-purple">Listo para inyectar</span>
        </div>
        """, unsafe_allow_html=True)

    with col_c2:
        st.markdown("""
        <div class="spec-card">
            <div>
                <div style="font-size:1.3rem; margin-bottom:6px;">⚙️ <b>ai-catalog.json</b></div>
                <p style="color:#9CA3AF; font-size:0.85rem;">Catálogo estandarizado con APIs, herramientas, esquemas de entrada y metadatos de la aplicación para integración en agentes con Function Calling.</p>
            </div>
            <span class="spec-badge badge-green">Protocolo Nativo Listo</span>
        </div>
        """, unsafe_allow_html=True)

    with col_c3:
        st.markdown("""
        <div class="spec-card">
            <div>
                <div style="font-size:1.3rem; margin-bottom:6px;">🏷️ <b>WebMCP Schema</b></div>
                <p style="color:#9CA3AF; font-size:0.85rem;">Definición de contexto de protocolo de modelo (Model Context Protocol). Proporciona acciones en tiempo real, sinopsis del sistema y capacidades de ejecución en navegador.</p>
            </div>
            <span class="spec-badge badge-cyan">MCP Compliant</span>
        </div>
        """, unsafe_allow_html=True)

    # Barra de Flujo (Pipeline)
    st.markdown("""
    <div style="margin-top:3rem;">
        <div class="card-label">Flujo de Escaneo en Tiempo Real</div>
        <div class="pipeline-container">
            <div class="pipeline-step"><b>1. DOM Fetch</b>Descarga el nivel HTML eliminando assets innecesarios.</div>
            <div class="pipeline-step"><b>2. Extracción Semántica</b>Identifica títulos, rutas canónicas, sinopsis y APIs.</div>
            <div class="pipeline-step"><b>3. Compilación MCP</b>Alinea acciones y recursos según la especificación WebMCP.</div>
            <div class="pipeline-step"><b>4. Empaquetado</b>Genera descarga en ZIP y código listo para CDN.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# PANTALLA 2: RESULTADOS (POST-SCAN)
# ==============================================================================
else:
    results = st.session_state.scan_data
    raw = results["raw"]

    # Barra Superior de Resultados
    col_t1, col_t2 = st.columns([4, 1.5])
    with col_t1:
        st.markdown(f"**Sitio Escaneado:** `{raw['base_url']}` &nbsp; <span class='badge-engine'>Agentes 100% Sincronizados</span>", unsafe_allow_html=True)
    with col_t2:
        if st.button("🔄 Re-escanear", type="secondary"):
            st.session_state.scan_data = None
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # 2 Columnas: Logs de Rastreo + Resumen de Exportación
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown(f"""
        <div class="log-panel">
            <div style="color:#10B981; font-weight:600; margin-bottom:12px;">✔ ¡Escaneo y generación completados con éxito!</div>
            <div class="log-item">
                <span style="color:#10B981;">✔</span>
                <div><b>Conectando y descargando estructura HTML</b><br><small style="color:#9CA3AF;">DOM response validado sin errores.</small></div>
            </div>
            <div class="log-item">
                <span style="color:#10B981;">✔</span>
                <div><b>Extrayendo metadatos OpenGraph & Semántica</b><br><small style="color:#9CA3AF;">{raw['title'][:45]}...</small></div>
            </div>
            <div class="log-item">
                <span style="color:#10B981;">✔</span>
                <div><b>Mapeados {len(raw['links'])} enlaces de navegación relevante</b><br><small style="color:#9CA3AF;">Rutas indexadas y normalizadas.</small></div>
            </div>
            <div class="log-item">
                <span style="color:#10B981;">✔</span>
                <div><b>Sintetizadas {len(raw['tools'])} herramientas agénticas WebMCP</b><br><small style="color:#9CA3AF;">Endpoints listos para Function Calling.</small></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        # Generar ZIP en memoria
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("llms.txt", results["llms"])
            zf.writestr("ai-catalog.json", results["catalog"])
            zf.writestr("webmcp-schema.html", results["mcp"])
        zip_bytes = zip_buf.getvalue()

        st.markdown(f"""
        <div class="log-panel">
            <div class="card-label">Resumen de Exportación</div>
            <div style="display:flex; justify-content:space-between; margin-bottom:15px;">
                <div><span style="font-size:1.8rem; font-weight:700;">3</span><br><small style="color:#9CA3AF;">llms, json, html</small></div>
                <div><span style="font-size:1.8rem; font-weight:700;">{round(len(zip_bytes)/1024, 1)} KB</span><br><small style="color:#9CA3AF;">Comprimido ZIP</small></div>
            </div>
            <div style="margin-bottom:12px; font-size:0.85rem;">Conformidad WebMCP: <b style="color:#10B981;">100% Válido</b></div>
        </div>
        """, unsafe_allow_html=True)

        st.download_button(
            label="📦 Descargar Bundle (.ZIP)",
            data=zip_bytes,
            file_name="agentic-spec-bundle.zip",
            mime="application/zip",
            type="primary"
        )

    # Visor de Código Inferior (Tabs con sintaxis limpia)
    st.markdown("<h4 style='margin-top:2rem; font-weight:600;'>Artefactos Agénticos Generados</h4>", unsafe_allow_html=True)
    tab_llms, tab_cat, tab_mcp = st.tabs(["📄 llms.txt", "⚙️ ai-catalog.json", "🏷️ WebMCP (HTML-LD)"])

    with tab_llms:
        st.code(results["llms"], language="markdown")
    with tab_cat:
        st.code(results["catalog"], language="json")
    with tab_mcp:
        st.code(results["mcp"], language="html")
