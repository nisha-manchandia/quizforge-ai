from app.config import settings
import json
import re
from typing import List


def clean_json_response(text: str) -> str:
    text = text.strip()
    text = re.sub(r'^```json\s*', '', text)
    text = re.sub(r'^```\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    return text.strip()

def generate_questions_mock(
    prompt: str,
    num_questions: int = 5,
    difficulty: str = "medium"
) -> List[dict]:
    """Mock AI generation for testing when API quota is exceeded."""
    questions = []
    for i in range(num_questions):
        questions.append({
            "question_text": f"Sample question {i+1} about {prompt}?",
            "options": {
                "A": "First option",
                "B": "Second option",
                "C": "Third option",
                "D": "Fourth option"
            },
            "correct_answer": "A",
            "explanation": f"This is the explanation for question {i+1} about {prompt}.",
            "difficulty": difficulty,
            "order_index": i + 1,
            "points": 100
        })
    return questions

def generate_questions(
    prompt: str,
    num_questions: int = 5,
    difficulty: str = "medium"
) -> List[dict]:
    if settings.openai_api_key and len(settings.openai_api_key) > 10 and settings.openai_api_key.startswith("sk-"):
        return generate_quiz_with_openai(prompt, num_questions, difficulty)
    elif settings.gemini_api_key and len(settings.gemini_api_key) > 10:
        try:
            return generate_quiz_with_gemini(prompt, num_questions, difficulty)
        except Exception:
            return generate_questions_mock(prompt, num_questions, difficulty)
    else:
        return generate_questions_mock(prompt, num_questions, difficulty)


def generate_quiz_with_openai(
    prompt: str,
    num_questions: int = 5,
    difficulty: str = "medium"
) -> List[dict]:
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)

    system_prompt = """You are a quiz generation assistant.
Always respond with valid JSON only — no other text, no markdown.
Generate multiple choice questions in exactly this format:
{
  "questions": [
    {
      "question_text": "The question here?",
      "options": {
        "A": "First option",
        "B": "Second option",
        "C": "Third option",
        "D": "Fourth option"
      },
      "correct_answer": "A",
      "explanation": "Why this answer is correct",
      "difficulty": "easy",
      "order_index": 1,
      "points": 100
    }
  ]
}"""

    user_prompt = f"Generate {num_questions} MCQs about: {prompt}. Difficulty: {difficulty}. Return only valid JSON."

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=2000
    )

    raw = response.choices[0].message.content
    cleaned = clean_json_response(raw)
    data = json.loads(cleaned)
    return data["questions"]


def generate_quiz_with_gemini(
    prompt: str,
    num_questions: int = 5,
    difficulty: str = "medium"
) -> List[dict]:
    import google.generativeai as genai

    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    full_prompt = f"""Generate {num_questions} multiple choice questions about: {prompt}
Difficulty level: {difficulty}

Respond with ONLY valid JSON, no other text:
{{
  "questions": [
    {{
      "question_text": "The question here?",
      "options": {{
        "A": "First option",
        "B": "Second option",
        "C": "Third option",
        "D": "Fourth option"
      }},
      "correct_answer": "A",
      "explanation": "Why this answer is correct",
      "difficulty": "{difficulty}",
      "order_index": 1,
      "points": 100
    }}
  ]
}}

Generate exactly {num_questions} questions. Return only the JSON, nothing else."""

    response = model.generate_content(full_prompt)
    raw = response.text
    cleaned = clean_json_response(raw)
    data = json.loads(cleaned)
    return data["questions"]


def generate_explanation(
    question_text: str,
    correct_answer: str,
    options: dict
) -> str:
    if settings.openai_api_key and len(settings.openai_api_key) > 10 and settings.openai_api_key.startswith("sk-"):
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)
        prompt = f"""Question: {question_text}
Correct answer: {correct_answer} — {options.get(correct_answer, '')}
Explain in 2-3 sentences why this is correct and why others are wrong."""
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        return response.choices[0].message.content

    elif settings.gemini_api_key and len(settings.gemini_api_key) > 10:
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = f"""Question: {question_text}
Correct answer: {correct_answer} — {options.get(correct_answer, '')}
Explain in 2-3 sentences why this is correct."""
        response = model.generate_content(prompt)
        return response.text

    return "No explanation available."