import streamlit as st
import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

st.set_page_config(
    page_title="MCQ Generator",
    page_icon="📝",
    layout="wide"
)

if not HF_TOKEN:
    st.error("Hugging Face token not found.")
    st.stop()


client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN
)

st.title("📝 AI MCQ Generator")

st.write(
    "Generate multiple-choice questions on any topic "
    "using Artificial Intelligence."
)

st.divider()

with st.sidebar:

    st.header("Quiz Settings")

    topic = st.text_input(
        "Enter Topic",
        placeholder="Example: Artificial Intelligence"
    )

    number = st.selectbox(
        "Number of Questions",
        [5, 10, 15]
    )

    difficulty = st.selectbox(
        "Difficulty",
        ["Easy", "Medium", "Hard"]
    )

    generate = st.button(
        "Generate MCQs",
        use_container_width=True
    )

if generate:

    if not topic.strip():

        st.warning("Please enter a topic.")

    else:

        with st.spinner("Generating questions..."):

            try:

                prompt = f"""
Create {number} multiple-choice questions about {topic}.

Difficulty level: {difficulty}

Return ONLY valid JSON.

Use exactly this format:

[
  {{
    "question": "Question here",
    "options": [
      "Option A",
      "Option B",
      "Option C",
      "Option D"
    ],
    "answer": "Option A",
    "explanation": "Short explanation"
  }}
]

Rules:
- Each question must have exactly 4 options.
- Only one option must be correct.
- The answer must exactly match one of the four options.
- Questions should be clear and educational.
"""

                response = client.chat.completions.create(
                    model="meta-llama/Llama-3.1-8B-Instruct:novita",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an educational MCQ generator. "
                                "Always follow the requested JSON format."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=2500,
                    temperature=0.7
                )

                result = response.choices[0].message.content

                # Remove markdown code fences if the AI adds them
                result = re.sub(
                    r"```json|```",
                    "",
                    result
                ).strip()

                questions = json.loads(result)

                st.session_state.questions = questions
                st.session_state.user_answers = {}
                st.session_state.submitted = False

            except Exception as e:

                st.error("Unable to generate MCQs.")
                st.code(str(e))

if "questions" in st.session_state:

    questions = st.session_state.questions

    st.subheader("Quiz")

    for i, q in enumerate(questions):

        st.markdown(
            f"### Q{i + 1}. {q['question']}"
        )

        st.session_state.user_answers[i] = st.radio(
            "Choose your answer:",
            q["options"],
            key=f"question_{i}"
        )

        st.divider()

    if st.button("Submit Quiz", type="primary"):

        score = 0

        st.session_state.submitted = True

        for i, q in enumerate(questions):

            user_answer = st.session_state.user_answers.get(i)

            if user_answer == q["answer"]:
                score += 1

        st.success(
            f"Your Score: {score} / {len(questions)}"
        )

    if st.session_state.get("submitted", False):

        st.subheader("Answers & Explanations")

        for i, q in enumerate(questions):

            user_answer = st.session_state.user_answers.get(i)

            if user_answer == q["answer"]:

                st.success(
                    f"Q{i + 1}: Correct"
                )

            else:

                st.error(
                    f"Q{i + 1}: Incorrect"
                )

                st.write(
                    f"Correct Answer: **{q['answer']}**"
                )

            st.info(q["explanation"])

st.divider()

st.caption(
    "AI MCQ Generator | Built with Python, Streamlit and Hugging Face"
)
