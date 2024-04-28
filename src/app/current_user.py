from core.security import Key, key_to_string


class CurrentUser:
    """store the information of the current user"""
    def __init__(self, key: Key = None):
        self.key = key

    def get_pubkey(self):
        return key_to_string(self.key.public_key)
