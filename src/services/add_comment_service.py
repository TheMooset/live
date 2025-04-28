from api.schemas.add_comment import AddComment
from config.enums import BanTypeEnums, ErrorCodeEnums
from data.repositories.postgres.comments import CommentRepository
from data.repositories.postgres.room_participant import RoomParticipantRepository
from data.repositories.postgres.room_ban import RoomBanRepository
from data.utils.query_utils import QueryFilter
from services.base_service import BaseService


class AddCommentService(BaseService):
    def __init__(self, model: AddComment, user_id: int):
        super().__init__()
        self.model = model
        self.user_id = user_id

        self.comment_repository = CommentRepository()
        self.room_participant_repository = RoomParticipantRepository()
        self.room_ban_repository = RoomBanRepository()

    def validate(self):
        check_participant = self.room_participant_repository.exist_entity_by_query_filters(query_filters=[
            QueryFilter(key="room_id", value=self.model.room_id),
            QueryFilter(key="device_id", value=self.model.device_id)
        ])

        if check_participant is False:
            self.add_error('شما هنوز وارد این پخش زنده نشده اید')
            return

        if self.room_ban_repository.check_user_is_ban(self.model.room_id, self.model.device_id,
                                                      [BanTypeEnums.add_comment.value], self.user_id):
            self.add_error(message='شما امکان فرستادن پیام در این پخش زنده را ندارید',
                           error_code=ErrorCodeEnums.user_is_ban.value)

    def process(self):
        self.comment_repository.transaction.begin()
        self.comment_repository.transaction.add_entity({
            'user_id': self.user_id,
            'room_id': self.model.room_id,
            'comment': self.model.comment,
        })
        self.comment_repository.transaction.save_changes()

        return {'result': True}
