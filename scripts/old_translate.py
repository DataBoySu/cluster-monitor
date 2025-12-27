import os
import re
import argparse
from llama_cpp import Llama

LANG_MAP = {
    "de": "German", 
    "fr": "French", 
    "es": "Spanish",
    "ja": "Japanese", 
    "zh": "Chinese(Simplified)",
    "ru": "Russian", 
    "pt": "Portuguese", 
    "ko": "Korean",
    "hi": "Hindi",
}

parser = argparse.ArgumentParser()
parser.add_argument("--lang", type=str, required=True)
args = parser.parse_args()
target_lang_name = LANG_MAP.get(args.lang, "English")

# Path Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README_PATH = os.path.join(BASE_DIR, "README.md")
OUTPUT_DIR = os.path.join(BASE_DIR, "locales")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, f"README.{args.lang}.md")
MODEL_PATH = os.path.join(BASE_DIR, "models", "aya-expanse-8b-q4_k_s.gguf")

os.makedirs(OUTPUT_DIR, exist_ok=True)
llm = Llama(model_path=MODEL_PATH, n_ctx=6144, n_threads=2, verbose=False)

with open(README_PATH, "r", encoding="utf-8") as f:
    original_text = f.read()

# --- PRE-PROCESSING: Protect Sensitive Blocks ---
# We replace complex blocks with placeholders so the LLM cannot mangle them.
protected_blocks = []

# Change this in your translate.py
def protect_match(match):
    # Use something clearly non-linguistic
    placeholder = f"[[PB_{len(protected_blocks)}]]" 
    protected_blocks.append(match.group(0))
    return placeholder

text_to_translate = original_text

# Refined Prompt for CJK and Technical Nuance
prompt = f"""<|START_OF_TURN_TOKEN|><|SYSTEM_TOKEN|>
You are a professional technical translator. Translate the provided README into professional developer-level {target_lang_name}.
CRITICAL RULES:
1. **Badges**: Do NOT translate Markdown image syntax. Specifically, do NOT translate text inside square brackets ![...] or parentheses (...) for badge lines (e.g., license, python).
2. **Navigation**: Do NOT modify the top-level HTML navigation bar (`<div align="center">`).
3. **Context**: Treat 'Enforcement' as 'System policy restriction' and 'Headless' as 'server without GUI'.
4. **Technical Integrity**: Preserve industry-standard terms (GPU, CLI, VRAM, SSH, Docker, API, CUDA) exactly as they appear in English.
5. **Formatting**: Preserve all emojis and HTML/Markdown tags exactly.
6. **No Talk**: Output ONLY the translated text. Do not include markdown code fences (```) around the entire output.<|END_OF_TURN_TOKEN|> 
7. **Context**: 
   - 'Enforcement' = Policy restriction/application (JA: 制限/強制, ZH: 强制执行).
   - 'Headless' = Servers without a display (JA: ヘッドレス, ZH: 无头).
   - 'Agnostic' = Independence (JA: 非依存, ZH: 无关性).
8. **System Tags**: Return any text in the format [[PB_X]] exactly as is. These are code identifiers, NOT text. Do NOT translate the word 'PB' or change the brackets.
9. **Noise**: Do not discard anything from the input, everything is important. This is a markdown/HTML document, so preserve tags.
<|START_OF_TURN_TOKEN|><|USER_TOKEN|>
{text_to_translate}<|END_OF_TURN_TOKEN|>
<|START_OF_TURN_TOKEN|><|CHATBOT_TOKEN|>"""

response = llm(prompt, max_tokens=6144, temperature=0, stop=["<|END_OF_TURN_TOKEN|>"])
translated_content = response['choices'][0]['text'].strip()

# --- POST-PROCESSING ---

# 2. Path Correction (Support single and double quotes)
# First, remove 'locales/' prefix if the LLM hallucinated it (so we can correctly prepend ../ later)
translated_content = re.sub(r'(\[.*?\]\()locales/', r'\1', translated_content)
translated_content = re.sub(r'((?:src|href)=["\'])locales/', r'\1', translated_content)

# Then, prepend ../ to relative paths
translated_content = re.sub(r'(\[.*?\]\()(?!(?:http|/|#|\.\./))', r'\1../', translated_content)
translated_content = re.sub(r'((?:src|href)=["\'])(?!(?:http|/|#|\.\./))', r'\1../', translated_content)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(translated_content)