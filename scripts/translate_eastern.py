import os
import re
import argparse
from llama_cpp import Llama

LANG_MAP = {
    "ja": "Japanese", 
    "zh": "Chinese(Simplified)",
    "ko": "Korean",
    "hi": "Hindi",
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

# --- PRE-PROCESSING ---
protected_blocks = []

def protect_match(match):
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

# Specialized Prompt for CJK/Eastern Languages
prompt = f"""<|START_OF_TURN_TOKEN|><|SYSTEM_TOKEN|>
You are a professional technical {target_lang_name} translator. Translate the provided GitHub README into {target_lang_name}.

CRITICAL RULES:
1. **Placeholders**: You will see tags like __PB_0__, __PB_1__. 
   - DO NOT translate them.
   - DO NOT remove them.
   - DO NOT convert underscores (_) to full-width characters. Keep them as it is.
2. **Formatting**: Preserve all Markdown structure exactly.
3. **Terminology**: Keep English technical terms (GPU, CLI, VRAM, Docker, CUDA) in English.
4. **Context**: 
   - 'Enforcement' = Policy restriction (e.g., JA: 制限/強制).
   - 'Headless' = Server without display.
5. **Output**: ONLY the translated text. No explanations.
<|END_OF_TURN_TOKEN|>
<|START_OF_TURN_TOKEN|><|USER_TOKEN|>
{text_to_translate}<|END_OF_TURN_TOKEN|>
<|START_OF_TURN_TOKEN|><|CHATBOT_TOKEN|>"""

response = llm(prompt, max_tokens=6144, temperature=0, stop=["<|END_OF_TURN_TOKEN|>"])
translated_content = response['choices'][0]['text'].strip()

# --- POST-PROCESSING: Chain Restoration ---

for i, block in enumerate(protected_blocks):
    placeholder = f"__PB_{i}__"
    
    # 1. Direct replacement
    if placeholder in translated_content:
        translated_content = translated_content.replace(placeholder, block)
        continue
    
    # 2. Loose Regex Fallback (Handles CJK full-width issues like ＿PB＿0＿)
    # Matches __PB_0__, ＿PB_0＿, [PB_0], etc.
    loose_pattern = re.compile(rf"[\[［]?\s*[__＿]+\s*PB_{i}\s*[__＿]+\s*[\]］]?", re.IGNORECASE)
    if loose_pattern.search(translated_content):
        translated_content = loose_pattern.sub(lambda m: block, translated_content)
        continue

    # 3. CRITICAL FALLBACK: Chain Insertion
    if i == 0: 
        translated_content = block + "\n\n" + translated_content
    else:
        prev_block = protected_blocks[i-1]
        if prev_block in translated_content:
            # Insert current block immediately after the previous one
            translated_content = translated_content.replace(prev_block, prev_block + "\n" + block, 1)
        else:
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
    lines = translated_content.splitlines()
    if lines[0].startswith("```"): lines = lines[1:]
    if lines and lines[-1].strip().startswith("```"): lines = lines[:-1]
    translated_content = "\n".join(lines).strip()

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(translated_content)