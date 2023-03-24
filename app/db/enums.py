import enum


class BaseEnum(enum.Enum):

    @classmethod
    def get_value_list(cls):
        return [member.value for value, member in cls.__members__.items()]

    @classmethod
    def get_members_list(cls):
        return [member for value, member in cls.__members__.items()]

    def __str__(self):
        return str.__str__(self)


class UserRoles(BaseEnum):
    admin = "Admin"
    operator = "Operator"
    user = "User"
