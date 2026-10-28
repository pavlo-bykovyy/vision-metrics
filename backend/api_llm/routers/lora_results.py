from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from shared import schemas, models
from shared.dependencies import verify_token
from shared.database import get_db

router = APIRouter(prefix="/lora/results", tags=["LoRA Results"])

@router.get("/{result_id}", response_model=schemas.EvaluationResultResponse)
async def get_evaluation_result(
        result_id: int,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    """
    Retrieves a specific evaluation generation result by its ID.

    Args:
        result_id (int): The unique identifier of the evaluation result.
        db (Session): The database session dependency.
        token (str): The authorization token dependency.

    Returns:
        schemas.EvaluationResultResponse: The requested evaluation result object.

    Raises:
        HTTPException: If the evaluation result is not found in the database (404).
    """
    result = db.query(models.EvaluationResult).filter(models.EvaluationResult.id == result_id).first()

    if not result:
        raise HTTPException(status_code=404, detail="Evaluation result not found")

    return result


@router.delete("/{result_id}")
async def delete_evaluation_result(
        result_id: int,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    """
    Deletes a specific evaluation generation result from the database by its ID.

    Args:
        result_id (int): The unique identifier of the evaluation result to delete.
        db (Session): The database session dependency.
        token (str): The authorization token dependency.

    Returns:
        dict: A success message confirming the deletion.

    Raises:
        HTTPException: If the evaluation result is not found (404) or if the database deletion fails (500).
    """
    result = db.query(models.EvaluationResult).filter(models.EvaluationResult.id == result_id).first()

    if not result:
        raise HTTPException(status_code=404, detail="Evaluation result not found")

    try:
        db.delete(result)
        db.commit()
        return {"message": f"Result {result_id} deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete result: {str(e)}")