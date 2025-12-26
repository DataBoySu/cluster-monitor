import os
import re
import argparse
from llama_cpp import Llama

# Map language codes to full English names for the system prompt
LANG_MAP = {
    "de": "German",
    "fr": "French",
    "es": "Spanish",
    "ja": "Japanese",
    "zh": "Simplified Chinese",
    "ru": "Russian",
    "pt": "Portuguese",
    "ko": "Korean",
    "hi": "Hindi"
}

parser = argparse.ArgumentParser()
parser.add_argument("--lang", type=str, required=True, help="Target language code (e.g., de, fr)")
args = parser.parse_args()

target_lang_name = LANG_MAP.get(args.lang, "English")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README_PATH = os.path.join(BASE_DIR, "README.md")
OUTPUT_DIR = os.path.join(BASE_DIR, "locales")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, f"README.{args.lang}.md")
MODEL_PATH = os.path.join(BASE_DIR, "models", "aya-expanse-8b-q4_k_s.gguf")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set n_ctx to 6144 as a safe middle ground for 8B model on 7GB RAM.
# Added n_threads=2 to match GitHub Action runner vCPUs.
llm = Llama(model_path=MODEL_PATH, n_ctx=6144, n_threads=2, verbose=False)

with open(README_PATH, "r", encoding="utf-8") as f:
    text_to_translate = f.read()

# Aya Expanse uses a specific header format for system/user/chatbot turns
prompt = f"""<|START_OF_TURN_TOKEN|><|SYSTEM_TOKEN|>
You are a professional technical translator specializing in software documentation (GitHub READMEs).
Translate the provided README into professional developer-level {target_lang_name}.
Maintain a formal tone and preserve technical terminology (e.g., GPU, CLI, vCPU).
Keep all Markdown/HTML syntax exactly as is.
CRITICAL RULES:
1. **Badges**: Do NOT translate badge alt text or URLs (e.g., keep `!License` exactly as is).
2. **Emojis**: Preserve all emojis exactly as they appear in the source.
3. **Navigation**: Do NOT strip, translate, or modify the top-level HTML navigation bar (<div align="center">...</div>) or the logo.
4. **Output**: ONLY output the translated {target_lang_name} text. No talk, just translation.
5. **Technical Consistency**: For languages like Hindi or Japanese, do not translate standard English UI/UX terms that are commonly used in their English form by developers (e.g., keep 'Dashboard', 'Wrapper', 'Throttling' if it is standard practice, or provide the translation followed by the English term in parentheses).
6. **Contextual Meaning**: Treat 'Enforcement' as 'Policy application/restriction' (e.g., Spanish: 'Ejecución/Restricción', not 'Enfoque'). Treat 'Headless' as a server without a display (e.g., do not translate literally to 'sin cabeza').
7. **Navigation Integrity**: Inside the <div align="center"> block, do NOT translate the names of the languages (e.g., 'English' must stay 'English', 'Deutsch' must stay 'Deutsch').
Do not add new information, do not summarize, and do not include any conversational filler or "thinking" process.<|END_OF_TURN_TOKEN|>
<|START_OF_TURN_TOKEN|><|USER_TOKEN|>
{text_to_translate}<|END_OF_TURN_TOKEN|>
<|START_OF_TURN_TOKEN|><|CHATBOT_TOKEN|>
"""
# Do not translate translate badges. Keep them as it is.
# IMPORTANT: Do not strip or modify the top-level HTML tags (like <div> or <img>) at the beginning of the file.
# ONLY output the translated {target_lang_name} text. No talk, just translation.
# max_tokens must be less than n_ctx (6144). 4096 leaves ~2000 tokens for README input.
response = llm(
    prompt, 
    max_tokens=6144, 
    temperature=0, # Set to 0 for maximum determinism in translation
    stop=["<|END_OF_TURN_TOKEN|>", "<|START_OF_TURN_TOKEN|>"]
)

translated_content = response['choices'][0]['text'].strip()

# 1. CLEANUP: Remove markdown code fences if the LLM included them
if translated_content.startswith("```"):
    lines = translated_content.splitlines()
    if lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]
    translated_content = "\n".join(lines).strip()

# 2. FIX PATHS: Handle relative paths for files in /locales/
# First, remove "locales/" if the LLM hallucinated it into the path
translated_content = re.sub(r'(\[.*?\]\()locales/', r'\1', translated_content)
translated_content = re.sub(r'((?:src|href)=")locales/', r'\1', translated_content)

# Then, prepend ../ to relative paths (ignoring external links, absolute paths, or anchors)
# This targets Markdown links/images text and HTML src="path"/href="path"
translated_content = re.sub(r'(\[.*?\]\()(?!(?:http|/|#|\.\./))', r'\1../', translated_content)
translated_content = re.sub(r'((?:src|href)=")(?!(?:http|/|#|\.\./))', r'\1../', translated_content)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(translated_content)

print(f"Translation to {target_lang_name} complete: {OUTPUT_PATH}")