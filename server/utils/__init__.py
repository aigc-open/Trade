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