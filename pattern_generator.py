import streamlit as st
import json
import uuid
import os
from datetime import datetime

st.set_page_config(page_title="GST AI Trainer Interface", layout="centered")
st.title("🧠 GST AI Agent — Admin Review Panel")

st.markdown("---")

# Step 0: Login Security
if "authenticated" not in st.session_state:
    with st.form("login_form"):
        st.subheader("🔐 Secure Login")
        login_id = st.text_input("Login ID")
        password = st.text_input("Password", type="password")
        login_submit = st.form_submit_button("Login")

    if login_submit:
        with open("users.json", "r") as userfile:
            valid_users = json.load(userfile)
        if login_id in valid_users and password == valid_users[login_id]:
            st.session_state["authenticated"] = True
            st.session_state["login_id"] = login_id
            st.rerun()
        else:
            st.error("❌ Invalid Login ID or Password")

# Step 1: Identity Capture (except for admin)
elif "identity" not in st.session_state:
    if st.session_state.get("login_id") == "admin":
        st.session_state["identity"] = {"name": "Admin", "role": "Tax Official", "mobile": "0000000000"}
        st.rerun()
    else:
        with st.form("trainer_info"):
            st.subheader("👤 Your Identity")
            name = st.text_input("Full Name")
            role = st.selectbox("Your Role", ["Tax Official", "Chartered Accountant", "Accountant", "Other"])
            mobile = st.text_input("Mobile Number")
            submitted_identity = st.form_submit_button("Continue")

        if submitted_identity:
            if not name or not mobile:
                st.warning("Please enter your name and mobile number to proceed.")
            else:
                st.session_state["identity"] = {"name": name, "role": role, "mobile": mobile}
                st.rerun()

# Step 2: Pattern Selection Interface
else:
    st.success(f"Welcome, {st.session_state['identity']['name']} ({st.session_state['identity']['role']})")
    pattern_folder = "emerging_patterns"
    pattern_files = [f for f in os.listdir(pattern_folder) if f.endswith(".json")]

    # Admin: Idea Submission Section
    if st.session_state['login_id'] == "admin":
        st.markdown("---")
        st.subheader("💡 Submit a New Thinking Idea for Pattern Generation")

        with st.form("idea_submission"):
            idea_title = st.text_input("Idea Title")
            idea_logic = st.text_area("Logic / Observation")
            suggestion_to_agent = st.text_area("How should the agent use this idea to generate a pattern?")
            idea_submit = st.form_submit_button("Submit Idea")

        if idea_submit:
            new_idea = {
                "idea_id": f"idea_{uuid.uuid4().hex[:8]}",
                "title": idea_title,
                "logic": idea_logic,
                "suggestion_to_agent": suggestion_to_agent
            }
            idea_path = "admin_ideas/admin_thinking_ideas.json"
            os.makedirs("admin_ideas", exist_ok=True)
            if os.path.exists(idea_path):
                with open(idea_path, "r") as f:
                    existing_ideas = json.load(f)
            else:
                existing_ideas = []

            existing_ideas.append(new_idea)
            with open(idea_path, "w") as f:
                json.dump(existing_ideas, f, indent=2)

            st.success("✅ Idea submitted successfully! The agent will use it in the next pattern generation cycle.")

    st.markdown("---")
    st.subheader("📂 Review Suggested Patterns")

    if not pattern_files:
        st.info("✅ No more pending patterns to review.")
    else:
        pattern_titles = {}
        for f in pattern_files:
            try:
                with open(os.path.join(pattern_folder, f), "r") as file:
                    data = json.load(file)
                    pattern_titles[f] = data.get("title", "Untitled Pattern")
            except:
                pattern_titles[f] = "Untitled Pattern"

        selected_pattern_id = st.selectbox(
            "📂 Select a pattern to review:",
            options=pattern_files,
            format_func=lambda f: pattern_titles.get(f, "Unknown Pattern")
        )

        if selected_pattern_id:
            with open(os.path.join(pattern_folder, selected_pattern_id), "r") as f:
                suggested_pattern = json.load(f)

            st.markdown("---")
            st.subheader("📄 Suggested Fraud Pattern for Review")

            with st.form("review_form"):
                st.write(f"**Pattern ID:** {suggested_pattern['pattern_id']}")
                title = st.text_input("Suggested Title", value=suggested_pattern["title"])
                behavior = st.text_area("Detected Behavior (edit if needed)", value="\n".join(suggested_pattern["detected_behavior"]))
                action = st.text_area("Recommended Action", value="\n".join(suggested_pattern["recommended_action"]))
                tags = st.text_input("Tags (comma-separated)", value=", ".join(suggested_pattern["tags"]))

                specific_instr = st.text_area("🧠 Trainer's Interpretation or Specific Instruction (optional)")
                status = st.radio("Do you want to confirm this pattern?", ["✅ Confirm", "❌ Reject", "📝 Send Back for Review"])
                novel_fraud = st.text_area("💡 Suggest a novel fraud pattern you’ve encountered (optional)")

                submitted_review = st.form_submit_button("Submit Feedback")

            if submitted_review:
                review_data = {
                    "submitted_by": st.session_state["identity"],
                    "pattern_id": suggested_pattern["pattern_id"],
                    "title": title,
                    "behavior": behavior.split("\n"),
                    "recommended_action": action.split("\n"),
                    "tags": [t.strip() for t in tags.split(",")],
                    "trainer_notes": specific_instr,
                    "status": status,
                    "novel_fraud_suggestion": novel_fraud,
                    "submitted_at": datetime.now().isoformat()
                }

                if not os.path.exists("pending_reviews"):
                    os.makedirs("pending_reviews")
                reviewed_file = f"pending_reviews/{uuid.uuid4()}.json"
                with open(reviewed_file, "w") as f:
                    json.dump(review_data, f, indent=2)

                os.remove(os.path.join(pattern_folder, selected_pattern_id))
                st.success("✅ Your feedback has been recorded. Loading next pattern...")
                st.rerun()
