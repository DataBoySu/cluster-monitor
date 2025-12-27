import os
import re
import argparse
from llama_cpp import Llama

LANG_MAP = {
    "de": "German", 
    "fr": "French", 
    "es": "Spanish",
    "ru": "Russian", 
    "pt": "Portuguese", 
}

parser = argparse.ArgumentParser()
parser.add_argument("--lang", type=str, required=True)
args = parser.parse_args()
target_lang_name = LANG_MAP.get(args.lang, "English")

# 2. Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README_PATH = os.path.join(BASE_DIR, "README.md")
OUTPUT_PATH = os.path.join(BASE_DIR, "locales", f"README.{args.lang}.md")
MODEL_PATH = os.path.join(BASE_DIR, "models", "aya-expanse-8b-q4_k_s.gguf")

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
llm = Llama(model_path=MODEL_PATH, n_ctx=8192, n_threads=2, verbose=False)

with open(README_PATH, "r", encoding="utf-8") as f:
    original_text = f.read()

# --- PRE-PROCESSING: Universal Agnostic Protection ---
text_to_translate = original_text

# 3. Translation
prompt = f"""<|START_OF_TURN_TOKEN|><|SYSTEM_TOKEN|>
You are a helpful technical translator. Translate the README into professional {target_lang_name} while following these guidelines.

GUIDELINES (follow but stay flexible):
- Prefer preserving top-level HTML tags, blocks, and attributes exactly as in the source. Avoid removing or reordering tags.
- Do NOT change file paths, URLs, or filenames in attributes (e.g., `src`, `href`) unless necessary to correct obvious encoding problems.
- Translate only visible human text (text nodes) that appears between tags. Do NOT translate tag names or code fragments.
- Preserve line breaks and indentation for lines that contain HTML tags where possible. If a minimal whitespace normalization is required for readability, that's acceptable.
- For `<img>` and other self-closing tags, keep the tag unchanged whenever possible; if you must alter formatting, keep attribute values intact.
- For `<a>` tags, preserve the `href` attribute value; translate only the link text.
- Do NOT add or remove structural lines; prefer best-effort translation over failing entirely.
- Output ONLY the final translated Markdown document content. Do NOT include any explanations, notes, or code fences.

EXAMPLE (input -> expected output):
Input:  <div align="center">Hello <a href="../README.md">English</a></div>
Output: <div align="center">Hola <a href="../README.md">English</a></div>

If you determine that a small, safe change to formatting is needed, apply the minimal change and translate text; do not return the original file verbatim unless absolutely unavoidable.<|END_OF_TURN_TOKEN|>
<|START_OF_TURN_TOKEN|><|USER_TOKEN|>
{text_to_translate}<|END_OF_TURN_TOKEN|>
<|START_OF_TURN_TOKEN|><|CHATBOT_TOKEN|>"""

response = llm(prompt, max_tokens=8192, temperature=0, stop=["<|END_OF_TURN_TOKEN|>"])
translated_content = response['choices'][0]['text'].strip()

# --- POST-PROCESSING: Robust Fuzzy Restoration ---
# 1. CLEANUP: Remove markdown code fences if the LLM included them
if translated_content.startswith("```"):
    lines = translated_content.splitlines()
    if lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]
    translated_content = "\n".join(lines).strip()

# 4. Path Correction (Repository Agnostic)
# Prepend ../ to links if they aren't external, absolute, or already corrected.
translated_content = re.sub(r'(\[.*?\]\()(?!(?:http|/|#|\.\./))', r'\1../', translated_content)
translated_content = re.sub(r'((?:src|href)=["\'])(?!(?:http|/|#|\.\./))', r'\1../', translated_content)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(translated_content)