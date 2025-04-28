from pydantic import BaseSettings


class Settings(BaseSettings):
    debug = True
    app_title = "live_shopping"
    log_level = "INFO"
    sentry_dsn = "https://9aa3fdbad9f84031936318d637704843@sentry.basalam.com/288"

    # postgres_user = "backdev"
    # postgres_pass = "ineedapassword"
    # postgres_host = "185.142.159.181"
    # postgres_port = "60502"
    # postgres_database = "basalam.ir"

    postgres_user = "score_system_r"
    postgres_pass = '8j%y;c=~f/+<*}>fCBWaumg;EDA^3Z`@8\_/N&y.'
    postgres_host = "gw.basalam.com"
    postgres_port = "12348"
    postgres_database = "basalam.ir"

    postgres_live_user = "dev_m_chavoshizade_user"
    postgres_live_pass = "FbJsy43G8as0jHqTFOO9jhveRSbzIwTglh1U6q1o167FxubYAswPPKeK8k2T"
    postgres_live_host = "prod-live-shopping-psql-postgresql-ha.prod-live-shopping.svc.cluster.local"
    postgres_live_port = "5432"
    postgres_live_database = "live_shopping"

    LIVEKIT_API_KEY = "APIY4q5oopTUsoF"
    LIVEKIT_API_SECRET = "od1KeQQeEsj8KUboWEdIH7WjIqnTMHLGRyOIKA0bebvA"
    LIVEKIT_HOST_URL = "https://livekit.basalam.dev"
    NEXT_PUBLIC_LIVEKIT_URL = "wss://livekit.basalam.dev"
    ROOM_EMPTY_TIME = 20 * 60

    file_storge = {
        'endpoint': 'https://tools-rgw.bk0.basalam.dev',
        'secret': 'QK6aZcqP0F7LGildc4OOtKTCEKbdCZYyrxWPLWN5',
        'access_key': 'ZCBDGQ8ULDGY0RF96671',
        'bucket': 'live',
        'region': 'ap-southeast-1',
        'force_path_style': True,
    }

    core_url = 'https://core.basalam.com'
    statics_url = 'https://statics.basalam.com'

    class Config:
        case_sensitive = False
        env_file = '../.env'
        env_file_encoding = 'utf-8'


config = Settings()
