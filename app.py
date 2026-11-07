import streamlit as st
import json
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# Configuración de la página
st.set_page_config(
    page_title="AI Agent & WebMCP Readiness Suite",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Agent & WebMCP Readiness Suite")
st.markdown(
    "Generador y validador de estándares recomendados para la navegación e integración de agentes de IA: "
    "**llms.txt**, **ai-catalog.json** y esquemas **WebMCP**."
)

tabs = st.tabs(["🛠️ Generador de Archivos", "🔍 Validador de Sitio Web"])

# ==========================================
# TAB 1: GENERADOR
# ==========================================
with tabs[0]:
    st.header("Generador de Archivos y Metadatos")
    tipo = st.selectbox(
        "Selecciona el estándar que deseas generar:",
        ["1. llms.txt", "2. ai-catalog.json", "3. Esquema WebMCP (JSON-LD)"]
    )

    # --------------------------------------
    # 1. llms.txt
    # --------------------------------------
    if tipo == "1. llms.txt":
        st.subheader("Generador de `llms.txt`")
        st.info("Debe ubicarse en la raíz del dominio: `https://tusitio.com/llms.txt`")

        col1, col2 = st.columns(2)
        with col1:
            site_name = st.text_input("Nombre del Proyecto/Sitio", "Mi Sitio Web")
            summary = st.text_area(
                "Resumen descriptivo (Contexto para el LLM)",
                "Plataforma especializada en soluciones B2B y análisis de datos en tiempo real."
            )
        with col2:
            st.markdown("**Enlaces Clave (Documentación / Secciones)**")
            link_title1 = st.text_input("Título Sección 1", "Documentación API")
            link_url1 = st.text_input("Ruta/URL 1", "/docs/api.md")
            link_desc1 = st.text_input("Descripción 1", "Especificación de endpoints públicos.")
            
            link_title2 = st.text_input("Título Sección 2", "Catálogo de Productos")
            link_url2 = st.text_input("Ruta/URL 2", "/productos.md")
            link_desc2 = st.text_input("Descripción 2", "Lista completa de inventario disponible.")

        llms_content = f"""# {site_name}
> {summary}

## Documentación Principal
- [{link_title1}]({link_url1}): {link_desc1}
- [{link_title2}]({link_url2}): {link_desc2}

## Enlaces Opcionales
- [Términos de Uso para IA](/terminos-ia.md): Reglas de rate-limiting y gobernanza de bots.
"""
        st.code(llms_content, language="markdown")
        st.download_button(
            label="Descargar llms.txt",
            data=llms_content,
            file_name="llms.txt",
            mime="text/plain"
        )

    # --------------------------------------
    # 2. ai-catalog.json
    # --------------------------------------
    elif tipo == "2. ai-catalog.json":
        st.subheader("Generador de `ai-catalog.json`")
        st.info("Debe ubicarse en: `/.well-known/ai-catalog.json` o en `/ai-catalog.json`")

        c1, c2 = st.columns(2)
        with c1:
            cat_name = st.text_input("Nombre del Catálogo", "Enterprise Agent Tools")
            cat_url = st.text_input("URL Base de la API", "https://api.tusitio.com")
            privacy = st.text_input("URL Política de Privacidad", "https://tusitio.com/privacy")
        with c2:
            openapi_url = st.text_input("URL Especificación OpenAPI (Swagger)", "https://api.tusitio.com/openapi.json")
            mcp_endpoint = st.text_input("Endpoint del Servidor MCP (si aplica)", "https://mcp.tusitio.com/sse")

        catalog_data = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "schema_version": "1.0.0",
            "provider": {
                "name": cat_name,
                "base_url": cat_url,
                "privacy_policy": privacy
            },
            "protocols": {
                "webmcp": {
                    "enabled": True,
                    "endpoint": mcp_endpoint
                },
                "openapi": {
                    "enabled": True if openapi_url else False,
                    "spec_url": openapi_url
                }
            },
            "rate_limits": {
                "requests_per_minute": 60,
                "requires_api_key": False
            }
        }
        json_catalog = json.dumps(catalog_data, indent=2, ensure_ascii=False)
        st.code(json_catalog, language="json")
        st.download_button(
            label="Descargar ai-catalog.json",
            data=json_catalog,
            file_name="ai-catalog.json",
            mime="application/json"
        )

    # --------------------------------------
    # 3. WebMCP Schema
    # --------------------------------------
    elif tipo == "3. Esquema WebMCP (JSON-LD)":
        st.subheader("Generador de Esquema WebMCP (JSON-LD para el HTML)")
        st.info("Pega este fragmento dentro del bloque `<head>` de tu página web.")

        tool_name = st.text_input("Nombre de la Acción / Tool", "buscar_disponibilidad")
        tool_desc = st.text_input("Descripción de lo que hace", "Verifica la disponibilidad y precio del producto.")
        endpoint = st.text_input("Endpoint HTTP que procesa la acción", "https://api.tusitio.com/v1/tools/check")
        param_name = st.text_input("Nombre del parámetro principal", "productId")
        param_desc = st.text_input("Descripción del parámetro", "Identificador único (SKU) del producto")

        webmcp_schema = {
            "@context": [
                "https://schema.org",
                {"@vocab": "https://modelcontextprotocol.io/spec/v1#"}
            ],
            "@type": "WebMCPTool",
            "name": tool_name,
            "description": tool_desc,
            "potentialAction": {
                "@type": "ConsumeAction",
                "target": {
                    "@type": "EntryPoint",
                    "urlTemplate": endpoint,
                    "httpMethod": "POST",
                    "encodingType": "application/json"
                }
            },
            "inputSchema": {
                "type": "object",
                "properties": {
                    param_name: {
                        "type": "string",
                        "description": param_desc
                    }
                },
                "required": [param_name]
            }
        }

        html_snippet = f'<script type="application/ld+json">\n{json.dumps(webmcp_schema, indent=2, ensure_ascii=False)}\n</script>'
        st.code(html_snippet, language="html")
        st.download_button(
            label="Descargar Snippet HTML",
            data=html_snippet,
            file_name="webmcp-schema.html",
            mime="text/html"
        )

# ==========================================
# TAB 2: VALIDADOR
# ==========================================
with tabs[1]:
    st.header("Validador de Sitio Web")
    target_url = st.text_input("Introduce la URL base de tu sitio web a evaluar:", "https://example.com")
    
    if st.button("Ejecutar Validación Completa", type="primary"):
        if not target_url.startswith("http://") and not target_url.startswith("https://"):
            st.error("Ingresa una URL válida que comience con http:// o https://")
        else:
            base = target_url.rstrip("/")
            headers = {"User-Agent": "AIAgentValidator/1.0 (+https://google.com/searchconsole)"}

            # --------------------------------------
            # 1. Validar llms.txt
            # --------------------------------------
            st.markdown("### 1. Archivo `llms.txt`")
            llms_url = f"{base}/llms.txt"
            try:
                r_llms = requests.get(llms_url, headers=headers, timeout=6)
                if r_llms.status_code == 200:
                    text = r_llms.text.strip()
                    if text.startswith("#") and "\n>" in text:
                        st.success(f"✅ `llms.txt` localizado en `{llms_url}` y cumple con la especificación H1 + Blockquote.")
                    else:
                        st.warning(f"⚠️ `llms.txt` responde 200 OK, pero su contenido no parece Markdown estándar.")
                elif r_llms.status_code == 404:
                    st.error(f"❌ No encontrado: `{llms_url}` (HTTP 404).")
                else:
                    st.warning(f"⚠️ Respuesta inusual: `{llms_url}` retornó HTTP {r_llms.status_code}.")
            except Exception as e:
                st.error(f"❌ Error de red al solicitar `llms.txt`: {e}")

            # --------------------------------------
            # 2. Validar ai-catalog.json
            # --------------------------------------
            st.markdown("### 2. Archivo `ai-catalog.json`")
            paths = ["/.well-known/ai-catalog.json", "/ai-catalog.json"]
            catalog_ok = False

            for p in paths:
                cat_url = f"{base}{p}"
                try:
                    r_cat = requests.get(cat_url, headers=headers, timeout=6)
                    if r_cat.status_code == 200:
                        cors_header = r_cat.headers.get("Access-Control-Allow-Origin")
                        data = r_cat.json()
                        st.success(f"✅ `ai-catalog.json` detectado en `{cat_url}`.")
                        
                        if cors_header == "*" or cors_header:
                            st.caption(f"ℹ️ CORS configurado correctamente (`Access-Control-Allow-Origin: {cors_header}`).")
                        else:
                            st.warning("⚠️ El archivo no envía encabezados CORS permisivos (`Access-Control-Allow-Origin: *`). Agentes en navegadores podrían ser bloqueados.")
                        catalog_ok = True
                        break
                except json.JSONDecodeError:
                    st.error(f"❌ Archivo en `{cat_url}` responde 200 pero NO es un JSON válido.")
                except Exception:
                    continue

            if not catalog_ok:
                st.error("❌ No se encontró `ai-catalog.json` ni en `/.well-known/` ni en la raíz.")

            # --------------------------------------
            # 3. Validar Esquema WebMCP en el HTML
            # --------------------------------------
            st.markdown("### 3. Esquema WebMCP en HTML")
            try:
                r_home = requests.get(base, headers=headers, timeout=6)
                soup = BeautifulSoup(r_home.text, "html.parser")
                scripts = soup.find_all("script", type="application/ld+json")
                
                webmcp_found = False
                for script in scripts:
                    if script.string and ("WebMCPTool" in script.string or "modelcontextprotocol.io" in script.string):
                        webmcp_found = True
                        st.success("✅ Metadatos WebMCP (JSON-LD) detectados en el HTML de la página de inicio.")
                        st.json(json.loads(script.string))
                        break
                
                if not webmcp_found:
                    st.warning("⚠️ No se detectó ninguna definición de herramientas WebMCP en el `<head>` del sitio.")
            except Exception as e:
                st.error(f"❌ Error al inspeccionar el código HTML del sitio: {e}")
