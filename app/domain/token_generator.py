import uuid


class UUIDTokenGenerator:
    def generate_session_token(self): return uuid.uuid4()
