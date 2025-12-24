import os
import re
from llama_cpp import Llama

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README_PATH = os.path.join(BASE_DIR, "README.md")
OUTPUT_DIR = os.path.join(BASE_DIR, "locales")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "translated_readme.md")
MODEL_PATH = os.path.join(BASE_DIR, "models", "qwen2.5-coder-1.5b-instruct.gguf")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. FIX: Increased n_ctx to 8192 so it sees the whole README + has room to think
# Added n_threads=2 to match GitHub Action runner vCPUs
llm = Llama(model_path=MODEL_PATH, n_ctx=8192, n_threads=2, verbose=False)

with open(README_PATH, "r", encoding="utf-8") as f:
    text_to_translate = f.read()

prompt = f"""<|im_start|>system
You are a professional technical translator. 
Translate the provided README to German. 
Keep all Markdown/HTML syntax. 
ONLY output the translated German text. No talk, just translation.<|im_end|>
<|im_start|>user
{text_to_translate}<|im_end|>
<|im_start|>assistant
"""

# 2. FIX: High max_tokens (4096) to prevent cut-off and low temperature for accuracy
response = llm(
    prompt, 
    max_tokens=4096, 
    temperature=0, # Set to 0 for maximum determinism in translation
    stop=["<|im_start|>", "<|im_end|>"]
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

# 2. FIX PATHS: Prepend ../ to relative paths since this file lives in /locales/
# This targets Markdown links/images text and HTML src="path"/href="path"
translated_content = re.sub(r'(\[.*?\]\()(?!(?:http|/|#))', r'\1../', translated_content)
translated_content = re.sub(r'((?:src|href)=")(?!(?:http|/|#))', r'\1../', translated_content)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(translated_content)

print("✅ Translation complete.")