import os
import re
import argparse
from llama_cpp import Llama

LANG_MAP = {
    "de": "German", 
    "fr": "French", 
    "es": "Spanish",
    "pt": "Portuguese", 
}

parser = argparse.ArgumentParser()
parser.add_argument("--lang", type=str, required=True)
args = parser.parse_args()
target_lang_name = LANG_MAP.get(args.lang, "English")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README_PATH = os.path.join(BASE_DIR, "README.md")
OUTPUT_DIR = os.path.join(BASE_DIR, "locales")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, f"README.{args.lang}.md")
MODEL_PATH = os.path.join(BASE_DIR, "models", "aya-expanse-8b-q4_k_s.gguf")

os.makedirs(OUTPUT_DIR, exist_ok=True)
llm = Llama(model_path=MODEL_PATH, n_ctx=6144, n_threads=2, verbose=False)

with open(README_PATH, "r", encoding="utf-8") as f:
    original_text = f.read()

# --- PRE-PROCESSING---

text_to_translate = original_text

prompt = f"""<|START_OF_TURN_TOKEN|><|SYSTEM_TOKEN|>
You are a professional technical {target_lang_name} translator.
Your task is to translate the README into {target_lang_name} while strictly preserving the header and layout.

MANDATORY INSTRUCTIONS:
1. **Start with the Header**: The output MUST begin with the exact Navigation Bar HTML and Logo HTML from the source. Do not translate or modify them.
2. **Preserve Badges**: All lines starting with `![` are code/badges. Copy them exactly. Do not translate the text inside `[]` or `()`.
3. **Translate Content**: Translate the rest of the documentation into professional {target_lang_name}.
4. **Technical Terms**: Keep terms like GPU, CLI, VRAM, SSH, Docker, API, CUDA in English.
5. **No Conversational Text**: Output only the final Markdown file content. No "Here is the translation" or code fences.
<|END_OF_TURN_TOKEN|>
<|START_OF_TURN_TOKEN|><|USER_TOKEN|>
{text_to_translate}<|END_OF_TURN_TOKEN|>
<|START_OF_TURN_TOKEN|><|CHATBOT_TOKEN|>"""

response = llm(prompt, max_tokens=6144, temperature=0, stop=["<|END_OF_TURN_TOKEN|>"])
translated_content = response['choices'][0]['text'].strip()

# --- POST-PROCESSING ---
# 1. CLEANUP: Remove markdown code fences if the LLM included them
if translated_content.startswith("```"):
    lines = translated_content.splitlines()
    if lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]
    translated_content = "\n".join(lines).strip()

# 2. Path Correction
# Prepend ../ to relative paths
translated_content = re.sub(r'(\[.*?\]\()(?!(?:http|/|#|\.\./))', r'\1../', translated_content)
translated_content = re.sub(r'((?:src|href)=["\'])(?!(?:http|/|#|\.\./))', r'\1../', translated_content)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(translated_content)