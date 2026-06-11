import streamlit as st
from openai import OpenAI
import json
import os   
from pathlib import Path

# --- Client init ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- System prompt ---
SYSTEM_PROMPT = """You are an expert Python code reviewer.
Analyze the provided Python code and return ONLY a valid JSON object with no markdown fences, no explanation.
The JSON must follow this exact structure:
{
  "bugs": ["bug description 1", "bug description 2"],
  "fixed_code": "corrected python code as a string"
}"""

# --- UI ---
HERE = Path(__file__).parent
image_path = HERE / "artificial-intelligence1.png"
st.set_page_config(
    page_title= 'AI Code Reviewer',
    page_icon='artificial-intelligence2.png',
    layout='centered'
    )


st.title("💬 An AI Code Reviewer")
st.caption("Enter your Python code here ...")

code_input = st.text_area(label="", height=150, placeholder="Paste your Python code here...")

if st.button("Generate", type="primary"):
    if not code_input.strip():
        st.warning("Please paste some code first.")
    else:
        with st.spinner("Reviewing your code..."):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": code_input}
                ],
                temperature=0
            )
            raw = response.choices[0].message.content
            clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

            try:
                result = json.loads(clean)

                st.markdown("## Code Review")

                st.markdown("### Bug Report")
                bugs = result.get("bugs", [])
                if bugs:
                    bug_text = " ".join([f"{i}. {b}" for i, b in enumerate(bugs, 1)])
                    st.markdown(f"The bugs in the code are: {bug_text}")
                else:
                    st.markdown("No bugs found.")

                st.markdown("### Fixed Code")
                st.code(result.get("fixed_code", ""), language="python")

            except json.JSONDecodeError:
                st.error("Failed to parse response. Raw output:")
                st.text(raw)