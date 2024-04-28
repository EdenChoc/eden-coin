
import json
from typing import Union
from hashlib import sha256
from ecdsa.util import sigencode_der, sigdecode_der

import bip39
from ecdsa import SigningKey, VerifyingKey, BadSignatureError


def key_to_string(key: Union[SigningKey, VerifyingKey]):
    """convert key to string"""
    return key.to_string().hex()


def signing_key_from_str(key_str: str) -> SigningKey:
    """convert str to private key"""
    return SigningKey.from_string(bytes.fromhex(key_str))


def verifying_key_from_str(key_str: str) -> VerifyingKey:
    """convert str to public key"""
    return VerifyingKey.from_string(bytes.fromhex(key_str))


class Key:

    def __init__(self, private_key: SigningKey = None):
        """If no private key is provided, a random one is generated"""
        self.private_key = private_key or SigningKey.generate()
        self.public_key = self.private_key.verifying_key

    @classmethod
    def from_seed_phrase(cls, seed_phrase: str):
        """Return the private key corresponding to this seed phrase"""
        key_str = bip39.decode_phrase(seed_phrase)
        key = SigningKey.from_string(key_str)
        return cls(key)

    def get_seed_phrase(self) -> str:
        """Returns the seed phrase corresponding to this private key"""
        seed_phrase = bip39.encode_bytes(self.private_key.to_string())
        return seed_phrase

    def sign_dict(self, content: dict) -> bytes:
        """return a signature that correspond the dict"""
        content_bytes = json.dumps(content, sort_keys=True).encode()
        signature = self.private_key.sign_deterministic(
            content_bytes,
            hashfunc=sha256,
            sigencode=sigencode_der
        )
        return signature

    @classmethod
    def verify_dict(cls, content: dict, signature: bytes, pub_key: VerifyingKey) -> bool:
        """verify if the signature correspond to the dict"""
        content_bytes = json.dumps(content, sort_keys=True).encode()
        try:
            ret = pub_key.verify(signature, content_bytes, sha256, sigdecode=sigdecode_der)
            assert ret
            print("Valid signature")
            return True
        except BadSignatureError:
            print("Incorrect signature")
            return False


