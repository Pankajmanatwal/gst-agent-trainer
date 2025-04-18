import os
import json
import uuid
from datetime import datetime
from pathlib import Path

RAW_TEXT_FOLDER = "data/post_cleaned_text"  # Already processed legal data
OUTPUT_FILE = "admin_ideas/agent_thoughts.json"

os.makedirs("admin_ideas", exist_ok=True)

# Load existing thoughts (if any)
if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "r") as f:
        existing_thoughts = json.load(f)
else:
    existing_thoughts = []

def generate_idea_from_text(filename, content):
    lines = content.split("\n")
    ideas = []
    for i, line in enumerate(lines):
        line = line.strip()
        if not line or len(line) < 80:
            continue

        # Basic heuristics for pattern idea generation
        if any(trigger in line.lower() for trigger in ["evasion", "penalty", "suppress", "fake", "mismatch", "violation"]):
            idea = {
                "idea_id": f"agent_{uuid.uuid4().hex[:6]}",
                "title": f"Potential red flag in: {filename}"[:80],
                "logic": line.strip(),
                "suggestion_to_agent": "Investigate if this condition can be framed as a pattern and generate a fraud case.",
                "source_file": filename,
                "generated_at": datetime.now().isoformat(),
                "source": "agent"
            }
            ideas.append(idea)
    return ideas

new_ideas = []

# Iterate through all files in raw text folder
for file in Path(RAW_TEXT_FOLDER).rglob("*.txt"):
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
        generated = generate_idea_from_text(file.name, content)
        new_ideas.extend(generated)

# Filter: avoid duplicates by title + logic
existing_signatures = {(i['title'], i['logic']) for i in existing_thoughts}
unique_new_ideas = [i for i in new_ideas if (i['title'], i['logic']) not in existing_signatures]

if unique_new_ideas:
    all_ideas = existing_thoughts + unique_new_ideas
    with open(OUTPUT_FILE, "w") as f:
        json.dump(all_ideas, f, indent=2)
    print(f"✅ {len(unique_new_ideas)} new agent ideas generated and saved.")
else:
    print("🟡 No new ideas found in this run.")
