import os
import re
import argparse
from openai import OpenAI  # pip install openai

# 1. Configuration
LANG_MAP = {
    "de": "German", "fr": "French", "es": "Spanish", "ja": "Japanese", 
    "zh": "Chinese(Simplified)", "ru": "Russian", "pt": "Portuguese", 
    "ko": "Korean", "hi": "Hindi"
}

parser = argparse.ArgumentParser()
parser.add_argument("--lang", type=str, required=True, help="Target language code")
args = parser.parse_args()
target_lang_name = LANG_MAP.get(args.lang, "English")

# Connect to LM Studio (Ensure port matches your LM Studio server settings)
client = OpenAI(base_url="http://localhost:5432/v1", api_key="lm-studio")

# File Paths
BASE_DIR = os.getcwd()
README_PATH = os.path.join(BASE_DIR, "README.md")
OUTPUT_PATH = os.path.join(BASE_DIR, "locales", f"README.{args.lang}.md")

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)


with open(README_PATH, "r", encoding="utf-8") as f:
    original_text = f.read()

text_to_translate = original_text

# --- TRANSLATION via LM STUDIO ---
prompt = f"""You are a precise, literal technical translator. Translate the README into professional {target_lang_name} while obeying the following STRICT rules.

MANDATORY RULES (do not ignore):
- CJK Token Separation: Do NOT merge or delete punctuation, spaces, or line breaks that sit between an HTML tag and target language text.
- Visual Preservation: Treat every < and > as a hard boundary. Do not allow any Chinese or Japanese characters to "leak" inside a tag's brackets.
- No Normalization: Do not attempt to "fix" the spacing of the original HTML to better fit {target_lang_name} grammar.
- Preserve every top-level HTML tag, block, and attribute exactly as in the source. Do NOT remove, reorder, normalize, or change any tag name or attribute (including `style`, `align`, `src`, `class`, etc.).
- Do NOT modify file paths, URLs, or filenames in attributes (e.g., `src`, `href`) in any way.
- Only translate visible human text (text nodes) that appears between tags. Do NOT translate tag names, attributes, filenames, or any code fragments.
- Preserve line breaks and indentation for any line that contains HTML tags. If you cannot translate a given line without changing its tags or attributes, leave that line unchanged.
- For `<img>` tags and other self-closing tags, do NOT alter the tag; keep it exactly as-is.
- For `<a>` tags, preserve the `href` attribute value exactly; translate only the link text.
- Do NOT add or remove blank lines; maintain the same number and order of lines as the input.
- Output ONLY the final translated Markdown document content. Do NOT include any explanations, notes, or code fences.

EXAMPLES (input -> expected output):
Input:  <div align="center">Welcome to <a href="../README.md">Project</a></div>
Output: <div align="center">Bienvenido a <a href="../README.md">Project</a></div>

Input:  <div style="margin:10px;"><img src="../path/logo.png" alt="Logo image"/></div>
Output: <div style="margin:10px;"><img src="../path/logo.png" alt="Logo image"/></div>

If you would need to remove, alter, or reformat any HTML tag or attribute to perform the translation, instead KEEP that original input line unchanged.

PENALTY INSTRUCTION: If you remove or change any HTML tag or attribute, that is incorrect — in that case the correct output is the exact original file content.
"""

response = client.chat.completions.create(
    model="aya-expanse-8b",
    messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": text_to_translate}
    ],
    temperature=0,
)

translated_content = response.choices[0].message.content.strip()

# --- POST-PROCESSING: Fuzzy Restoration ---

translated_content = re.sub(r'(\[.*?\]\()(?!(?:http|/|#|\.\./))', r'\1../', translated_content)
translated_content = re.sub(r'((?:src|href)=["\'])(?!(?:http|/|#|\.\./))', r'\1../', translated_content)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(translated_content)

print(f"Done! Translated README saved to: {OUTPUT_PATH}")