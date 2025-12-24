import os
import re
from llama_cpp import Llama

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README_PATH = os.path.join(BASE_DIR, "README.md")
OUTPUT_DIR = os.path.join(BASE_DIR, "locales")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "translated_readme.md")
MODEL_PATH = os.path.join(BASE_DIR, "models", "aya-expanse-8b-q4_k_s.gguf")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Reduced n_ctx to 4096 to fit 8B model + KV cache within 7GB GitHub Runner RAM.
# Added n_threads=2 to match GitHub Action runner vCPUs.
llm = Llama(model_path=MODEL_PATH, n_ctx=4096, n_threads=2, verbose=False)

with open(README_PATH, "r", encoding="utf-8") as f:
    text_to_translate = f.read()

# Aya Expanse uses a specific header format for system/user/chatbot turns
prompt = f"""<|START_OF_TURN_TOKEN|><|SYSTEM_TOKEN|>
You are a professional technical translator. 
Perform a strict technical translation of the provided README into professional developer-level German. 
Maintain a formal tone and preserve technical terminology (e.g., GPU, CLI, vCPU).
Keep all Markdown/HTML syntax exactly as is. 
ONLY output the translated German text. No talk, just translation.
Do not add new information, do not summarize, and do not include any conversational filler or "thinking" process.<|END_OF_TURN_TOKEN|>
<|START_OF_TURN_TOKEN|><|USER_TOKEN|>
{text_to_translate}<|END_OF_TURN_TOKEN|>
<|START_OF_TURN_TOKEN|><|CHATBOT_TOKEN|>
"""

# 2. FIX: High max_tokens (4096) to prevent cut-off and low temperature for accuracy
response = llm(
    prompt, 
    max_tokens=4096, 
    temperature=0, # Set to 0 for maximum determinism in translation
    stop=["<|END_OF_TURN_TOKEN|>", "<|START_OF_TURN_TOKEN|>"]
)

translated_content = response['choices'][0]['text'].strip()

# 0. SAFETY: Remove HTML comments if the LLM wrapped the output in them
translated_content = re.sub(r'^<!--\s*|(?:\s*)?-->$', '', translated_content).strip()

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

print("✅ Translation complete.")