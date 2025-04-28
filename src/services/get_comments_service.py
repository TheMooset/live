from data.repositories.postgres.comments import CommentRepository
from services.base_service import BaseService
from services.microservices.core import CoreService


class GetCommentsService(BaseService):
    def __init__(self, room_id: int, limit: int, offset: int):
        super().__init__()
        self.room_id = room_id
        self.limit = limit
        self.offset = offset
        self.core_service = CoreService()
        self.comment_repository = CommentRepository()

    def validate(self):
        pass

    def process(self):
        users = {}
        comments = self.comment_repository.get_room_comments(room_id=self.room_id, limit=self.limit, offset=self.offset)
        if comments:
            users = self.core_service.get_users_data([a['user_id'] for a in comments])

        for comment in comments:
            comment['user'] = users[comment['user_id']]

        return {'comments': comments}
