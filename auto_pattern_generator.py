import os
import json
import uuid
import time
from datetime import datetime

ADMIN_IDEAS_PATH = "admin_ideas/admin_thinking_ideas.json"
OUTPUT_FOLDER = "emerging_patterns"
CHECK_INTERVAL_HOURS = 3

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def load_admin_ideas():
    if not os.path.exists(ADMIN_IDEAS_PATH):
        return []
    with open(ADMIN_IDEAS_PATH, "r") as f:
        return json.load(f)

def already_generated(idea_id):
    filename = f"pattern_{idea_id}.json"
    return os.path.exists(os.path.join(OUTPUT_FOLDER, filename))

def generate_pattern_from_idea(idea):
    pattern = {
        "pattern_id": f"pattern_{idea['idea_id']}",
        "title": idea["title"],
        "detected_behavior": [idea["logic"]],
        "recommended_action": [idea["suggestion_to_agent"]],
        "tags": ["auto_generated", "admin_idea"],
        "generated_at": datetime.now().isoformat()
    }
    with open(os.path.join(OUTPUT_FOLDER, f"pattern_{idea['idea_id']}.json"), "w") as f:
        json.dump(pattern, f, indent=2)
    print(f"✅ Generated: {pattern['pattern_id']}")

def generate_patterns():
    ideas = load_admin_ideas()
    new_count = 0
    for idea in ideas:
        if not already_generated(idea["idea_id"]):
            generate_pattern_from_idea(idea)
            new_count += 1
    print(f"Total new patterns generated: {new_count}")

if __name__ == "__main__":
    while True:
        print("\n⏱️ Running auto pattern generator...", datetime.now().isoformat())
        generate_patterns()
        print(f"⏳ Sleeping for {CHECK_INTERVAL_HOURS} hours...")
        time.sleep(CHECK_INTERVAL_HOURS * 3600)
