import streamlit as st
import json
import requests
import io
import zipfile
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

st.set_page_config(
    page_title="AI Agent Auto-Scanner & WebMCP Suite",
    page_icon="⚡",
    layout="wide"
)

# ==========================================
# FUNCIONES DE EXTRACCIÓN Y RASTREO
# ==========================================

def scan_website(base_url):
    """Escanea el sitio web y extrae información semántica, enlaces y formularios."""
    headers = {"User-Agent": "Mozilla/5.0 (compatible; AIAgentScanner/2.0; +https://google.com)"}
    
    # 1. Petición a la Home
    resp = requests.get(base_url, headers=headers, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    
    # 2. Extracción de Título y Descripción
    title = soup.title.string.strip() if soup.title and soup.title.string else urlparse(base_url).netloc
    
    meta_desc = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
    description = meta_desc["content"].strip() if meta_desc and "content" in meta_desc.attrs else "Sitio web y plataforma digital oficial."
    
    # 3. Extracción de Enlaces de Navegación (para llms.txt)
    links_dict = {}
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        link_text = a.get_text(strip=True)
        if not link_text or len(link_text) < 3 or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue
            
        full_url = urljoin(base_url, href)
        # Solo enlaces internos
        if urlparse(full_url).netloc == urlparse(base_url).netloc:
            # Filtrar páginas irrelevantes repetidas
            if full_url not in links_dict and full_url != base_url and full_url != f"{base_url}/":
                links_dict[full_url] = link_text

    # Priorizar enlaces clave (docs, api, blog, contacto, productos)
    priority_keywords = ["doc", "api", "servicio", "producto", "blog", "precio", "contacto", "nosotros", "about", "terms"]
    categorized_links = []
    
    for url, text in list(links_dict.items())[:30]:  # Limitar a top 30
        is_priority = any(k in url.lower() or k in text.lower() for k in priority_keywords)
        categorized_links.append({"title": text, "url": url, "priority": is_priority})
        
    categorized_links = sorted(categorized_links, key=lambda x: x["priority"], reverse=True)[:10]

    # 4. Detección de Formularios / Búsquedas para WebMCP
    detected_tools = []
    forms = soup.find_all("form")
    for idx, form in enumerate(forms):
        action = form.get("action", "")
        method = form.get("method", "GET").upper()
        inputs = form.find_all(["input", "select"])
        
        form_endpoint = urljoin(base_url, action) if action else base_url
        params = {}
        
        for inp in inputs:
            name = inp.get("name")
            inp_type = inp.get("type", "text")
            if name and inp_type not in ["hidden", "submit", "button"]:
                params[name] = {
                    "type": "string",
                    "description": f"Parámetro {name} (campo {inp_type})"
                }
        
        if params:
            tool_name = f"accion_formulario_{idx+1}"
            if any("search" in k.lower() or "q" == k.lower() or "query" in k.lower() for k in params):
                tool_name = "buscar_en_sitio"
                
            detected_tools.append({
                "name": tool_name,
                "description": f"Ejecuta una consulta en {form_endpoint}",
                "endpoint": form_endpoint,
                "method": method,
                "parameters": params
            })

    # Si no detectó formularios, crear una búsqueda genérica WebMCP por defecto
    if not detected_tools:
        detected_tools.append({
            "name": "buscar_en_sitio",
            "description": "Herramienta por defecto para buscar contenidos o productos en el sitio.",
            "endpoint": urljoin(base_url, "/search"),
            "method": "GET",
            "parameters": {
                "query": {"type": "string", "description": "Término de búsqueda o palabra clave"}
            }
        })

    # 5. Detección tentativa de OpenAPI
    openapi_detected = None
    for path in ["/openapi.json", "/swagger.json", "/api-docs"]:
        try:
            test_url = urljoin(base_url, path)
            r_test = requests.head(test_url, headers=headers, timeout=3)
            if r_test.status_code == 200:
                openapi_detected = test_url
                break
        except Exception:
            pass

    return {
        "title": title,
        "description": description,
        "base_url": base_url,
        "links": categorized_links,
        "tools": detected_tools,
        "openapi": openapi_detected
    }

# ==========================================
# GENERADORES DE ARCHIVOS
# ==========================================

def generate_llms_txt(data):
    lines = [f"# {data['title']}", f"> {data['description']}\n", "## Documentación y Enlaces Clave"]
    for l in data["links"]:
        lines.append(f"- [{l['title']}]({l['url']}): Enlace indexado por la web agéntica.")
    lines.append("\n## Gobernanza y Reglas de IA\n- [Términos de Servicio](/tos): Acceso para agentes automatizados y bots de búsqueda.")
    return "\n".join(lines)

def generate_ai_catalog(data):
    tools_formatted = []
    for t in data["tools"]:
        tools_formatted.append({
            "name": t["name"],
            "description": t["description"],
            "execution": {
                "type": "http",
                "method": t["method"],
                "endpoint": t["endpoint"]
            },
            "parameters": {
                "type": "object",
                "properties": t["parameters"],
                "required": list(t["parameters"].keys())
            }
        })

    catalog = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema_version": "1.0.0",
        "site": {
            "name": data["title"],
            "base_url": data["base_url"],
            "description": data["description"]
        },
        "capabilities": {
            "webmcp_version": "2024-11-05",
            "tools": tools_formatted,
            "openapi_spec": data["openapi"]
        }
    }
    return json.dumps(catalog, indent=2, ensure_ascii=False)

def generate_webmcp_snippet(data):
    tool = data["tools"][0]
    schema = {
        "@context": [
            "https://schema.org",
            {"@vocab": "https://modelcontextprotocol.io/spec/v1#"}
        ],
        "@type": "WebMCPTool",
        "name": tool["name"],
        "description": tool["description"],
        "potentialAction": {
            "@type": "ConsumeAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": tool["endpoint"],
                "httpMethod": tool["method"]
            }
        },
        "inputSchema": {
            "type": "object",
            "properties": tool["parameters"],
            "required": list(tool["parameters"].keys())
        }
    }
    return f'<!-- Pega este código dentro de la etiqueta <head> de tu página web -->\n<script type="application/ld+json">\n{json.dumps(schema, indent=2, ensure_ascii=False)}\n</script>'

def create_zip_package(llms_txt, ai_catalog, webmcp_html):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("llms.txt", llms_txt)
        zip_file.writestr("ai-catalog.json", ai_catalog)
        zip_file.writestr("webmcp-schema.html", webmcp_html)
    return buf.getvalue()


# ==========================================
# INTERFAZ STREAMLIT
# ==========================================

st.title("⚡ Auto-Generador de Archivos para Agentes de IA")
st.markdown("Ingresa la URL de tu sitio web. El sistema lo escaneará, extraerá su estructura y creará automáticamente los archivos **llms.txt**, **ai-catalog.json** y el esquema **WebMCP**.")

url_input = st.text_input("Ingresa la URL completa de tu sitio web:", "https://")

if st.button("🚀 Escanear Sitio y Generar Todo", type="primary"):
    if not url_input.startswith("http://") and not url_input.startswith("https://"):
        st.error("Por favor ingresa una URL válida (ejemplo: https://tu-dominio.com)")
    else:
        url_input = url_input.rstrip("/")
        with st.status("Analizando sitio web...", expanded=True) as status:
            try:
                st.write("🌐 Conectando y descargando estructura HTML...")
                data = scan_website(url_input)
                
                st.write(f"📝 Extrayendo metadatos: **{data['title']}**")
                st.write(f"🔗 Mapeados {len(data['links'])} enlaces de navegación relevantes.")
                st.write(f"🛠️ Detectadas {len(data['tools'])} herramientas/acciones para WebMCP.")
                
                # Generar archivos
                llms_txt = generate_llms_txt(data)
                ai_catalog = generate_ai_catalog(data)
                webmcp_html = generate_webmcp_snippet(data)
                zip_data = create_zip_package(llms_txt, ai_catalog, webmcp_html)
                
                status.update(label="¡Escaneo y generación completados con éxito!", state="complete", expanded=False)
                
                # Botón de descarga del paquete completo
                st.success("🎉 Todos los archivos han sido generados con base en el análisis de tu web.")
                st.download_button(
                    label="📦 Descargar Todos los Archivos (.ZIP)",
                    data=zip_data,
                    file_name="ai-agent-files.zip",
                    mime="application/zip",
                    type="primary"
                )
                
                # Vista previa con tabs
                st.markdown("### Vista Previa de los Archivos")
                prev_tab1, prev_tab2, prev_tab3 = st.tabs(["📄 llms.txt", "⚙️ ai-catalog.json", "🏷️ WebMCP (HTML)"])
                
                with prev_tab1:
                    st.caption("Ubicación recomendada: `https://tusitio.com/llms.txt`")
                    st.code(llms_txt, language="markdown")
                    st.download_button("Descargar solo llms.txt", llms_txt, "llms.txt", "text/plain")
                    
                with prev_tab2:
                    st.caption("Ubicación recomendada: `https://tusitio.com/.well-known/ai-catalog.json` o `/ai-catalog.json`")
                    st.code(ai_catalog, language="json")
                    st.download_button("Descargar solo ai-catalog.json", ai_catalog, "ai-catalog.json", "application/json")
                    
                with prev_tab3:
                    st.caption("Ubicación: Pegar dentro de la etiqueta `<head>` en tu HTML principal.")
                    st.code(webmcp_html, language="html")
                    st.download_button("Descargar solo WebMCP snippet", webmcp_html, "webmcp-schema.html", "text/html")

            except Exception as e:
                status.update(label="Error durante el escaneo", state="error")
                st.error(f"No fue posible analizar la URL especificada: {str(e)}")
