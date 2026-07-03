from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.quiz import Quiz, Question
from app.schemas.quiz import QuizCreate, QuizUpdate, QuestionCreate
from uuid import UUID


def create_quiz(db: Session, quiz_data: QuizCreate, creator_id: UUID) -> Quiz:
    """Create a new quiz with optional questions."""

    # Create the quiz
    new_quiz = Quiz(
        title=quiz_data.title,
        description=quiz_data.description,
        creator_id=creator_id,
        difficulty=quiz_data.difficulty,
        is_public=quiz_data.is_public,
        time_limit=quiz_data.time_limit,
        generation_source="manual",
        status="draft"
    )
    db.add(new_quiz)
    db.flush()  # Gets the quiz ID without committing yet

    # Add questions if provided
    for q in quiz_data.questions:
        question = Question(
            quiz_id=new_quiz.id,
            question_text=q.question_text,
            options=q.options,
            correct_answer=q.correct_answer,
            explanation=q.explanation,
            difficulty=q.difficulty,
            order_index=q.order_index,
            points=q.points
        )
        db.add(question)

    db.commit()
    db.refresh(new_quiz)
    return new_quiz


def get_my_quizzes(db: Session, creator_id: UUID) -> list:
    """Get all quizzes created by a specific user."""
    return db.query(Quiz).filter(
        Quiz.creator_id == creator_id
    ).order_by(Quiz.created_at.desc()).all()


def get_quiz_by_id(db: Session, quiz_id: UUID, user_id: UUID) -> Quiz:
    """
    Get a single quiz by ID.
    Raises 404 if not found.
    Raises 403 if user doesn't own it and it's not public.
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()

    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )

    # Allow access if owner or if quiz is public
    if quiz.creator_id != user_id and not quiz.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this quiz"
        )

    return quiz


def update_quiz(
    db: Session,
    quiz_id: UUID,
    quiz_data: QuizUpdate,
    user_id: UUID
) -> Quiz:
    """Update quiz details. Only owner can update."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()

    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )

    if quiz.creator_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't own this quiz"
        )

    # Only update fields that were actually provided
    update_data = quiz_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(quiz, field, value)

    db.commit()
    db.refresh(quiz)
    return quiz


def delete_quiz(db: Session, quiz_id: UUID, user_id: UUID) -> None:
    """Delete a quiz. Only owner can delete."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()

    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )

    if quiz.creator_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't own this quiz"
        )

    db.delete(quiz)
    db.commit()


def add_question(
    db: Session,
    quiz_id: UUID,
    question_data: QuestionCreate,
    user_id: UUID
) -> Question:
    """Add a question to a quiz. Only owner can add questions."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()

    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )

    if quiz.creator_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't own this quiz"
        )

    question = Question(
        quiz_id=quiz_id,
        question_text=question_data.question_text,
        options=question_data.options,
        correct_answer=question_data.correct_answer,
        explanation=question_data.explanation,
        difficulty=question_data.difficulty,
        order_index=question_data.order_index,
        points=question_data.points
    )

    db.add(question)
    db.commit()
    db.refresh(question)
    return question


def delete_question(
    db: Session,
    quiz_id: UUID,
    question_id: UUID,
    user_id: UUID
) -> None:
    """Delete a question. Only quiz owner can delete."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()

    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )

    if quiz.creator_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't own this quiz"
        )

    question = db.query(Question).filter(
        Question.id == question_id,
        Question.quiz_id == quiz_id
    ).first()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    db.delete(question)
    db.commit()