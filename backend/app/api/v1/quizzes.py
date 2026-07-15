from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.core.dependencies import get_db
from app.api.v1.auth import get_current_user
from app.schemas.quiz import (
    QuizCreate,
    QuizUpdate,
    QuizResponse,
    QuizDetailResponse,
    QuestionCreate,
    QuestionResponse
)
from app.services.quiz_service import (
    create_quiz,
    get_my_quizzes,
    get_quiz_by_id,
    update_quiz,
    delete_quiz,
    add_question,
    delete_question
)

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])


@router.post("", response_model=QuizDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_new_quiz(quiz_data: QuizCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Create a new quiz."""
    return create_quiz(db, quiz_data, current_user.id)


@router.get("", response_model=List[QuizResponse])
async def list_my_quizzes(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Get all quizzes created by the current user."""
    return get_my_quizzes(db, current_user.id)


@router.get("/{quiz_id}", response_model=QuizDetailResponse)
async def get_quiz(quiz_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Get a single quiz with all its questions."""
    return get_quiz_by_id(db, quiz_id, current_user.id)


@router.put("/{quiz_id}", response_model=QuizResponse)
async def update_existing_quiz(quiz_id: UUID, quiz_data: QuizUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Update quiz details."""
    return update_quiz(db, quiz_id, quiz_data, current_user.id)


@router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_quiz(quiz_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Delete a quiz."""
    delete_quiz(db, quiz_id, current_user.id)


@router.post("/{quiz_id}/questions", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def add_question_to_quiz(quiz_id: UUID, question_data: QuestionCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Add a question to an existing quiz."""
    return add_question(db, quiz_id, question_data, current_user.id)


@router.delete("/{quiz_id}/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question_from_quiz(quiz_id: UUID, question_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Delete a question from a quiz."""
    delete_question(db, quiz_id, question_id, current_user.id)


@router.post("/generate", response_model=QuizDetailResponse, status_code=status.HTTP_201_CREATED)
async def generate_ai_quiz(
    prompt: str,
    num_questions: int = 5,
    difficulty: str = "medium",
    title: str = "AI Generated Quiz",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Generate a quiz using AI from a text prompt."""
    from app.services.ai_service import generate_questions

    try:
        ai_questions = generate_questions(
            prompt=prompt,
            num_questions=num_questions,
            difficulty=difficulty
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

    questions = []
    for i, q in enumerate(ai_questions):
        questions.append(QuestionCreate(
            question_text=q["question_text"],
            options=q["options"],
            correct_answer=q["correct_answer"],
            explanation=q.get("explanation", ""),
            difficulty=q.get("difficulty", difficulty),
            order_index=i + 1,
            points=q.get("points", 100)
        ))

    quiz_data = QuizCreate(
        title=title,
        description=f"AI generated quiz about: {prompt}",
        difficulty=difficulty,
        is_public=False,
        time_limit=30,
        questions=questions
    )

    return create_quiz(db, quiz_data, current_user.id)