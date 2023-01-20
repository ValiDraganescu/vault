from logger import timed_log
from typing import Tuple, Optional

from nacl.public import PrivateKey, PublicKey, SealedBox

class SecurityManager:

    def __init__(self):
        pass

    def __adjust_to_length(self, data: str, length: int, padding_data: Optional[str] = None) -> str:
        i = 0
        while len(data) < length:
            padding = padding_data if padding_data else data[i]
            data += padding
            i += 1
            if i == len(data):
                i = 0
        return data

    @timed_log(show_time=True)
    def create_key_pair(self, email: str, password: str) -> Tuple[PrivateKey, PublicKey]:
        adjusted_password = self.__adjust_to_length(password + email, 32)
        seed = bytes(adjusted_password, "utf-8")[0:32]
        private_key = PrivateKey.from_seed(seed)
        public_key = private_key.public_key
        return (private_key, public_key)

    @timed_log(show_time=True)
    def encrypt(self, public_key: PublicKey, data: str) -> bytes:
        try:
            box = SealedBox(public_key)
            # data = self.__adjust_to_length(data, 48, " ")
            return box.encrypt(bytes(data, 'utf-8'))
        except Exception as e:
            print(f'Error: {e}')
            return None

    @timed_log(show_time=True)
    def decrypt(self, private_key: PrivateKey, data: str) -> bytes:
        try:
            box = SealedBox(private_key)
            return box.decrypt(bytes(data))
        except Exception as e:
            print(f'Error: {e}')
            return None


    