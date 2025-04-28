from fastapi import APIRouter, Depends

from api import middlewares
from api.schemas.add_comment import AddComment
from services.add_comment_service import AddCommentService

router = APIRouter()


@router.post("")
def add_comment(comment: AddComment, user_id=Depends(middlewares.get_user_id_from_token)):
    return AddCommentService(model=comment, user_id=user_id).execute()
