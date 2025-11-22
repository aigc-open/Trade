
from utils.ossUtils.oss import OSSManager
from django.conf import settings
from enum import Enum

class EnumDesc:
    @classmethod
    def choice(cls, e: Enum):
        return [(value.value, name) for name, value in
                e.__members__.items()]

    @classmethod
    def help_text(cls, e: Enum):
        return [value for name, value in
                e.__members__.items()]


s3 = OSSManager(endpoint_url=settings.AWS_ENDPOINT_URL, aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY, region_name=settings.AWS_REGION_NAME)
