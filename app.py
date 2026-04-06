from __future__ import annotations

import os
import io
import re
import json
import time
import math
import random
import textwrap
import datetime as dt
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st

# Optional deps (guarded)
try:
    import yaml
except Exception:
    yaml = None

try:
    import pandas as pd
except Exception:
    pd = None

try:
    import altair as alt
except Exception:
    alt = None

try:
    import requests
except Exception:
    requests = None

try:
    import httpx
except Exception:
    httpx = None

try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None

# LLM SDKs (guarded)
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

try:
    import google.generativeai as genai
except Exception:
    genai = None

try:
    from anthropic import Anthropic
except Exception:
    Anthropic = None

# Graph rendering (optional)
try:
    import graphviz
except Exception:
    graphviz = None


# -----------------------------
# Constants & Localization
# -----------------------------

APP_TITLE = "WOW Agentic Regulatory Studio"
APP_VERSION = "1.0.0"

ENV_KEYS = {
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "grok": "GROK_API_KEY",
}

# Model registry
ALL_MODELS = [
    # OpenAI
    "gpt-4o-mini",
    "gpt-4.1-mini",
    # Gemini
    "gemini-2.5-flash",
    "gemini-3-flash-preview",
    "gemini-2.5-flash-lite",
    "gemini-3.1-flash-lite-preview",
    # Anthropic (examples; allow user to add via agents.yaml too)
    "claude-3-5-sonnet-2024-10",
    "claude-3-5-haiku-20241022",
    # Grok
    "grok-4-fast-reasoning",
    "grok-3-mini",
]

GEMINI_GUIDANCE_MODELS_STEP_A = [
    "gemini-2.5-flash",
    "gemini-3-flash-preview",
    "gemini-3.1-flash-lite-preview",
]
GEMINI_GUIDANCE_MODELS_STEP_B = [
    "gemini-2.5-flash",
    "gemini-3-flash-preview",
]
GEMINI_GUIDANCE_MODELS_STEP_C = [
    "gemini-2.5-flash",
    "gemini-3-flash-preview",
]

THEMES = ["Light", "Dark"]
UI_LANGS = ["English", "繁體中文"]

PAINTER_STYLES = [
    "Monet",
    "Van Gogh",
    "Klimt",
    "Picasso",
    "Hokusai",
    "Turner",
    "Vermeer",
    "Renoir",
    "Matisse",
    "Kandinsky",
    "Dalí",
    "Rembrandt",
    "Frida Kahlo",
    "Georgia O’Keeffe",
    "Edward Hopper",
    "Cézanne",
    "Gauguin",
    "Caravaggio",
    "Magritte",
    "Rothko",
]

# Painter style CSS (lightweight gradients; keep safe for Streamlit)
STYLE_CSS = {
    "Monet": "linear-gradient(120deg, #d9f2ff 0%, #fff6e5 100%)",
    "Van Gogh": "linear-gradient(120deg, #0b3d91 0%, #f9d65c 50%, #f26b38 100%)",
    "Klimt": "linear-gradient(120deg, #fff3b0 0%, #d4af37 45%, #3b2f2f 100%)",
    "Picasso": "linear-gradient(120deg, #ff595e 0%, #ffca3a 33%, #8ac926 66%, #1982c4 100%)",
    "Hokusai": "linear-gradient(120deg, #e0f7ff 0%, #0b3d91 65%, #ffffff 100%)",
    "Turner": "linear-gradient(120deg, #ffe29a 0%, #ff7a59 60%, #7bdff2 100%)",
    "Vermeer": "linear-gradient(120deg, #0b1320 0%, #2b4c7e 55%, #f3d9b1 100%)",
    "Renoir": "linear-gradient(120deg, #ffd6e8 0%, #fff1cc 100%)",
    "Matisse": "linear-gradient(120deg, #ff4d6d 0%, #4d96ff 50%, #f9f871 100%)",
    "Kandinsky": "linear-gradient(120deg, #111827 0%, #7c3aed 45%, #22c55e 100%)",
    "Dalí": "linear-gradient(120deg, #0f172a 0%, #f59e0b 45%, #ef4444 100%)",
    "Rembrandt": "linear-gradient(120deg, #1c1917 0%, #7c2d12 55%, #fbbf24 100%)",
    "Frida Kahlo": "linear-gradient(120deg, #14532d 0%, #ef4444 50%, #fde047 100%)",
    "Georgia O’Keeffe": "linear-gradient(120deg, #f8fafc 0%, #e2e8f0 45%, #111827 100%)",
    "Edward Hopper": "linear-gradient(120deg, #0f172a 0%, #334155 55%, #fde68a 100%)",
    "Cézanne": "linear-gradient(120deg, #dbeafe 0%, #fde68a 55%, #86efac 100%)",
    "Gauguin": "linear-gradient(120deg, #7c3aed 0%, #fb7185 55%, #fbbf24 100%)",
    "Caravaggio": "linear-gradient(120deg, #0b0f19 0%, #7f1d1d 55%, #f5f5f4 100%)",
    "Magritte": "linear-gradient(120deg, #93c5fd 0%, #f8fafc 60%, #111827 100%)",
    "Rothko": "linear-gradient(120deg, #7f1d1d 0%, #b45309 50%, #0f172a 100%)",
}

I18N = {
    "English": {
        "sidebar_settings": "Settings",
        "theme": "Theme",
        "language": "UI Language",
        "painter_style": "Painter Style",
        "jackpot": "Jackpot style",
        "default_model": "Default model",
        "temperature": "Temperature",
        "max_tokens": "Max tokens",
        "api_keys": "API Keys",
        "loaded_from_env": "Loaded from environment",
        "enter_key": "Enter API key",
        "clear_key": "Clear key",
        "agents_catalog": "Agents Catalog",
        "upload_agents_yaml": "Upload agents.yaml",
        "tabs_dashboard": "Dashboard",
        "tabs_tw": "TW Premarket",
        "tabs_510k_intel": "510(k) Intelligence",
        "tabs_pdf_md": "PDF → Markdown",
        "tabs_510k_pipeline": "510(k) Review Pipeline",
        "tabs_notes": "AI Note Keeper",
        "tabs_guidance": "Guidance Reviewer & Research",
        "tabs_agents": "Agents Config Studio",
        "status": "Status",
        "run": "Run",
        "prompt": "Prompt",
        "system_prompt": "System prompt",
        "input": "Input",
        "output": "Output",
        "output_view": "Output view",
        "markdown": "Markdown",
        "text": "Text",
        "download": "Download",
        "save": "Save",
        "error": "Error",
        "ready": "Ready",
        "running": "Running",
        "done": "Done",
        "blocked": "Blocked",
        "needs_review": "Needs review",
        "provider": "Provider",
        "duration": "Duration",
        "tokens_est": "Tokens (est.)",
        "history": "Run history",
        "reset": "Reset",
        "offline_mode": "Offline mode (no external retrieval)",
        "enable_web_retrieval": "Enable web retrieval (if network allowed)",
        "output_language": "Output language",
        "tc_default": "Traditional Chinese (default)",
        "en": "English",
        "upload_or_paste": "Upload or paste guidance",
        "paste_here": "Paste here",
        "file_upload": "Upload file (txt/md/pdf)",
        "step_a": "Step A — Comprehensive grounded research report (2000–3000 words)",
        "step_b": "Step B — Template-based report",
        "step_c": "Step C — Generate skill.md",
        "template": "Template",
        "use_default_template": "Use default template",
        "upload_template": "Upload template (md/txt)",
        "knowledge_graph": "Regulatory Knowledge Graph",
        "grounding_inspector": "Grounding Inspector",
        "bilingual": "Bilingual side-by-side renderer",
        "build_graph": "Build graph",
        "inspect": "Inspect grounding",
        "render_bilingual": "Render bilingual",
    },
    "繁體中文": {
        "sidebar_settings": "設定",
        "theme": "主題",
        "language": "介面語言",
        "painter_style": "畫家風格",
        "jackpot": "Jackpot 隨機風格",
        "default_model": "預設模型",
        "temperature": "溫度",
        "max_tokens": "最大 tokens",
        "api_keys": "API 金鑰",
        "loaded_from_env": "已由環境變數載入",
        "enter_key": "輸入 API 金鑰",
        "clear_key": "清除金鑰",
        "agents_catalog": "Agents 目錄",
        "upload_agents_yaml": "上傳 agents.yaml",
        "tabs_dashboard": "儀表板",
        "tabs_tw": "TFDA 查驗登記",
        "tabs_510k_intel": "FDA 510(k) 情報",
        "tabs_pdf_md": "PDF → Markdown",
        "tabs_510k_pipeline": "510(k) 審查流程",
        "tabs_notes": "AI 筆記保管員",
        "tabs_guidance": "指引審閱與法規研究",
        "tabs_agents": "Agents 設定工作室",
        "status": "狀態",
        "run": "執行",
        "prompt": "提示詞",
        "system_prompt": "系統提示詞",
        "input": "輸入",
        "output": "輸出",
        "output_view": "輸出檢視",
        "markdown": "Markdown",
        "text": "文字",
        "download": "下載",
        "save": "儲存",
        "error": "錯誤",
        "ready": "就緒",
        "running": "執行中",
        "done": "完成",
        "blocked": "被阻擋",
        "needs_review": "需覆核",
        "provider": "供應商",
        "duration": "耗時",
        "tokens_est": "Tokens（估）",
        "history": "執行紀錄",
        "reset": "重設",
        "offline_mode": "離線模式（不進行外部檢索）",
        "enable_web_retrieval": "啟用網路檢索（若環境允許）",
        "output_language": "輸出語言",
        "tc_default": "繁體中文（預設）",
        "en": "英文",
        "upload_or_paste": "上傳或貼上指引",
        "paste_here": "貼在這裡",
        "file_upload": "上傳檔案（txt/md/pdf）",
        "step_a": "步驟 A — 生成 2000–3000 字、具引用之研究報告",
        "step_b": "步驟 B — 套用模板產生報告",
        "step_c": "步驟 C — 產生 skill.md",
        "template": "模板",
        "use_default_template": "使用預設模板",
        "upload_template": "上傳模板（md/txt）",
        "knowledge_graph": "法規知識圖譜",
        "grounding_inspector": "引用/落地檢查器",
        "bilingual": "雙語並排渲染器",
        "build_graph": "建立圖譜",
        "inspect": "檢查落地",
        "render_bilingual": "生成雙語",
    },
}


def t(key: str) -> str:
    lang = st.session_state.get("settings", {}).get("ui_lang", "English")
    return I18N.get(lang, I18N["English"]).get(key, key)


# -----------------------------
# Utilities
# -----------------------------

def now_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def approx_tokens(text: str) -> int:
    # Rough heuristic: 4 chars/token (varies by language/model)
    if not text:
        return 0
    return max(1, int(len(text) / 4))


def safe_filename(name: str, default: str = "download") -> str:
    name = re.sub(r"[^\w\-. ]+", "_", name.strip())
    name = name.replace(" ", "_")
    return name or default


def apply_style(theme: str, painter_style: str) -> None:
    bg = STYLE_CSS.get(painter_style, STYLE_CSS["Monet"])
    if theme == "Dark":
        base_text = "#E5E7EB"
        card_bg = "rgba(17, 24, 39, 0.65)"
        border = "rgba(255, 255, 255, 0.08)"
        input_bg = "rgba(17, 24, 39, 0.85)"
        accent = "#22c55e"
    else:
        base_text = "#111827"
        card_bg = "rgba(255, 255, 255, 0.72)"
        border = "rgba(17, 24, 39, 0.10)"
        input_bg = "rgba(255, 255, 255, 0.90)"
        accent = "#0ea5e9"

    css = f"""
    <style>
      .stApp {{
        background: {bg};
        background-attachment: fixed;
        color: {base_text};
      }}
      .wow-card {{
        background: {card_bg};
        border: 1px solid {border};
        padding: 14px 16px;
        border-radius: 14px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.10);
        margin: 8px 0;
      }}
      .wow-chip {{
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        border: 1px solid {border};
        background: rgba(0,0,0,0.08);
        font-size: 12px;
        margin-right: 6px;
      }}
      .wow-status-idle {{ background: rgba(148,163,184,0.20); }}
      .wow-status-ready {{ background: rgba(34,197,94,0.20); }}
      .wow-status-running {{ background: rgba(245,158,11,0.25); }}
      .wow-status-done {{ background: rgba(14,165,233,0.20); }}
      .wow-status-error {{ background: rgba(239,68,68,0.25); }}
      .wow-status-blocked {{ background: rgba(239,68,68,0.18); }}
      .wow-status-review {{ background: rgba(168,85,247,0.20); }}

      .wow-kpi {{
        font-size: 28px;
        font-weight: 800;
        line-height: 1.0;
      }}
      .wow-muted {{ opacity: 0.8; font-size: 13px; }}

      /* Inputs: try to improve contrast; Streamlit limits full control */
      textarea, input {{
        background: {input_bg} !important;
      }}

      /* Coral keyword highlight */
      .kw-coral {{
        color: #ff7f50;
        font-weight: 700;
      }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def status_chip(status: str) -> str:
    mapping = {
        "Idle": "wow-status-idle",
        "Ready": "wow-status-ready",
        "Running": "wow-status-running",
        "Done": "wow-status-done",
        "Error": "wow-status-error",
        "Blocked": "wow-status-blocked",
        "Needs review": "wow-status-review",
    }
    css_class = mapping.get(status, "wow-status-idle")
    return f'<span class="wow-chip {css_class}">{status}</span>'


def provider_for_model(model: str) -> str:
    m = (model or "").lower()
    if m.startswith("gpt-"):
        return "openai"
    if m.startswith("gemini-"):
        return "gemini"
    if "claude" in m:
        return "anthropic"
    if m.startswith("grok-"):
        return "grok"
    # default: let it fail later with a good error
    return "unknown"


def get_api_key(provider: str) -> Tuple[Optional[str], str]:
    """
    Returns (api_key, source) where source in {"env","session","missing"}.
    """
    env_name = ENV_KEYS.get(provider)
    if env_name:
        v = os.getenv(env_name)
        if v:
            return v, "env"
    key = st.session_state.get("api_keys", {}).get(provider)
    if key:
        return key, "session"
    return None, "missing"


def log_event(tab: str, agent: str, model: str, provider: str,
              tokens_in: int, tokens_out: int, duration_ms: int,
              extra: Optional[Dict[str, Any]] = None) -> None:
    st.session_state.setdefault("history", [])
    st.session_state["history"].append({
        "ts": now_iso(),
        "tab": tab,
        "agent": agent,
        "model": model,
        "provider": provider,
        "tokens_in_est": tokens_in,
        "tokens_out_est": tokens_out,
        "tokens_total_est": tokens_in + tokens_out,
        "duration_ms": duration_ms,
        **(extra or {}),
    })


# -----------------------------
# LLM Call Router
# -----------------------------

def call_llm(
    model: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    temperature: float,
) -> str:
    provider = provider_for_model(model)
    api_key, source = get_api_key(provider)
    if not api_key:
        raise RuntimeError(f"Missing API key for provider={provider} (source={source}).")

    max_tokens = int(clamp(max_tokens, 256, 120000))
    temperature = float(clamp(temperature, 0.0, 1.0))

    if provider == "openai":
        if OpenAI is None:
            raise RuntimeError("OpenAI SDK not installed.")
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt or ""},
                {"role": "user", "content": user_prompt or ""},
            ],
        )
        return resp.choices[0].message.content or ""

    if provider == "gemini":
        if genai is None:
            raise RuntimeError("google-generativeai SDK not installed.")
        genai.configure(api_key=api_key)
        gmodel = genai.GenerativeModel(model)
        # Gemini uses a different config name
        resp = gmodel.generate_content(
            (system_prompt or "") + "\n\n" + (user_prompt or ""),
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            },
        )
        # Some responses provide .text; others in candidates
        text = getattr(resp, "text", None)
        if text:
            return text
        try:
            return resp.candidates[0].content.parts[0].text
        except Exception:
            return str(resp)

    if provider == "anthropic":
        if Anthropic is None:
            raise RuntimeError("Anthropic SDK not installed.")
        client = Anthropic(api_key=api_key)
        resp = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "",
            messages=[{"role": "user", "content": user_prompt or ""}],
        )
        # Anthropic returns list of content blocks
        out = []
        for block in resp.content:
            if getattr(block, "type", "") == "text":
                out.append(block.text)
        return "\n".join(out).strip()

    if provider == "grok":
        if httpx is None:
            raise RuntimeError("httpx not installed (required for Grok).")
        # xAI compatible endpoint
        url = "https://api.x.ai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system_prompt or ""},
                {"role": "user", "content": user_prompt or ""},
            ],
        }
        with httpx.Client(timeout=60.0) as client:
            r = client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
        return data["choices"][0]["message"]["content"] or ""

    raise RuntimeError(f"Unknown provider for model={model} (provider={provider}).")


# -----------------------------
# Agents Catalog
# -----------------------------

DEFAULT_AGENTS_CATALOG = {
    "agents": {
        "pdf_to_markdown_agent": {
            "model": "gemini-2.5-flash",
            "max_tokens": 12000,
            "temperature": 0.2,
            "system_prompt": "You convert extracted PDF text into clean, well-structured Markdown. Preserve headings, lists, tables when possible. Do not hallucinate content.",
            "user_prompt": "Convert the following text into Markdown. If you see page headers/footers, remove them. Keep section titles and numbering.",
        },
        "tw_screen_review_agent": {
            "model": "gemini-2.5-flash",
            "max_tokens": 14000,
            "temperature": 0.2,
            "system_prompt": "You are a TFDA pre-screening reviewer. You check completeness, consistency, and missing attachments. Be strict and actionable.",
            "user_prompt": "Perform a TFDA pre-screening review. Output: (1) Key issues (must-fix), (2) Nice-to-have improvements, (3) Completeness checklist table with status and remarks.",
        },
        "tw_app_doc_helper": {
            "model": "gemini-2.5-flash",
            "max_tokens": 14000,
            "temperature": 0.2,
            "system_prompt": "You are a regulatory technical writer. Improve structure and clarity without changing facts. Mark missing info as ※待補.",
            "user_prompt": "Rewrite the application draft into clear, consistent Traditional Chinese Markdown suitable for a submission draft.",
        },
        "fda_510k_intel_agent": {
            "model": "gemini-2.5-flash",
            "max_tokens": 16000,
            "temperature": 0.2,
            "system_prompt": "You are an FDA 510(k) intelligence analyst. Be careful about uncertainty. Provide citations where sources are given.",
            "user_prompt": "Create a 510(k) intelligence memo based on the provided inputs. Include: device overview, potential predicates, relevant guidance/standards, key questions, and a checklist.",
        },
        "note_organizer_agent": {
            "model": "gpt-4o-mini",
            "max_tokens": 8000,
            "temperature": 0.2,
            "system_prompt": "You are an expert note organizer. Produce organized Markdown with headings, bullets, action items, and highlight keywords with <span class=\"kw-coral\">...</span>.",
            "user_prompt": "Transform the note into organized Markdown. Add a short keyword list at top. Highlight important keywords in coral using span class kw-coral.",
        },
        # Guidance workspace agents
        "guidance_analyze_research_agent": {
            "model": "gemini-3-flash-preview",
            "max_tokens": 24000,
            "temperature": 0.2,
            "system_prompt": "You are a senior medical device regulatory researcher. You MUST ground claims in provided excerpts and retrieved sources. If external retrieval is unavailable, say so and provide a verification checklist.",
            "user_prompt": "Generate a 2000–3000 word grounded regulatory research report in the requested language, using citations and a complete source library.",
        },
        "template_report_agent": {
            "model": "gemini-2.5-flash",
            "max_tokens": 18000,
            "temperature": 0.2,
            "system_prompt": "You fit an existing report into a provided template while preserving meaning and citation tags.",
            "user_prompt": "Rewrite the report to match the template exactly. Preserve citations like [S1], [G-p12], etc.",
        },
        "skill_md_generator_agent": {
            "model": "gemini-2.5-flash",
            "max_tokens": 16000,
            "temperature": 0.2,
            "system_prompt": "You are creating a SKILL.md in the standard skill format. Write the entire content in the specified language. Include 3 WOW behaviors: Auto-Crosswalk Builder, Citation Quality Gate, Checklist-to-Actions Converter.",
            "user_prompt": "Create a skill.md that defines a new agent skill for generating comprehensive medical device guidance based on the structure of the provided guidance and reports. Use standard skill-creator format.",
        },
        "grounding_inspector_agent": {
            "model": "gemini-2.5-flash",
            "max_tokens": 8000,
            "temperature": 0.2,
            "system_prompt": "You are a grounding inspector. Identify uncited claims and ambiguous or outdated references. Provide a fix list.",
            "user_prompt": "Inspect the document for grounding issues. Output: (1) uncited claims list, (2) ambiguous language list, (3) outdated references risk, (4) suggested fixes.",
        },
        "knowledge_graph_agent": {
            "model": "gemini-2.5-flash",
            "max_tokens": 8000,
            "temperature": 0.2,
            "system_prompt": "Extract a compact knowledge graph as JSON triples. Be faithful to the text; do not invent nodes.",
            "user_prompt": "Extract a knowledge graph from the document as JSON with keys: nodes[], edges[] where edges are {source, relation, target, evidence_excerpt, citations[]}.",
        },
        "bilingual_renderer_agent": {
            "model": "gemini-2.5-flash",
            "max_tokens": 12000,
            "temperature": 0.2,
            "system_prompt": "You translate while preserving Markdown structure and tables. Do not change meaning. Keep citations intact.",
            "user_prompt": "Render a bilingual version: preserve headings and table alignment. Keep citations unchanged.",
        },
    }
}


def load_agents_catalog_from_disk() -> Optional[Dict[str, Any]]:
    if yaml is None:
        return None
    for path in ["agents.yaml", "agents.yml"]:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                if isinstance(data, dict) and "agents" in data and isinstance(data["agents"], dict):
                    return data
            except Exception:
                return None
    return None


def ensure_agents_catalog() -> None:
    if "agents_cfg" not in st.session_state:
        disk = load_agents_catalog_from_disk()
        st.session_state["agents_cfg"] = disk or DEFAULT_AGENTS_CATALOG


# -----------------------------
# Retrieval (FDA + web fallback)
# -----------------------------

@dataclass
class SourceItem:
    source_id: str
    title: str
    url: str
    publisher: str
    doc_no: str
    date: str
    accessed: str
    snippet: str
    relevance: str
    kind: str  # e.g., "510k", "guidance", "standard", "user_url", "offline"


def can_web_retrieve() -> bool:
    if requests is None:
        return False
    return bool(st.session_state.get("guidance", {}).get("enable_web", False)) and not bool(
        st.session_state.get("guidance", {}).get("offline_mode", False)
    )


def openfda_510k_by_product_code(product_code: str, limit: int = 5) -> List[SourceItem]:
    if not (requests and product_code):
        return []
    url = "https://api.fda.gov/device/510k.json"
    params = {"search": f"product_code:{product_code}", "limit": str(limit)}
    try:
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return []

    out = []
    results = data.get("results", []) or []
    for i, item in enumerate(results, start=1):
        k = item.get("k_number", "") or ""
        dev = item.get("device_name", "") or item.get("openfda", {}).get("device_name", "")
        date = item.get("decision_date", "") or item.get("date_received", "") or ""
        sponsor = item.get("applicant", "") or ""
        # openFDA doesn't always provide a canonical summary URL; cite the endpoint and key fields
        out.append(SourceItem(
            source_id=f"S510K{i}",
            title=f"openFDA 510(k) record: {k} — {dev}".strip(" —"),
            url=f"{url}?search=product_code:{product_code}&limit={limit}",
            publisher="FDA (openFDA)",
            doc_no=k or "",
            date=date or "",
            accessed=now_iso(),
            snippet=f"Sponsor: {sponsor}. Product code: {product_code}.",
            relevance="Potential predicate / comparable cleared device signals.",
            kind="510k",
        ))
    return out


def duckduckgo_search(query: str, limit: int = 5, site_filter: Optional[str] = None) -> List[Tuple[str, str, str]]:
    """
    Very lightweight HTML scrape. If blocked, returns [].
    Returns list of (title, url, snippet).
    """
    if not requests:
        return []
    q = query
    if site_filter:
        q = f"site:{site_filter} {query}"
    try:
        r = requests.get("https://duckduckgo.com/html/", params={"q": q}, timeout=20,
                         headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        html = r.text
    except Exception:
        return []

    # Crude parsing: find results links
    # DuckDuckGo HTML structure can change; keep best-effort and safe.
    results = []
    for m in re.finditer(r'<a rel="nofollow" class="result__a" href="([^"]+)">(.+?)</a>', html):
        url = m.group(1)
        title = re.sub("<.*?>", "", m.group(2))
        # snippet near the link (best effort)
        snippet = ""
        post = html[m.end(): m.end() + 500]
        sm = re.search(r'<a class="result__snippet".*?>(.*?)</a>|<div class="result__snippet".*?>(.*?)</div>', post, re.S)
        if sm:
            snippet = re.sub("<.*?>", "", (sm.group(1) or sm.group(2) or "")).strip()
        results.append((title.strip(), url.strip(), snippet))
        if len(results) >= limit:
            break
    return results


def retrieve_fda_guidance_and_standards(topic: str, limit_each: int = 5) -> List[SourceItem]:
    """
    Best-effort retrieval. If web retrieval disabled/unavailable, returns [].
    """
    if not can_web_retrieve():
        return []

    items: List[SourceItem] = []
    # Guidance
    guidance_hits = duckduckgo_search(topic + " FDA guidance", limit=limit_each, site_filter="fda.gov")
    for i, (title, url, snippet) in enumerate(guidance_hits, start=1):
        items.append(SourceItem(
            source_id=f"SG{i}",
            title=title or "FDA guidance (search result)",
            url=url,
            publisher="FDA",
            doc_no="",
            date="",
            accessed=now_iso(),
            snippet=snippet[:400],
            relevance="Potentially relevant FDA guidance document (verify on access).",
            kind="guidance",
        ))

    # Standards (FDA recognized consensus standards database)
    std_hits = duckduckgo_search(topic + " FDA recognized consensus standards", limit=limit_each, site_filter="fda.gov")
    for i, (title, url, snippet) in enumerate(std_hits, start=1):
        items.append(SourceItem(
            source_id=f"SS{i}",
            title=title or "FDA recognized standards (search result)",
            url=url,
            publisher="FDA",
            doc_no="",
            date="",
            accessed=now_iso(),
            snippet=snippet[:400],
            relevance="Potentially relevant standards listing (verify).",
            kind="standard",
        ))
    return items


def user_url_sources(urls_text: str) -> List[SourceItem]:
    urls = []
    for line in (urls_text or "").splitlines():
        line = line.strip()
        if line.startswith("http://") or line.startswith("https://"):
            urls.append(line)
    out = []
    for i, u in enumerate(urls, start=1):
        out.append(SourceItem(
            source_id=f"U{i}",
            title="User-provided reference URL",
            url=u,
            publisher="User provided",
            doc_no="",
            date="",
            accessed=now_iso(),
            snippet="",
            relevance="User supplied source for grounding.",
            kind="user_url",
        ))
    return out


def sources_to_markdown(sources: List[SourceItem], lang: str) -> str:
    if lang == "English":
        lines = ["## Source library", ""]
        for s in sources:
            lines += [
                f"- **[{s.source_id}] {s.title}**",
                f"  - Publisher: {s.publisher}",
                f"  - Doc No.: {s.doc_no or 'N/A'}",
                f"  - URL: {s.url or 'N/A'}",
                f"  - Date: {s.date or 'N/A'}",
                f"  - Accessed: {s.accessed}",
                f"  - Relevance: {s.relevance}",
            ]
            if s.snippet:
                lines.append(f"  - Snippet: {s.snippet}")
            lines.append("")
        return "\n".join(lines).strip() + "\n"
    else:
        lines = ["## 來源彙整（Source library）", ""]
        for s in sources:
            lines += [
                f"- **[{s.source_id}] {s.title}**",
                f"  - 發布者：{s.publisher}",
                f"  - 文件編號：{s.doc_no or 'N/A'}",
                f"  - 連結：{s.url or 'N/A'}",
                f"  - 日期：{s.date or 'N/A'}",
                f"  - 存取時間：{s.accessed}",
                f"  - 關聯性：{s.relevance}",
            ]
            if s.snippet:
                lines.append(f"  - 摘要：{s.snippet}")
            lines.append("")
        return "\n".join(lines).strip() + "\n"


# -----------------------------
# File ingestion
# -----------------------------

def extract_pdf_text(file_bytes: bytes, max_pages: Optional[int] = None) -> Tuple[str, List[Tuple[int, str]]]:
    """
    Returns (full_text, page_markers) where page_markers is list of (page_index_1based, page_text).
    """
    if PdfReader is None:
        raise RuntimeError("pypdf not installed; cannot read PDFs.")
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = reader.pages
    n = len(pages)
    if max_pages is not None:
        n = min(n, max_pages)
    full = []
    markers = []
    for i in range(n):
        try:
            txt = pages[i].extract_text() or ""
        except Exception:
            txt = ""
        txt = txt.strip()
        markers.append((i + 1, txt))
        full.append(f"\n\n[PAGE {i+1}]\n{txt}")
    return "\n".join(full).strip(), markers


def read_uploaded_file(uploaded) -> Tuple[str, Dict[str, Any]]:
    """
    Returns (text, meta)
    meta includes: filename, filetype, page_markers (if pdf)
    """
    if uploaded is None:
        return "", {}
    name = uploaded.name
    suffix = (name.split(".")[-1] or "").lower()
    data = uploaded.read()

    meta = {"filename": name, "filetype": suffix, "page_markers": []}

    if suffix == "pdf":
        txt, markers = extract_pdf_text(data, max_pages=None)
        meta["page_markers"] = markers
        return txt, meta

    # text-like
    try:
        txt = data.decode("utf-8", errors="replace")
    except Exception:
        txt = str(data)
    return txt, meta


# -----------------------------
# Keyword highlight helper
# -----------------------------

def highlight_keywords_md(md_text: str, keywords: List[str], color: str = "#ff7f50") -> str:
    """
    Wraps keywords in HTML span with inline style color.
    Uses word-boundary-ish approach; best-effort for CJK too.
    """
    if not md_text or not keywords:
        return md_text

    # Sort longer first to avoid partial overlaps
    kws = sorted({k.strip() for k in keywords if k.strip()}, key=len, reverse=True)
    if not kws:
        return md_text

    # Avoid replacing inside code fences
    parts = re.split(r"(```.*?```)", md_text, flags=re.S)
    out_parts = []

    for part in parts:
        if part.startswith("```") and part.endswith("```"):
            out_parts.append(part)
            continue
        tmp = part
        for kw in kws:
            # Case-insensitive for Latin; for CJK it won't matter
            pattern = re.compile(re.escape(kw), re.IGNORECASE)
            tmp = pattern.sub(lambda m: f'<span style="color:{color}; font-weight:700;">{m.group(0)}</span>', tmp)
        out_parts.append(tmp)
    return "".join(out_parts)


# -----------------------------
# UI Components
# -----------------------------

def init_session_state() -> None:
    st.session_state.setdefault("settings", {
        "theme": "Light",
        "ui_lang": "繁體中文",
        "painter_style": "Monet",
        "default_model": "gpt-4o-mini",
        "temperature": 0.2,
        "max_tokens": 12000,
    })
    st.session_state.setdefault("api_keys", {})
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("wow", {"global_status": "Ready"})
    st.session_state.setdefault("notes", {
        "raw": "",
        "organized": "",
        "effective": "",
        "prompt": "",
        "model": "",
        "saved_prompts": [],  # list of {title, prompt, model, ts}
        "magics": {},
    })
    st.session_state.setdefault("guidance", {
        "input_text": "",
        "input_meta": {},
        "output_lang": "繁體中文",
        "offline_mode": False,
        "enable_web": True,
        "product_code": "",
        "device_type": "",
        "topic_hint": "",
        "user_urls": "",
        "sources": [],
        "stepA_prompt": "",
        "stepA_model": GEMINI_GUIDANCE_MODELS_STEP_A[0],
        "stepA_out": "",
        "stepB_template": "",
        "stepB_prompt": "",
        "stepB_model": GEMINI_GUIDANCE_MODELS_STEP_B[0],
        "stepB_out": "",
        "stepC_prompt": "",
        "stepC_model": GEMINI_GUIDANCE_MODELS_STEP_C[0],
        "skill_md": "",
        "graph_json": "",
        "grounding_report": "",
        "bilingual_other_lang": "English",
        "bilingual_out": "",
    })
    st.session_state.setdefault("agent_studio", {
        "pipeline": [],  # list of steps: {agent_id, prompt, model, input, output}
    })


def render_sidebar() -> None:
    s = st.session_state["settings"]

    with st.sidebar:
        st.markdown(f"### {t('sidebar_settings')}")
        s["theme"] = st.selectbox(t("theme"), THEMES, index=THEMES.index(s.get("theme", "Light")))
        s["ui_lang"] = st.selectbox(t("language"), UI_LANGS, index=UI_LANGS.index(s.get("ui_lang", "English")))
        s["painter_style"] = st.selectbox(t("painter_style"), PAINTER_STYLES,
                                         index=PAINTER_STYLES.index(s.get("painter_style", "Monet")))
        cols = st.columns([1, 1])
        with cols[0]:
            if st.button(t("jackpot")):
                s["painter_style"] = random.choice(PAINTER_STYLES)
                st.session_state["wow"]["global_status"] = "Ready"
                st.rerun()
        with cols[1]:
            st.caption(f"v{APP_VERSION}")

        st.divider()
        s["default_model"] = st.selectbox(t("default_model"), ALL_MODELS,
                                         index=ALL_MODELS.index(s.get("default_model", "gpt-4o-mini")))
        s["temperature"] = st.slider(t("temperature"), 0.0, 1.0, float(s.get("temperature", 0.2)), 0.05)
        s["max_tokens"] = st.number_input(t("max_tokens"), min_value=256, max_value=120000,
                                          value=int(s.get("max_tokens", 12000)), step=256)

        st.divider()
        st.markdown(f"### {t('api_keys')}")
        for provider in ["openai", "gemini", "anthropic", "grok"]:
            env_name = ENV_KEYS[provider]
            env_val = os.getenv(env_name)
            if env_val:
                st.markdown(f"- **{provider.upper()}**: `{t('loaded_from_env')}`")
            else:
                key_field = st.text_input(f"{provider.upper()} — {t('enter_key')}", type="password",
                                          value=st.session_state["api_keys"].get(provider, ""))
                # store (but avoid storing empty)
                if key_field.strip():
                    st.session_state["api_keys"][provider] = key_field.strip()
                else:
                    # keep missing if user cleared
                    st.session_state["api_keys"].pop(provider, None)
                if st.button(f"{provider.upper()} — {t('clear_key')}", key=f"clear_{provider}"):
                    st.session_state["api_keys"].pop(provider, None)
                    st.rerun()

        st.divider()
        st.markdown(f"### {t('agents_catalog')}")
        if yaml is None:
            st.warning("PyYAML not installed; agents.yaml upload/editor disabled.")
        else:
            up = st.file_uploader(t("upload_agents_yaml"), type=["yaml", "yml"])
            if up is not None:
                try:
                    data = yaml.safe_load(up.read().decode("utf-8", errors="replace"))
                    if not (isinstance(data, dict) and "agents" in data and isinstance(data["agents"], dict)):
                        raise ValueError("Invalid agents.yaml format: missing top-level 'agents' dict.")
                    st.session_state["agents_cfg"] = data
                    st.success("Loaded agents catalog into session.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to load agents.yaml: {e}")


def wow_header() -> None:
    s = st.session_state["settings"]
    apply_style(s["theme"], s["painter_style"])

    # Global status display
    status = st.session_state.get("wow", {}).get("global_status", "Ready")
    st.markdown(
        f"""
        <div class="wow-card">
          <div style="display:flex; justify-content:space-between; align-items:center; gap:12px;">
            <div>
              <div style="font-size:20px; font-weight:800;">{APP_TITLE}</div>
              <div class="wow-muted">Theme: {s['theme']} · UI: {s['ui_lang']} · Style: {s['painter_style']}</div>
            </div>
            <div>{status_chip(status)}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def agent_runner_panel(
    *,
    tab_name: str,
    agent_id: str,
    default_input: str = "",
    fixed_models: Optional[List[str]] = None,
    allow_prompt_edit: bool = True,
    allow_input_edit: bool = True,
    key_prefix: str,
) -> Tuple[str, str]:
    """
    Generic agent runner: prompt + model selection + input + output editor.
    Returns (effective_output, last_status)
    """
    ensure_agents_catalog()
    agents = st.session_state["agents_cfg"]["agents"]
    cfg = agents.get(agent_id, {})

    st.session_state.setdefault("agent_state", {})
    state = st.session_state["agent_state"].setdefault(key_prefix, {
        "status": "Ready",
        "prompt": cfg.get("user_prompt", ""),
        "system_prompt": cfg.get("system_prompt", ""),
        "model": cfg.get("model", st.session_state["settings"]["default_model"]),
        "max_tokens": int(cfg.get("max_tokens", st.session_state["settings"]["max_tokens"])),
        "temperature": float(cfg.get("temperature", st.session_state["settings"]["temperature"])),
        "input": default_input or "",
        "output": "",
        "view": "Markdown",
        "last_duration_ms": 0,
        "last_tokens_in": 0,
        "last_tokens_out": 0,
        "last_provider": "",
        "last_ts": "",
    })

    # Sync default input only if user hasn't typed anything yet
    if default_input and not state.get("input"):
        state["input"] = default_input

    status = state["status"]
    st.markdown(
        f"""
        <div class="wow-card">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div style="font-weight:800;">Agent: <code>{agent_id}</code></div>
            <div>{status_chip(status)}</div>
          </div>
          <div class="wow-muted">Model: <code>{state['model']}</code> · {t('provider')}: <code>{provider_for_model(state['model'])}</code></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    cols = st.columns([1, 1, 1])
    with cols[0]:
        models = fixed_models or ALL_MODELS
        # ensure model exists in list
        if state["model"] not in models:
            models = models + [state["model"]]
        state["model"] = st.selectbox("Model", models, index=models.index(state["model"]), key=f"{key_prefix}_model")
    with cols[1]:
        state["max_tokens"] = st.number_input(t("max_tokens"), 256, 120000, int(state["max_tokens"]),
                                              step=256, key=f"{key_prefix}_maxtok")
    with cols[2]:
        state["temperature"] = st.slider(t("temperature"), 0.0, 1.0, float(state["temperature"]), 0.05,
                                         key=f"{key_prefix}_temp")

    if allow_prompt_edit:
        state["system_prompt"] = st.text_area(t("system_prompt"), value=state["system_prompt"], height=120,
                                              key=f"{key_prefix}_sysp")
        state["prompt"] = st.text_area(t("prompt"), value=state["prompt"], height=140,
                                       key=f"{key_prefix}_userp")
    else:
        st.caption("Prompt is fixed for this step.")
        st.code(state["system_prompt"])
        st.code(state["prompt"])

    if allow_input_edit:
        state["input"] = st.text_area(t("input"), value=state["input"], height=220, key=f"{key_prefix}_in")
    else:
        st.caption("Input is fixed for this step.")
        st.code(state["input"])

    run_cols = st.columns([1, 1, 2])
    with run_cols[0]:
        run_btn = st.button(t("run"), key=f"{key_prefix}_run")
    with run_cols[1]:
        state["view"] = st.radio(t("output_view"), [t("markdown"), t("text")], horizontal=True, key=f"{key_prefix}_view")
    with run_cols[2]:
        if state.get("last_ts"):
            st.caption(f"{t('duration')}: {state['last_duration_ms']/1000:.2f}s · {t('tokens_est')}: {state['last_tokens_in']+state['last_tokens_out']} · {state['last_ts']}")

    if run_btn:
        st.session_state["wow"]["global_status"] = "Running"
        state["status"] = "Running"
        st.rerun()

    # Execute if flagged running (two-phase to allow UI refresh)
    if state["status"] == "Running":
        start = time.time()
        provider = provider_for_model(state["model"])
        user_full = (state["prompt"] or "").strip() + "\n\n---\n\n" + (state["input"] or "").strip()

        tokens_in = approx_tokens((state["system_prompt"] or "") + "\n" + user_full)
        try:
            out = call_llm(
                model=state["model"],
                system_prompt=state["system_prompt"],
                user_prompt=user_full,
                max_tokens=int(state["max_tokens"]),
                temperature=float(state["temperature"]),
            )
            duration_ms = int((time.time() - start) * 1000)
            tokens_out = approx_tokens(out)

            state["output"] = out
            state["status"] = "Done"
            state["last_duration_ms"] = duration_ms
            state["last_tokens_in"] = tokens_in
            state["last_tokens_out"] = tokens_out
            state["last_provider"] = provider
            state["last_ts"] = now_iso()
            st.session_state["wow"]["global_status"] = "Ready"

            log_event(
                tab=tab_name,
                agent=agent_id,
                model=state["model"],
                provider=provider,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                duration_ms=duration_ms,
            )
        except Exception as e:
            state["status"] = "Error"
            st.session_state["wow"]["global_status"] = "Ready"
            st.error(f"{t('error')}: {e}")

    # Output editor
    st.markdown(f"#### {t('output')}")
    if state["view"] == t("markdown"):
        # show render + editable raw
        st.markdown(state["output"] or "")
        state["output"] = st.text_area("Editable output (Markdown)", value=state["output"], height=260,
                                       key=f"{key_prefix}_out_md")
    else:
        state["output"] = st.text_area("Editable output (Text)", value=state["output"], height=260,
                                       key=f"{key_prefix}_out_txt")

    return state["output"], state["status"]


# -----------------------------
# Dashboard
# -----------------------------

def render_dashboard() -> None:
    st.subheader(t("tabs_dashboard"))

    hist = st.session_state.get("history", [])
    total_runs = len(hist)
    uniq_tabs = len(set(h.get("tab") for h in hist))
    total_tokens = sum(int(h.get("tokens_total_est", 0)) for h in hist)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='wow-card'><div class='wow-kpi'>{total_runs}</div><div class='wow-muted'>Total runs</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='wow-card'><div class='wow-kpi'>{uniq_tabs}</div><div class='wow-muted'>Unique tabs</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='wow-card'><div class='wow-kpi'>{total_tokens}</div><div class='wow-muted'>Tokens (est.)</div></div>", unsafe_allow_html=True)

    # Latest run status wall
    if hist:
        last = max(hist, key=lambda x: x.get("ts", ""))
        tokens = int(last.get("tokens_total_est", 0))
        if tokens > 80000:
            level = "High"
        elif tokens > 40000:
            level = "Medium"
        else:
            level = "Normal"
        st.markdown(
            f"""
            <div class="wow-card">
              <div style="display:flex; justify-content:space-between; gap:12px; align-items:center;">
                <div>
                  <div style="font-weight:900;">WOW Status Wall</div>
                  <div class="wow-muted">Last run: <b>{last.get('tab')}</b> · Agent: <code>{last.get('agent')}</code></div>
                  <div class="wow-muted">Model: <code>{last.get('model')}</code> · Provider: <code>{last.get('provider')}</code></div>
                </div>
                <div style="text-align:right;">
                  <div style="font-size:22px; font-weight:900;">{level}</div>
                  <div class="wow-muted">{t('tokens_est')}: {tokens}</div>
                  <div class="wow-muted">{t('duration')}: {int(last.get('duration_ms',0))/1000:.2f}s</div>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    if not hist:
        st.info("No history yet.")
        return

    # Charts
    if pd is None or alt is None:
        st.warning("pandas/altair not installed; charts disabled.")
        st.dataframe(hist)
        return

    df = pd.DataFrame(hist)
    df["ts_dt"] = pd.to_datetime(df["ts"], errors="coerce")

    st.markdown("### Usage analytics")
    c1, c2 = st.columns(2)
    with c1:
        tab_counts = df.groupby("tab").size().reset_index(name="count")
        ch = alt.Chart(tab_counts).mark_bar().encode(
            x=alt.X("tab:N", sort="-y"),
            y="count:Q",
            tooltip=["tab:N", "count:Q"],
        ).properties(height=260)
        st.altair_chart(ch, use_container_width=True)

    with c2:
        model_counts = df.groupby("model").size().reset_index(name="count")
        ch = alt.Chart(model_counts).mark_bar().encode(
            x=alt.X("model:N", sort="-y"),
            y="count:Q",
            tooltip=["model:N", "count:Q"],
        ).properties(height=260)
        st.altair_chart(ch, use_container_width=True)

    st.markdown("### Model × Tab heatmap")
    heat = df.groupby(["tab", "model"]).size().reset_index(name="count")
    ch = alt.Chart(heat).mark_rect().encode(
        x=alt.X("model:N", sort=ALL_MODELS),
        y=alt.Y("tab:N", sort="-x"),
        color=alt.Color("count:Q", scale=alt.Scale(scheme="blues")),
        tooltip=["tab:N", "model:N", "count:Q"],
    ).properties(height=300)
    st.altair_chart(ch, use_container_width=True)

    st.markdown("### Token usage over time")
    line = alt.Chart(df).mark_line(point=True).encode(
        x="ts_dt:T",
        y="tokens_total_est:Q",
        color="tab:N",
        tooltip=["ts:N", "tab:N", "agent:N", "model:N", "tokens_total_est:Q", "duration_ms:Q"],
    ).properties(height=260)
    st.altair_chart(line, use_container_width=True)

    st.markdown(f"### {t('history')}")
    st.dataframe(df.sort_values("ts", ascending=False).head(50), use_container_width=True)


# -----------------------------
# TW Premarket (simplified but complete)
# -----------------------------

TW_APP_FIELDS = [
    "doc_no", "e_no", "apply_date",
    "case_type", "device_category", "case_kind", "origin", "product_class",
    "name_zh", "name_en", "indications", "spec_comp",
    "uniform_id", "firm_name", "firm_addr", "resp_name",
    "contact_name", "contact_tel", "contact_email",
    "manu_name", "manu_country", "manu_addr",
    "similar_info", "labeling_info", "tech_file_info",
    "preclinical_info", "clinical_info",
]

def tw_key(k: str) -> str:
    return f"tw_{k}"


def tw_init() -> None:
    for f in TW_APP_FIELDS:
        st.session_state.setdefault(tw_key(f), "")

    st.session_state.setdefault("tw_guidance_text", "")
    st.session_state.setdefault("tw_app_markdown", "")
    st.session_state.setdefault("tw_app_effective_md", "")


def compute_tw_completeness() -> float:
    required = ["e_no", "case_type", "product_class", "name_zh", "indications", "spec_comp", "firm_name", "manu_name"]
    filled = 0
    for r in required:
        if (st.session_state.get(tw_key(r), "") or "").strip():
            filled += 1
    return filled / max(1, len(required))


def build_tw_app_md() -> str:
    d = {f: st.session_state.get(tw_key(f), "") for f in TW_APP_FIELDS}
    md = f"""# TFDA 查驗登記申請草稿（Draft）

## 1. 基本資料
- 文件編號：{d['doc_no']}
- 案件編號（E No.）：{d['e_no']}
- 申請日期：{d['apply_date']}
- 案件類別：{d['case_type']}
- 器材類別：{d['device_category']}
- 分級（Class）：{d['product_class']}
- 來源：{d['origin']}

## 2. 器材資訊
- 中文名稱：{d['name_zh']}
- 英文名稱：{d['name_en']}
- 適應症/用途：{d['indications']}
- 規格/組成：{d['spec_comp']}

## 3. 申請/聯絡資訊
- 統一編號：{d['uniform_id']}
- 公司名稱：{d['firm_name']}
- 公司地址：{d['firm_addr']}
- 負責人：{d['resp_name']}
- 聯絡人：{d['contact_name']}
- 電話：{d['contact_tel']}
- Email：{d['contact_email']}

## 4. 製造廠資訊
- 製造廠名稱：{d['manu_name']}
- 國別：{d['manu_country']}
- 地址：{d['manu_addr']}

## 5. 其他摘要
- 類似品/等同性：{d['similar_info']}
- 標示/說明書：{d['labeling_info']}
- 技術文件摘要：{d['tech_file_info']}
- 臨床前資料摘要：{d['preclinical_info']}
- 臨床資料摘要：{d['clinical_info']}

---
（本文件為系統自動產生草稿，需人工校對。）
"""
    return md.strip() + "\n"


def render_tw_premarket() -> None:
    tw_init()
    st.subheader(t("tabs_tw"))

    comp = compute_tw_completeness()
    if comp >= 0.8:
        msg = "High completeness"
        status = "Done"
    elif comp >= 0.5:
        msg = "Medium completeness"
        status = "Needs review"
    else:
        msg = "Low completeness"
        status = "Blocked"

    st.markdown(
        f"""
        <div class="wow-card">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="font-weight:900;">WOW Application Completeness</div>
              <div class="wow-muted">{msg} · {comp*100:.0f}%</div>
            </div>
            <div>{status_chip(status)}</div>
          </div>
        </div>
        """, unsafe_allow_html=True
    )
    st.progress(comp)

    with st.expander("Application form", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("E No.", key=tw_key("e_no"))
            st.text_input("申請日期", key=tw_key("apply_date"))
            st.text_input("案件類別", key=tw_key("case_type"))
            st.text_input("器材類別", key=tw_key("device_category"))
            st.text_input("分級（Class）", key=tw_key("product_class"))
        with c2:
            st.text_input("中文名稱", key=tw_key("name_zh"))
            st.text_input("英文名稱", key=tw_key("name_en"))
            st.text_area("適應症/用途", key=tw_key("indications"), height=120)
            st.text_area("規格/組成", key=tw_key("spec_comp"), height=120)

        st.text_input("公司名稱", key=tw_key("firm_name"))
        st.text_input("製造廠名稱", key=tw_key("manu_name"))
        st.text_area("類似品/等同性摘要", key=tw_key("similar_info"), height=90)
        st.text_area("臨床前資料摘要", key=tw_key("preclinical_info"), height=90)
        st.text_area("臨床資料摘要", key=tw_key("clinical_info"), height=90)

    if st.button("生成申請書 Markdown 草稿"):
        md = build_tw_app_md()
        st.session_state["tw_app_markdown"] = md
        st.session_state["tw_app_effective_md"] = md

    if st.session_state.get("tw_app_markdown"):
        st.markdown("### Application draft (editable)")
        st.markdown(st.session_state["tw_app_effective_md"])
        st.session_state["tw_app_effective_md"] = st.text_area(
            "Editable markdown",
            value=st.session_state["tw_app_effective_md"],
            height=220
        )

    st.markdown("### Guidance input (optional)")
    g_up = st.file_uploader("Upload guidance (pdf/txt/md)", type=["pdf", "txt", "md"], key="tw_guid_up")
    if g_up is not None:
        txt, _meta = read_uploaded_file(g_up)
        st.session_state["tw_guidance_text"] = txt
    st.session_state["tw_guidance_text"] = st.text_area("Or paste guidance text", value=st.session_state["tw_guidance_text"], height=140)

    st.markdown("### Pre-screening review agent")
    default_in = (st.session_state.get("tw_app_effective_md", "") or "") + "\n\n---\n\n" + (st.session_state.get("tw_guidance_text", "") or "")
    agent_runner_panel(
        tab_name="TW Premarket",
        agent_id="tw_screen_review_agent",
        default_input=default_in,
        key_prefix="tw_screen",
    )

    st.markdown("### Application document helper")
    agent_runner_panel(
        tab_name="TW Premarket",
        agent_id="tw_app_doc_helper",
        default_input=st.session_state.get("tw_app_effective_md", ""),
        key_prefix="tw_helper",
    )


# -----------------------------
# 510(k) Intelligence
# -----------------------------

def render_510k_intel() -> None:
    st.subheader(t("tabs_510k_intel"))
    st.caption("Draft an intelligence memo; add product code if available to improve retrieval in the Guidance workspace.")

    c1, c2 = st.columns(2)
    with c1:
        device_name = st.text_input("Device name", key="k_device_name")
        sponsor = st.text_input("Sponsor / applicant", key="k_sponsor")
    with c2:
        product_code = st.text_input("Product code (optional)", key="k_product_code")
        k_number = st.text_input("K number (optional)", key="k_k_number")

    base = f"""Device name: {device_name}
Sponsor: {sponsor}
Product code: {product_code}
K number: {k_number}

Task:
Create a detailed 510(k) intelligence memo (approx 2000–3000 words if enough info), including: device overview, potential predicate clues, likely guidance and standards, key risks, and a compliance checklist.
If information is missing, clearly list questions and assumptions.
"""
    agent_runner_panel(
        tab_name="510(k) Intelligence",
        agent_id="fda_510k_intel_agent",
        default_input=base,
        key_prefix="k_intel",
    )


# -----------------------------
# PDF → Markdown
# -----------------------------

def render_pdf_to_md() -> None:
    st.subheader(t("tabs_pdf_md"))
    up = st.file_uploader("Upload PDF", type=["pdf"])
    raw = ""
    meta = {}
    if up is not None:
        try:
            raw, meta = read_uploaded_file(up)
            st.success(f"Loaded: {meta.get('filename')}")
        except Exception as e:
            st.error(f"{t('error')}: {e}")

    if raw:
        st.markdown("#### Extracted text preview")
        st.text_area("Preview", value=raw[:4000], height=180)

    agent_runner_panel(
        tab_name="PDF→Markdown",
        agent_id="pdf_to_markdown_agent",
        default_input=raw,
        key_prefix="pdfmd",
    )


# -----------------------------
# 510(k) Review Pipeline (simple 2-step)
# -----------------------------

def render_510k_pipeline() -> None:
    st.subheader(t("tabs_510k_pipeline"))

    st.markdown("### Step 1 — Structure submission text")
    st.session_state.setdefault("subm_raw", "")
    st.session_state.setdefault("subm_struct", "")
    st.session_state["subm_raw"] = st.text_area("Paste submission content", value=st.session_state["subm_raw"], height=220)

    # Use generic agent runner via a temporary inline agent config
    ensure_agents_catalog()
    if "submission_structurer_agent" not in st.session_state["agents_cfg"]["agents"]:
        st.session_state["agents_cfg"]["agents"]["submission_structurer_agent"] = {
            "model": st.session_state["settings"]["default_model"],
            "max_tokens": 12000,
            "temperature": 0.2,
            "system_prompt": "You are a 510(k) submission organizer. Produce structured Markdown with clear sections and checklists.",
            "user_prompt": "Rewrite the content into a well-structured Markdown submission outline with sections and bullet points. Do not invent missing data.",
        }
    out1, _ = agent_runner_panel(
        tab_name="510(k) Review Pipeline",
        agent_id="submission_structurer_agent",
        default_input=st.session_state["subm_raw"],
        key_prefix="pipe_struct",
    )
    st.session_state["subm_struct"] = out1

    st.markdown("### Step 2 — Draft review memo + checklist")
    st.session_state.setdefault("subm_checklist", "")
    st.session_state["subm_checklist"] = st.text_area("Paste or draft checklist (optional)", value=st.session_state["subm_checklist"], height=160)

    if "review_memo_agent" not in st.session_state["agents_cfg"]["agents"]:
        st.session_state["agents_cfg"]["agents"]["review_memo_agent"] = {
            "model": st.session_state["settings"]["default_model"],
            "max_tokens": 14000,
            "temperature": 0.2,
            "system_prompt": "You are an internal FDA reviewer. Be grounded, cautious, and actionable.",
            "user_prompt": "Create an internal review memo: summary, key issues, standards/guidance, and a checklist table with status and evidence needed.",
        }
    combined = (st.session_state.get("subm_struct", "") or "") + "\n\n---\n\nChecklist:\n" + (st.session_state.get("subm_checklist", "") or "")
    agent_runner_panel(
        tab_name="510(k) Review Pipeline",
        agent_id="review_memo_agent",
        default_input=combined,
        key_prefix="pipe_memo",
    )


# -----------------------------
# AI Note Keeper + Magics (6)
# -----------------------------

def render_notes() -> None:
    st.subheader(t("tabs_notes"))
    notes = st.session_state["notes"]

    st.markdown("### Step 1 — Paste note, transform to organized Markdown")
    notes["raw"] = st.text_area("Paste note (text/markdown)", value=notes.get("raw", ""), height=200)

    # Allow prompt/model selection for organizer
    ensure_agents_catalog()
    org_agent = st.session_state["agents_cfg"]["agents"].get("note_organizer_agent", DEFAULT_AGENTS_CATALOG["agents"]["note_organizer_agent"])
    notes.setdefault("prompt", org_agent.get("user_prompt", ""))
    notes.setdefault("model", org_agent.get("model", st.session_state["settings"]["default_model"]))

    c1, c2 = st.columns(2)
    with c1:
        notes["model"] = st.selectbox("Model", ALL_MODELS, index=ALL_MODELS.index(notes["model"]) if notes["model"] in ALL_MODELS else 0, key="note_model")
    with c2:
        if st.button("Organize note"):
            st.session_state["wow"]["global_status"] = "Running"
            start = time.time()
            sys_p = org_agent.get("system_prompt", "")
            user_p = notes["prompt"] or org_agent.get("user_prompt", "")
            try:
                out = call_llm(
                    model=notes["model"],
                    system_prompt=sys_p,
                    user_prompt=(user_p + "\n\n---\n\n" + notes["raw"]),
                    max_tokens=int(st.session_state["settings"]["max_tokens"]),
                    temperature=float(st.session_state["settings"]["temperature"]),
                )
                duration_ms = int((time.time() - start) * 1000)
                notes["organized"] = out
                notes["effective"] = out
                st.session_state["wow"]["global_status"] = "Ready"
                log_event("AI Note Keeper", "note_organizer_agent", notes["model"], provider_for_model(notes["model"]),
                          approx_tokens(sys_p + user_p + notes["raw"]), approx_tokens(out), duration_ms)
            except Exception as e:
                st.session_state["wow"]["global_status"] = "Ready"
                st.error(f"{t('error')}: {e}")

    notes["prompt"] = st.text_area("Organizer prompt (editable)", value=notes.get("prompt", ""), height=140)

    st.markdown("### Organized note (editable)")
    if notes.get("effective"):
        st.markdown(notes["effective"], unsafe_allow_html=True)
    notes["effective"] = st.text_area("Editable organized note (Markdown)", value=notes.get("effective", ""), height=260)

    # Keep prompt with note
    st.markdown("### Keep prompt with the note")
    keep_cols = st.columns([2, 2, 1])
    with keep_cols[0]:
        title = st.text_input("Saved prompt title", value="Note organizer preset", key="note_preset_title")
    with keep_cols[1]:
        if st.button("Save prompt preset"):
            notes["saved_prompts"].append({"title": title, "prompt": notes["prompt"], "model": notes["model"], "ts": now_iso()})
            st.success("Saved.")
    with keep_cols[2]:
        if st.button(t("reset"), key="note_reset"):
            st.session_state["notes"] = {
                "raw": "", "organized": "", "effective": "",
                "prompt": notes.get("prompt", ""), "model": notes.get("model", ""),
                "saved_prompts": notes.get("saved_prompts", []),
                "magics": {},
            }
            st.rerun()

    if notes.get("saved_prompts"):
        with st.expander("Saved prompt presets", expanded=False):
            for i, p in enumerate(notes["saved_prompts"]):
                st.write(f"{i+1}. **{p['title']}** — {p['model']} — {p['ts']}")
                if st.button(f"Load preset {i+1}", key=f"load_preset_{i}"):
                    notes["prompt"] = p["prompt"]
                    notes["model"] = p["model"]
                    st.rerun()

    st.divider()
    st.markdown("## AI Magics (6)")

    # Shared controls
    magic_model = st.selectbox("Magic model", ALL_MODELS, index=ALL_MODELS.index(st.session_state["settings"]["default_model"]))
    base_text = notes.get("effective", "")

    def run_magic(agent_name: str, sys_p: str, user_p: str, payload: str, key_out: str) -> None:
        start = time.time()
        try:
            out = call_llm(
                model=magic_model,
                system_prompt=sys_p,
                user_prompt=user_p + "\n\n---\n\n" + payload,
                max_tokens=int(st.session_state["settings"]["max_tokens"]),
                temperature=float(st.session_state["settings"]["temperature"]),
            )
            duration_ms = int((time.time() - start) * 1000)
            notes["magics"][key_out] = out
            log_event("AI Note Keeper", agent_name, magic_model, provider_for_model(magic_model),
                      approx_tokens(sys_p + user_p + payload), approx_tokens(out), duration_ms)
        except Exception as e:
            st.error(f"{t('error')}: {e}")

    # 1) AI Keywords (custom color)
    with st.expander("Magic 1 — AI Keywords (custom color)", expanded=False):
        kw = st.text_input("Keywords (comma-separated)", value="risk,sterilization,biocompatibility,510(k)")
        color = st.color_picker("Highlight color", value="#ff7f50")
        if st.button("Apply highlight"):
            kws = [x.strip() for x in kw.split(",") if x.strip()]
            notes["effective"] = highlight_keywords_md(notes["effective"], kws, color=color)
            st.success("Applied.")
        st.caption("This magic is deterministic (no LLM call).")

    # 2) AI Action Extractor
    with st.expander("Magic 2 — AI Action Extractor", expanded=False):
        prompt = st.text_area("Prompt", value="Extract action items into a Markdown table: task | owner(role) | priority | due date | evidence excerpt.", height=120, key="m2p")
        if st.button("Run Action Extractor"):
            run_magic("note_magic_action_extractor",
                      "You extract action items from notes. Be specific and concise.",
                      prompt, base_text, "m2_out")
        st.markdown(notes["magics"].get("m2_out", ""))

    # 3) AI Risk Flags
    with st.expander("Magic 3 — AI Risk Flags", expanded=False):
        prompt = st.text_area("Prompt", value="Identify regulatory risk flags. Output a table: risk | severity(L/M/H) | why | recommended mitigation | supporting excerpt.", height=120, key="m3p")
        if st.button("Run Risk Flags"):
            run_magic("note_magic_risk_flags",
                      "You identify regulatory risk flags without hallucination; cite excerpts.",
                      prompt, base_text, "m3_out")
        st.markdown(notes["magics"].get("m3_out", ""))

    # 4) AI Meeting Minutes Converter
    with st.expander("Magic 4 — AI Meeting Minutes Converter", expanded=False):
        prompt = st.text_area("Prompt", value="Convert to formal meeting minutes: attendees, agenda, discussion summary, decisions, next steps.", height=120, key="m4p")
        if st.button("Run Minutes Converter"):
            run_magic("note_magic_minutes",
                      "You produce formal meeting minutes in clean Markdown.",
                      prompt, base_text, "m4_out")
        st.markdown(notes["magics"].get("m4_out", ""))

    # 5) AI Compliance Crosswalk
    with st.expander("Magic 5 — AI Compliance Crosswalk", expanded=False):
        framework = st.multiselect("Frameworks", ["ISO 13485", "ISO 14971", "IEC 62304", "IEC 62366-1", "ISO 10993", "ISO 11135/11137/17665"], default=["ISO 14971", "ISO 13485"])
        prompt = st.text_area("Prompt", value="Create a crosswalk mapping note content to the selected frameworks. Output a table with gaps and suggested evidence.", height=120, key="m5p")
        if st.button("Run Crosswalk"):
            payload = "Frameworks: " + ", ".join(framework) + "\n\n" + base_text
            run_magic("note_magic_crosswalk",
                      "You map content to compliance frameworks and identify gaps. Do not invent evidence.",
                      prompt, payload, "m5_out")
        st.markdown(notes["magics"].get("m5_out", ""))

    # 6) AI Diff & Improve
    with st.expander("Magic 6 — AI Diff & Improve", expanded=False):
        original = st.text_area("Original note", value=notes.get("raw", ""), height=140)
        edited = st.text_area("Edited/organized note", value=notes.get("effective", ""), height=140)
        prompt = st.text_area("Prompt", value="Compare the original vs edited. Suggest clarity improvements while preserving meaning. Output: improvements list + rewritten version (optional).", height=120, key="m6p")
        if st.button("Run Diff & Improve"):
            payload = "ORIGINAL:\n" + original + "\n\nEDITED:\n" + edited
            run_magic("note_magic_diff_improve",
                      "You compare two notes and propose improvements without changing intent.",
                      prompt, payload, "m6_out")
        st.markdown(notes["magics"].get("m6_out", ""))

    st.divider()
    st.markdown("### Downloads")
    md = notes.get("effective", "")
    st.download_button("Download .md", data=md.encode("utf-8"), file_name="note.md", mime="text/markdown")
    st.download_button("Download .txt", data=re.sub(r"<[^>]+>", "", md).encode("utf-8"), file_name="note.txt", mime="text/plain")


# -----------------------------
# Guidance Reviewer & Research
# -----------------------------

DEFAULT_REPORT_TEMPLATE_TC = """# （預設模板）醫療器材指引審查報告與審查清單

## 一、審查目的與範圍
- 器材/主題：
- 輸入文件：
- 輸出語言：
- 重要假設與限制：

## 二、文件重點摘要（含引用）
（以條列方式列出文件關鍵要求、適用範圍、定義與例外。）

## 三、法規與標準彙整
### 3.1 FDA（含 guidance / 510(k) / recognized standards）
### 3.2 國際法規（EU MDR / IMDRF / 其他）
### 3.3 產業/共識標準（ISO/IEC/ASTM 等）

## 四、差異分析與落地建議
- 與輸入文件一致處：
- 潛在落差/風險：
- 建議補強資料：

## 五、審查清單（Checklist）
| 審查項目 | 具備文件/證據 | 來源引用 | 狀態（符合/不適用/待補） | 備註 |
|---|---|---|---|---|

## 六、結論與待釐清問題
- 審查結論：
- 待釐清問題清單：

## 附錄：來源彙整（Source library）
（列出所有引用來源與存取時間）
"""

DEFAULT_REPORT_TEMPLATE_EN = """# (Default Template) Medical Device Guidance Review Report & Checklist

## 1. Purpose and Scope
- Device/topic:
- Input document:
- Output language:
- Key assumptions/limitations:

## 2. Key document takeaways (with citations)
(Bullets capturing scope, definitions, requirements, exceptions.)

## 3. Regulations and standards landscape
### 3.1 FDA (guidance / 510(k) / recognized consensus standards)
### 3.2 International regulations (EU MDR / IMDRF / others)
### 3.3 Industry standards (ISO/IEC/ASTM etc.)

## 4. Gap analysis and practical recommendations
- Alignments:
- Potential gaps/risks:
- Recommended evidence to add:

## 5. Review checklist
| Item | Expected evidence | Source citation | Status (Meets/NA/Needs work) | Notes |
|---|---|---|---|---|

## 6. Conclusion and open questions
- Conclusion:
- Questions for sponsor:

## Appendix: Source library
(List all sources with access date)
"""


def render_guidance_workspace() -> None:
    g = st.session_state["guidance"]
    st.subheader(t("tabs_guidance"))

    # Controls
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        g["output_lang"] = st.selectbox(t("output_language"), ["繁體中文", "English"],
                                        index=0 if g.get("output_lang", "繁體中文") == "繁體中文" else 1)
    with c2:
        g["offline_mode"] = st.checkbox(t("offline_mode"), value=bool(g.get("offline_mode", False)))
    with c3:
        g["enable_web"] = st.checkbox(t("enable_web_retrieval"), value=bool(g.get("enable_web", True)),
                                      disabled=bool(g.get("offline_mode", False)))

    st.markdown("### " + t("upload_or_paste"))
    up = st.file_uploader(t("file_upload"), type=["txt", "md", "pdf"], key="guid_up")
    if up is not None:
        try:
            txt, meta = read_uploaded_file(up)
            g["input_text"] = txt
            g["input_meta"] = meta
            st.success(f"Loaded: {meta.get('filename')}")
        except Exception as e:
            st.error(f"{t('error')}: {e}")

    g["input_text"] = st.text_area(t("paste_here"), value=g.get("input_text", ""), height=220)

    st.markdown("### Optional hints (improves retrieval quality)")
    c1, c2, c3 = st.columns(3)
    with c1:
        g["product_code"] = st.text_input("FDA product code (optional)", value=g.get("product_code", ""))
    with c2:
        g["device_type"] = st.text_input("Device type / category", value=g.get("device_type", ""))
    with c3:
        g["topic_hint"] = st.text_input("Topic hint (e.g., sterilization / biocompatibility / SaMD)", value=g.get("topic_hint", ""))

    g["user_urls"] = st.text_area("User-provided reference URLs (one per line, optional)", value=g.get("user_urls", ""), height=100)

    # Retrieval
    st.markdown("### Retrieval & sources")
    if st.button("Run retrieval"):
        sources: List[SourceItem] = []
        # User URLs always included
        sources.extend(user_url_sources(g.get("user_urls", "")))

        if not g.get("offline_mode", False):
            # openFDA 510k by product code
            if g.get("product_code", "").strip():
                sources.extend(openfda_510k_by_product_code(g["product_code"].strip(), limit=5))
            # guidance/standards best effort
            topic = (g.get("topic_hint") or g.get("device_type") or "medical device").strip()
            sources.extend(retrieve_fda_guidance_and_standards(topic, limit_each=5))

        g["sources"] = [s.__dict__ for s in sources]
        st.success(f"Sources collected: {len(sources)}")

    sources_objs = [SourceItem(**x) for x in (g.get("sources", []) or [])]
    st.markdown(sources_to_markdown(sources_objs, g["output_lang"]) if sources_objs else "_No sources yet._")

    # Build input package for Step A/B/C
    filename = (g.get("input_meta", {}) or {}).get("filename", "")
    page_markers = (g.get("input_meta", {}) or {}).get("page_markers", []) or []
    page_citation_hint = ""
    if page_markers:
        page_citation_hint = "PDF page markers exist: cite as [G-p12] etc."
    else:
        page_citation_hint = "No PDF page markers: cite as [G] for uploaded guidance."

    guidance_block = f"""[UPLOADED_GUIDANCE]
Filename: {filename or "N/A"}
{page_citation_hint}

Content:
{g.get("input_text","")}
"""

    sources_block = sources_to_markdown(sources_objs, g["output_lang"]) if sources_objs else ""

    # ---------------- Step A ----------------
    st.markdown("## " + t("step_a"))
    g["stepA_model"] = st.selectbox("Model (Step A)", GEMINI_GUIDANCE_MODELS_STEP_A,
                                   index=GEMINI_GUIDANCE_MODELS_STEP_A.index(g.get("stepA_model", GEMINI_GUIDANCE_MODELS_STEP_A[0])))
    default_stepA_prompt_en = """You will produce a 2000–3000 word Markdown report grounded in:
(1) the uploaded guidance content, and
(2) the provided external sources list.

Hard rules:
- Every major claim must include citations like [G-p12] for uploaded guidance pages or [SG1]/[SS2]/[S510K1] for external sources.
- If external retrieval is missing/unreliable, explicitly state limitations and provide a verification checklist.
- Include: executive summary, document synopsis with key excerpts, FDA landscape, international alignment, standards & testing implications, compliance checklist table, gaps/questions, appendices with source library.

Write in the specified output language.
"""
    default_stepA_prompt_tc = """請以 2000–3000 字 Markdown 生成「具引用之法規研究報告」，並以：
(1) 使用者上傳之指引內容、以及
(2) 外部來源清單
作為落地（grounding）依據。

硬性規則：
- 每個重大主張必須附引用，例如：上傳 PDF 以 [G-p12] 標示頁碼；外部來源以 [SG1]/[SS2]/[S510K1] 等標示。
- 若外部檢索不足或不可用，必須明確揭露限制並提供「待查證清單」。
- 必含：執行摘要、文件重點（含引用）、FDA 情境（guidance/510k/recognized standards）、國際法規對照、標準/測試意涵、審查清單表、落差與待釐清問題、附錄來源彙整。

請用指定輸出語言完整撰寫。
"""
    if not g.get("stepA_prompt"):
        g["stepA_prompt"] = default_stepA_prompt_tc if g["output_lang"] == "繁體中文" else default_stepA_prompt_en
    g["stepA_prompt"] = st.text_area("Prompt (Step A, editable)", value=g.get("stepA_prompt", ""), height=200)

    if st.button("Run Step A"):
        st.session_state["wow"]["global_status"] = "Running"
        start = time.time()
        sys_p = st.session_state["agents_cfg"]["agents"]["guidance_analyze_research_agent"]["system_prompt"]
        user_p = g["stepA_prompt"]
        payload = f"""Output language: {g['output_lang']}

{guidance_block}

[EXTERNAL_SOURCES]
{sources_block}
"""
        try:
            out = call_llm(
                model=g["stepA_model"],
                system_prompt=sys_p,
                user_prompt=user_p + "\n\n---\n\n" + payload,
                max_tokens=int(st.session_state["settings"]["max_tokens"]),
                temperature=float(st.session_state["settings"]["temperature"]),
            )
            duration_ms = int((time.time() - start) * 1000)
            g["stepA_out"] = out
            st.session_state["wow"]["global_status"] = "Ready"
            log_event("Guidance Reviewer", "guidance_analyze_research_agent", g["stepA_model"], provider_for_model(g["stepA_model"]),
                      approx_tokens(sys_p + user_p + payload), approx_tokens(out), duration_ms)
        except Exception as e:
            st.session_state["wow"]["global_status"] = "Ready"
            st.error(f"{t('error')}: {e}")

    st.markdown("### Step A output (editable)")
    if g.get("stepA_out"):
        st.markdown(g["stepA_out"], unsafe_allow_html=True)
    g["stepA_out"] = st.text_area("Editable Step A Markdown", value=g.get("stepA_out", ""), height=260)

    st.download_button("Download Step A (.md)", data=(g.get("stepA_out", "")).encode("utf-8"),
                       file_name="comprehensive_report.md", mime="text/markdown")
    st.download_button("Download Step A (.txt)", data=re.sub(r"<[^>]+>", "", (g.get("stepA_out",""))).encode("utf-8"),
                       file_name="comprehensive_report.txt", mime="text/plain")

    # ---------------- Step B ----------------
    st.markdown("## " + t("step_b"))
    g["stepB_model"] = st.selectbox("Model (Step B)", GEMINI_GUIDANCE_MODELS_STEP_B,
                                   index=GEMINI_GUIDANCE_MODELS_STEP_B.index(g.get("stepB_model", GEMINI_GUIDANCE_MODELS_STEP_B[0])))

    templ_choice = st.radio(t("template"), [t("use_default_template"), t("upload_template")], horizontal=True)
    if templ_choice == t("use_default_template"):
        g["stepB_template"] = DEFAULT_REPORT_TEMPLATE_TC if g["output_lang"] == "繁體中文" else DEFAULT_REPORT_TEMPLATE_EN
        st.code(g["stepB_template"], language="markdown")
    else:
        t_up = st.file_uploader(t("upload_template"), type=["md", "txt"], key="templ_up")
        if t_up is not None:
            txt, _ = read_uploaded_file(t_up)
            g["stepB_template"] = txt
        g["stepB_template"] = st.text_area("Template text", value=g.get("stepB_template", ""), height=200)

    if not g.get("stepB_prompt"):
        g["stepB_prompt"] = "Fit the report into the template. Preserve citations. Do not delete key compliance content."
    g["stepB_prompt"] = st.text_area("Prompt (Step B, editable)", value=g.get("stepB_prompt", ""), height=120)

    if st.button("Run Step B"):
        if not (g.get("stepA_out", "").strip() and g.get("stepB_template", "").strip()):
            st.error("Step A output and template are required.")
        else:
            st.session_state["wow"]["global_status"] = "Running"
            start = time.time()
            sys_p = st.session_state["agents_cfg"]["agents"]["template_report_agent"]["system_prompt"]
            user_p = g["stepB_prompt"]
            payload = f"""Output language: {g['output_lang']}

[TEMPLATE]
{g['stepB_template']}

[INPUT_REPORT]
{g['stepA_out']}
"""
            try:
                out = call_llm(
                    model=g["stepB_model"],
                    system_prompt=sys_p,
                    user_prompt=user_p + "\n\n---\n\n" + payload,
                    max_tokens=int(st.session_state["settings"]["max_tokens"]),
                    temperature=float(st.session_state["settings"]["temperature"]),
                )
                duration_ms = int((time.time() - start) * 1000)
                g["stepB_out"] = out
                st.session_state["wow"]["global_status"] = "Ready"
                log_event("Guidance Reviewer", "template_report_agent", g["stepB_model"], provider_for_model(g["stepB_model"]),
                          approx_tokens(sys_p + user_p + payload), approx_tokens(out), duration_ms)
            except Exception as e:
                st.session_state["wow"]["global_status"] = "Ready"
                st.error(f"{t('error')}: {e}")

    st.markdown("### Step B output (editable)")
    if g.get("stepB_out"):
        st.markdown(g["stepB_out"], unsafe_allow_html=True)
    g["stepB_out"] = st.text_area("Editable Step B Markdown", value=g.get("stepB_out", ""), height=260)

    st.download_button("Download Step B (.md)", data=(g.get("stepB_out", "")).encode("utf-8"),
                       file_name="template_report.md", mime="text/markdown")
    st.download_button("Download Step B (.txt)", data=re.sub(r"<[^>]+>", "", (g.get("stepB_out",""))).encode("utf-8"),
                       file_name="template_report.txt", mime="text/plain")

    # ---------------- Step C ----------------
    st.markdown("## " + t("step_c"))
    g["stepC_model"] = st.selectbox("Model (Step C)", GEMINI_GUIDANCE_MODELS_STEP_C,
                                   index=GEMINI_GUIDANCE_MODELS_STEP_C.index(g.get("stepC_model", GEMINI_GUIDANCE_MODELS_STEP_C[0])))

    if not g.get("stepC_prompt"):
        g["stepC_prompt"] = (
            "Use skill-creator style. Create a SKILL.md with YAML frontmatter (name, description). "
            "Write in the specified output language. Include 3 WOW behaviors: Auto-Crosswalk Builder, "
            "Citation Quality Gate, Checklist-to-Actions Converter. Provide output templates and examples."
        )
    g["stepC_prompt"] = st.text_area("Prompt (Step C, editable)", value=g.get("stepC_prompt", ""), height=140)

    if st.button("Run Step C (skill.md)"):
        if not g.get("stepB_out", "").strip():
            st.error("Step B output is required (template-based report).")
        else:
            st.session_state["wow"]["global_status"] = "Running"
            start = time.time()
            sys_p = st.session_state["agents_cfg"]["agents"]["skill_md_generator_agent"]["system_prompt"]
            user_p = g["stepC_prompt"]
            payload = f"""Output language: {g['output_lang']}

[UPLOADED_GUIDANCE]
{guidance_block}

[COMPREHENSIVE_REPORT_STEP_A]
{g.get('stepA_out','')}

[TEMPLATE_BASED_REPORT_STEP_B]
{g.get('stepB_out','')}
"""
            try:
                out = call_llm(
                    model=g["stepC_model"],
                    system_prompt=sys_p,
                    user_prompt=user_p + "\n\n---\n\n" + payload,
                    max_tokens=int(st.session_state["settings"]["max_tokens"]),
                    temperature=float(st.session_state["settings"]["temperature"]),
                )
                duration_ms = int((time.time() - start) * 1000)
                g["skill_md"] = out
                st.session_state["wow"]["global_status"] = "Ready"
                log_event("Guidance Reviewer", "skill_md_generator_agent", g["stepC_model"], provider_for_model(g["stepC_model"]),
                          approx_tokens(sys_p + user_p + payload), approx_tokens(out), duration_ms)
            except Exception as e:
                st.session_state["wow"]["global_status"] = "Ready"
                st.error(f"{t('error')}: {e}")

    st.markdown("### skill.md (editable)")
    if g.get("skill_md"):
        st.markdown(g["skill_md"], unsafe_allow_html=True)
    g["skill_md"] = st.text_area("Editable skill.md", value=g.get("skill_md", ""), height=260)
    st.download_button("Download skill.md", data=(g.get("skill_md", "")).encode("utf-8"),
                       file_name="skill.md", mime="text/markdown")

    # WOW AI Features
    st.divider()
    st.markdown("## WOW AI Features")

    # 1) Knowledge graph
    st.markdown("### " + t("knowledge_graph"))
    graph_input = g.get("stepA_out") or g.get("stepB_out") or g.get("input_text", "")
    if st.button(t("build_graph")):
        st.session_state["wow"]["global_status"] = "Running"
        start = time.time()
        sys_p = st.session_state["agents_cfg"]["agents"]["knowledge_graph_agent"]["system_prompt"]
        user_p = st.session_state["agents_cfg"]["agents"]["knowledge_graph_agent"]["user_prompt"]
        payload = graph_input
        try:
            out = call_llm(
                model=st.session_state["agents_cfg"]["agents"]["knowledge_graph_agent"]["model"],
                system_prompt=sys_p,
                user_prompt=user_p + "\n\n---\n\n" + payload,
                max_tokens=8000,
                temperature=0.2,
            )
            duration_ms = int((time.time() - start) * 1000)
            g["graph_json"] = out
            st.session_state["wow"]["global_status"] = "Ready"
            log_event("Guidance Reviewer", "knowledge_graph_agent",
                      st.session_state["agents_cfg"]["agents"]["knowledge_graph_agent"]["model"],
                      provider_for_model(st.session_state["agents_cfg"]["agents"]["knowledge_graph_agent"]["model"]),
                      approx_tokens(sys_p + user_p + payload), approx_tokens(out), duration_ms)
        except Exception as e:
            st.session_state["wow"]["global_status"] = "Ready"
            st.error(f"{t('error')}: {e}")

    g["graph_json"] = st.text_area("Graph JSON (editable)", value=g.get("graph_json", ""), height=200)
    if g.get("graph_json"):
        # Render if graphviz available
        try:
            data = json.loads(g["graph_json"])
            nodes = data.get("nodes", [])
            edges = data.get("edges", [])
            st.caption(f"Nodes: {len(nodes)} · Edges: {len(edges)}")
            if graphviz is not None and edges:
                dot = graphviz.Digraph()
                # add nodes (limit to keep UI responsive)
                node_set = set()
                for e in edges[:80]:
                    node_set.add(e.get("source", ""))
                    node_set.add(e.get("target", ""))
                for n in list(node_set)[:60]:
                    if n:
                        dot.node(n[:60])
                for e in edges[:80]:
                    s0 = (e.get("source", "") or "")[:60]
                    t0 = (e.get("target", "") or "")[:60]
                    rel = (e.get("relation", "") or "")[:30]
                    if s0 and t0:
                        dot.edge(s0, t0, label=rel)
                st.graphviz_chart(dot)
            else:
                st.dataframe(edges[:200] if isinstance(edges, list) else [])
        except Exception:
            st.info("Graph JSON is not valid JSON yet. You can edit and retry rendering.")

    # 2) Grounding inspector
    st.markdown("### " + t("grounding_inspector"))
    inspect_input = g.get("stepA_out") or ""
    if st.button(t("inspect")):
        if not inspect_input.strip():
            st.error("Need Step A output for grounding inspection.")
        else:
            st.session_state["wow"]["global_status"] = "Running"
            start = time.time()
            agent = st.session_state["agents_cfg"]["agents"]["grounding_inspector_agent"]
            sys_p = agent["system_prompt"]
            user_p = agent["user_prompt"]
            payload = "Output language: " + g["output_lang"] + "\n\n" + inspect_input
            try:
                out = call_llm(
                    model=agent["model"],
                    system_prompt=sys_p,
                    user_prompt=user_p + "\n\n---\n\n" + payload,
                    max_tokens=8000,
                    temperature=0.2,
                )
                duration_ms = int((time.time() - start) * 1000)
                g["grounding_report"] = out
                st.session_state["wow"]["global_status"] = "Ready"
                log_event("Guidance Reviewer", "grounding_inspector_agent", agent["model"], provider_for_model(agent["model"]),
                          approx_tokens(sys_p + user_p + payload), approx_tokens(out), duration_ms)
            except Exception as e:
                st.session_state["wow"]["global_status"] = "Ready"
                st.error(f"{t('error')}: {e}")

    st.markdown(g.get("grounding_report", ""), unsafe_allow_html=True)

    # 3) Bilingual renderer
    st.markdown("### " + t("bilingual"))
    other_lang = "English" if g["output_lang"] == "繁體中文" else "繁體中文"
    g["bilingual_other_lang"] = other_lang
    bilingual_input = g.get("stepB_out") or g.get("stepA_out") or ""
    if st.button(t("render_bilingual")):
        if not bilingual_input.strip():
            st.error("Need Step A or Step B output to render bilingual view.")
        else:
            st.session_state["wow"]["global_status"] = "Running"
            start = time.time()
            agent = st.session_state["agents_cfg"]["agents"]["bilingual_renderer_agent"]
            sys_p = agent["system_prompt"]
            user_p = agent["user_prompt"]
            payload = f"""Primary language: {g['output_lang']}
Secondary language: {other_lang}

Content:
{bilingual_input}
"""
            try:
                out = call_llm(
                    model=agent["model"],
                    system_prompt=sys_p,
                    user_prompt=user_p + "\n\n---\n\n" + payload,
                    max_tokens=12000,
                    temperature=0.2,
                )
                duration_ms = int((time.time() - start) * 1000)
                g["bilingual_out"] = out
                st.session_state["wow"]["global_status"] = "Ready"
                log_event("Guidance Reviewer", "bilingual_renderer_agent", agent["model"], provider_for_model(agent["model"]),
                          approx_tokens(sys_p + user_p + payload), approx_tokens(out), duration_ms)
            except Exception as e:
                st.session_state["wow"]["global_status"] = "Ready"
                st.error(f"{t('error')}: {e}")

    if g.get("bilingual_out"):
        colA, colB = st.columns(2)
        with colA:
            st.markdown(f"#### {g['output_lang']}")
            st.markdown(bilingual_input, unsafe_allow_html=True)
        with colB:
            st.markdown(f"#### {other_lang}")
            st.markdown(g["bilingual_out"], unsafe_allow_html=True)


# -----------------------------
# Agents Config Studio
# -----------------------------

def render_agents_studio() -> None:
    st.subheader(t("tabs_agents"))
    ensure_agents_catalog()

    if yaml is None:
        st.warning("PyYAML not installed.")
        st.json(st.session_state["agents_cfg"])
        return

    agents = st.session_state["agents_cfg"].get("agents", {})
    st.markdown(f"### Agents overview ({len(agents)})")
    st.dataframe(
        [{"agent_id": k, "model": v.get("model"), "max_tokens": v.get("max_tokens"), "temperature": v.get("temperature")} for k, v in agents.items()],
        use_container_width=True
    )

    st.markdown("### Edit raw YAML (session only)")
    raw = yaml.safe_dump(st.session_state["agents_cfg"], sort_keys=False, allow_unicode=True)
    edited = st.text_area("agents.yaml", value=raw, height=360)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Apply YAML to session"):
            try:
                data = yaml.safe_load(edited)
                if not (isinstance(data, dict) and "agents" in data and isinstance(data["agents"], dict)):
                    raise ValueError("Invalid format: requires top-level 'agents' dict.")
                st.session_state["agents_cfg"] = data
                st.success("Applied.")
                st.rerun()
            except Exception as e:
                st.error(f"{t('error')}: {e}")
    with c2:
        st.download_button("Download agents.yaml", data=edited.encode("utf-8"), file_name="agents.yaml", mime="text/yaml")


# -----------------------------
# Main
# -----------------------------

def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    init_session_state()
    ensure_agents_catalog()

    render_sidebar()
    wow_header()

    tabs = st.tabs([
        t("tabs_dashboard"),
        t("tabs_tw"),
        t("tabs_510k_intel"),
        t("tabs_pdf_md"),
        t("tabs_510k_pipeline"),
        t("tabs_notes"),
        t("tabs_guidance"),
        t("tabs_agents"),
    ])

    with tabs[0]:
        render_dashboard()
    with tabs[1]:
        render_tw_premarket()
    with tabs[2]:
        render_510k_intel()
    with tabs[3]:
        render_pdf_to_md()
    with tabs[4]:
        render_510k_pipeline()
    with tabs[5]:
        render_notes()
    with tabs[6]:
        render_guidance_workspace()
    with tabs[7]:
        render_agents_studio()


if __name__ == "__main__":
    main()
