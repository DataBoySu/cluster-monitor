import os
import re
import argparse
import sys
import time
from openai import OpenAI

# 1. Config
LANG_MAP = {
    "de": "German", "fr": "French", "es": "Spanish", "ja": "Japanese",
    "zh": "Chinese(Simplified)", "ru": "Russian", "pt": "Portuguese",
    "ko": "Korean", "hi": "Hindi"
}

parser = argparse.ArgumentParser()
parser.add_argument("--lang", type=str, required=True)
args = parser.parse_args()
target_lang_name = LANG_MAP.get(args.lang, "English")

client = OpenAI(base_url="http://localhost:5432/v1", api_key="lm-studio")

# 2. Advanced Tokenizer: Merges tiny fragments to prevent hallucinations
def get_smart_chunks(text):
    # 1. Capture major containers as single blocks
    # This regex now looks for the WHOLE div/details block at once
    pattern = r'(' \
              r'```[\s\S]*?```|' \
              r'<div\b[^>]*>[\s\S]*?<\/div>|' \
              r'<details\b[^>]*>[\s\S]*?<\/details>|' \
              r'^#{1,6} .*' \
              r')'
              
    raw_parts = re.split(pattern, text, flags=re.MULTILINE | re.IGNORECASE)
    
    chunks = []
    for part in raw_parts:
        if not part or not part.strip(): continue
        
        # Identify if the chunk is a major structural container
        if part.strip().startswith(('<div', '<details', '```', '#')):
            chunks.append(("struct", part.strip()))
        else:
            # Everything else (Badges, prose, small links) stays together as one PROSE block
            chunks.append(("prose", part.strip()))
            
    return chunks

# 3. Strict Prompts
SYSTEM_STRUCT = (
    "You are a literal mirror. Output the provided HTML/Markdown exactly as it is. Only translate the human-readable text between tags. "
    "Do NOT add markdown code fences (```)."
    "Do NOT add any notes or explanations."
    "If there is no text to translate, return the input 100% unchanged."
    "ONLY translate the 'alt' text or the text between tags. "
    "FORBIDDEN: Do not add markdown code fences (```). Do not change attributes."
)

SYSTEM_PROSE = (
    f"Translate this documentation snippet into {target_lang_name}. "
    "STRICT RULES: \n"
    "1. Translate ONLY the provided text.\n"
    "2. DO NOT add definitions, explanations, or extra context.\n"
    "3. If the input is just a symbol (like |), return just that symbol.\n"
    "4. Keep technical terms (GPU, VRAM, Docker) in English."
    "Do NOT define terms or add extra context."
    "If the input is a list of badges or symbols, preserve their exact Markdown syntax."
    "Output ONLY the translation."
)

# 4. Main Loop
def main():
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    chunks = get_smart_chunks(content)
    final_output = []

    print(f"--- Processing {len(chunks)} Smart Fragments ---")

    for i, (ctype, ctext) in enumerate(chunks):
        sys.stdout.write(f"\n[{i+1}/{len(chunks)}] ")
        
        system = SYSTEM_STRUCT if ctype == "struct" else SYSTEM_PROSE
        
        response = client.chat.completions.create(
            model="aya-expanse-8b",
            messages=[{"role": "system", "content": system}, {"role": "user", "content": ctext}],
            temperature=0,
            stream=True
        )

        translated = ""
        for part in response:
            if part.choices[0].delta.content:
                t = part.choices[0].delta.content
                translated += t
                sys.stdout.write(t)
                sys.stdout.flush()
        
        # Fail-safe for Structural blocks
        if ctype == "struct" and len(translated.strip()) < 5:
            translated = ctext
            
        final_output.append(translated)

    # Save and Fix Paths
    full_text = "\n".join(final_output)
    full_text = re.sub(r'(\[.*?\]\()(?!(?:http|/|#|\.\./))', r'\1../', full_text)
    
    os.makedirs("locales", exist_ok=True)
    with open(f"locales/README.{args.lang}.md", "w", encoding="utf-8") as f:
        f.write(full_text)

if __name__ == "__main__":
    main()