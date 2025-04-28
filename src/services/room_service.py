from livekit import room, RoomServiceClient, models
from livekit._proto.livekit_egress_pb2 import S3Upload, RoomCompositeEgressRequest, EncodedFileOutput, MP4
from livekit._proto.livekit_room_pb2 import RoomEgress

from config import config


class RoomManagementService(RoomServiceClient):
    def __init__(self):
        super().__init__(
            host=config.LIVEKIT_HOST_URL,
            api_key=config.LIVEKIT_API_KEY,
            api_secret=config.LIVEKIT_API_SECRET
        )

    def create_custom_room(self, name: str, metadata: str, empty_timeout: int = config.ROOM_EMPTY_TIME) -> models.Room:
        ctx = self._create_context(room_create=True)
        room_egress = RoomEgress(room=RoomCompositeEgressRequest(room_name=name, file=EncodedFileOutput(
            filepath=f'{name}',
            file_type=MP4,
            s3=S3Upload(**config.file_storge)
        )))
        request = room.CreateRoomRequest(name=name, empty_timeout=empty_timeout, metadata=metadata, egress=room_egress)

        return self._client.CreateRoom(ctx=ctx, request=request)
