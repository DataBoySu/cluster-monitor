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
    lines = f.readlines()

# --- PRE-PROCESSING: Protect Sensitive Blocks ---
protected_blocks = []

def protect_match(match):
    # Use underscores to look like code variables, which LLMs respect more
    placeholder = f"__PB_{len(protected_blocks)}__" 
    protected_blocks.append(match.group(0))
    return placeholder

# Manual Line Protection (User Request)
# Block 0: Lines 1-15 (Nav + Logo) -> lines[0:15]
protected_blocks.append("".join(lines[0:15]))
# Block 1: Lines 19-66 (Badges + Gallery) -> lines[18:66]
protected_blocks.append("".join(lines[18:66]))

# Construct text: PB0 + Lines 16-18 (Quote) + PB1 + Lines 67+ (Body)
text_to_translate = f"__PB_0__{''.join(lines[15:18])}__PB_1__{''.join(lines[66:])}"

# Protect any remaining images in the rest of the text
text_to_translate = re.sub(r'(!\[[^\]\r\n]*\]\([^)\r\n]+\))', protect_match, text_to_translate)

prompt = f"""<|START_OF_TURN_TOKEN|><|SYSTEM_TOKEN|>
You are a professional technical translator. Translate the provided README into professional developer-level {target_lang_name}.
CRITICAL RULES:
1. **Structure**: Keep the layout exactly the same.
2. **Placeholders**: You will see placeholders like __PB_0__, __PB_1__. These are images or layout blocks. KEEP THEM EXACTLY AS IS. Do not move or translate them.
3. **Terminology**: Preserve terms like GPU, CLI, VRAM, SSH, Docker, API, CUDA.
4. **No Talk**: Output ONLY the translated text.
<|END_OF_TURN_TOKEN|>
<|START_OF_TURN_TOKEN|><|USER_TOKEN|>
{text_to_translate}<|END_OF_TURN_TOKEN|>
<|START_OF_TURN_TOKEN|><|CHATBOT_TOKEN|>"""

response = llm(prompt, max_tokens=6144, temperature=0, stop=["<|END_OF_TURN_TOKEN|>"])
translated_content = response['choices'][0]['text'].strip()

# --- POST-PROCESSING: Chain Restoration ---

for i, block in enumerate(protected_blocks):
    placeholder = f"__PB_{i}__"
    
    # 1. Direct replacement (Best case)
    if placeholder in translated_content:
        translated_content = translated_content.replace(placeholder, block)
        continue
    
    # 2. Loose Regex Fallback (Handles spacing issues)
    loose_pattern = re.compile(rf"\[?\s*__\s*PB_{i}\s*__\s*\]?", re.IGNORECASE)
    if loose_pattern.search(translated_content):
        translated_content = loose_pattern.sub(lambda m: block, translated_content)
        continue

    # 3. CRITICAL FALLBACK: Chain Insertion
    # If a block is missing, insert it immediately after the previous block.
    # This ensures Nav -> Logo -> Badge1 -> Badge2 order is preserved even if the LLM drops them.
    
    if i == 0: 
        # Nav missing? Prepend to file.
        translated_content = block + "\n\n" + translated_content
    else:
        # Insert after the previous block (which is guaranteed to be in the text now)
        prev_block = protected_blocks[i-1]
        if prev_block in translated_content:
            # Replace the previous block with "Previous + New"
            # We use a specific check to avoid duplicating if the previous block appears multiple times (unlikely for these headers)
            translated_content = translated_content.replace(prev_block, prev_block + "\n" + block, 1)
        else:
            # If previous block is somehow missing (shouldn't happen due to loop order), just prepend
            translated_content = block + "\n\n" + translated_content

# 4. Path Correction
# Remove 'locales/' hallucination
translated_content = re.sub(r'(\[.*?\]\()locales/', r'\1', translated_content)
translated_content = re.sub(r'((?:src|href)=["\'])locales/', r'\1', translated_content)

# Prepend ../ to relative paths
translated_content = re.sub(r'(\[.*?\]\()(?!(?:http|/|#|\.\./))', r'\1../', translated_content)
translated_content = re.sub(r'((?:src|href)=["\'])(?!(?:http|/|#|\.\./))', r'\1../', translated_content)

# 5. Cleanup
translated_content = re.sub(r'^<!--\s*|(?:\s*)?-->$', '', translated_content).strip()
if translated_content.startswith("```"):
    translated_content = "\n".join(translated_content.splitlines()[1:-1]).strip()

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(translated_content)