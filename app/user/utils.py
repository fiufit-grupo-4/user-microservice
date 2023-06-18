from bson import ObjectId as BaseObjectId


class ObjectIdPydantic(str):
    """Creating a ObjectId class for pydantic models."""

    @classmethod
    def validate(cls, value):
        """Validate given str value to check if good for being ObjectId."""
        try:
            return BaseObjectId(str(value))
        except Exception as e:
            raise ValueError("Not a valid user ID") from e

    @classmethod
    def __get_validators__(cls):
        yield cls.validate


# Metrics actions
USER_EDIT = "user_edit"
SIGNUP = "signup"
GOOGLE_SIGNUP = "google_signup"
BLOCK = "block"
UNBLOCK = "unblock"
LOGIN = "login"
GOOGLE_LOGIN = "google_login"
PASSWORD_EDIT = "password_reset"
