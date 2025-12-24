import os
from llama_cpp import Llama

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README_PATH = os.path.join(BASE_DIR, "README.md")
OUTPUT_PATH = os.path.join(BASE_DIR, "translated_readme.md")
MODEL_PATH = os.path.join(BASE_DIR, "models", "qwen3-1.7b-instruct.gguf")

# 1. FIX: Increased n_ctx to 8192 so it sees the whole README + has room to think
llm = Llama(model_path=MODEL_PATH, n_ctx=8192, verbose=False)

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
    temperature=0.1, 
    stop=["<|im_start|>", "<|im_end|>"]
)

translated_content = response['choices'][0]['text'].strip()

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(translated_content)

print("✅ Translation complete.")