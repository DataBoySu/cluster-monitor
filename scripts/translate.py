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

# Aya Expanse specific header format system/user/chatbot turns
prompt = f"""<|START_OF_TURN_TOKEN|><|SYSTEM_TOKEN|>
You are a professional technical translator specializing in software documentation (GitHub READMEs).
Translate the provided README into professional developer-level {target_lang_name}.
CRITICAL RULES:
1. **Badges**: Do NOT translate Markdown image syntax. Specifically, do NOT translate text inside square brackets `![...]` or parentheses `(...)` for badge lines (e.g., license, python, version badges).
2. **Navigation**: Do NOT modify the top-level HTML navigation bar (`<div align="center">`).
3. **Context**: Treat 'Enforcement' as 'System policy restriction' and 'Headless' as 'server without GUI'.
4. **Technical Integrity**: Preserve standard terms (GPU, CLI, VRAM, SSH, Docker) in English.
5. **Formatting**: Preserve all emojis and HTML/Markdown tags exactly.
6. **No Talk**: Output ONLY the translated text. Do not include markdown code fences (```) around the entire output.<|END_OF_TURN_TOKEN|>
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
# We need to ensure that links to the root go up one level (../) 
# but links to other files in the same /locales/ folder stay relative.

# Step 1: Prepend ../ to relative paths (ignoring external links, absolute paths, anchors, or locales/)
# This targets Markdown links/images text and HTML src="path"/href="path"
translated_content = re.sub(r'(\[.*?\]\()(?!(?:http|/|#|\.\./|locales/))', r'\1../', translated_content)
translated_content = re.sub(r'((?:src|href)=")(?!(?:http|/|#|\.\./|locales/))', r'\1../', translated_content)

# Step 2: Handle links that point to the locales directory.
# Since the translated file is ALREADY in /locales/, we strip the 'locales/' prefix
# so they point to the sibling files in the same directory.
translated_content = re.sub(r'(\[.*?\]\()locales/', r'\1', translated_content)
translated_content = re.sub(r'((?:src|href)=")locales/', r'\1', translated_content)

# 3. RESTORE BADGES: Ensure badges match the original English README exactly.
# This fixes cases where the LLM translates the Alt text (e.g., ![License] -> ![Lizenz])
# or slightly alters the URL.

# Extract all shields.io badges from the original source text
original_badges = re.findall(r'(!\[.*?\]\(https://img\.shields\.io/.*?\))', text_to_translate)

for badge in original_badges:
    # Extract the URL from the original badge to use as a key
    match = re.search(r'\((https://img\.shields\.io/.*?)\)', badge)
    if match:
        url = match.group(1)
        # Replace any markdown image in the translated text that has this URL
        # with the exact original badge string.
        translated_content = re.sub(rf'!\[.*?\]\({re.escape(url)}\)', lambda m: badge, translated_content)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(translated_content)

print(f"Translation to {target_lang_name} complete: {OUTPUT_PATH}")