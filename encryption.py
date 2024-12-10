import gnupg
import os
import sys
# sys.path.insert(0, "/glue/lib/")  # หรือ path ที่คุณ unzip libraries
# sys.path.insert(0, "/glue/lib/Crypto/")

import base64
from io import BytesIO

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


class Encryption:
    def __init__(self):
        self.iv = b"0123456789ABCDEF"
        self.gpg = gnupg.GPG()

    def decrypt_gpg_stream(self, private_key: str, passphrase: str, encrypted_stream: BytesIO) -> BytesIO:
        try:
            encrypted_stream.seek(0)
            # Import public key
            import_result = self.gpg.import_keys(private_key)
            if not import_result:
                print("import private key failed")
                return None
            
            decrypted_data = self.gpg.decrypt(encrypted_stream.read(), passphrase=passphrase)
            if decrypted_data.ok:
                return BytesIO(decrypted_data.data)  # ส่งคืนข้อมูลที่ถอดรหัสแล้วเป็น stream
            else:
                raise ValueError(f"decrypt failed: {decrypted_data.stderr}")
        except Exception as e:
            raise e

    def encrypt_gpg_stream(self, public_key: str, plain_stream: BytesIO) -> BytesIO:
        try:
            plain_stream.seek(0)
            # Import public key
            import_result = self.gpg.import_keys(public_key)
            if not import_result:
                raise ValueError("Import public key failed")
            
            # Encrypt the data in binary format
            encrypted_data = self.gpg.encrypt(
                plain_stream.read(),
                recipients=import_result.fingerprints,
                always_trust=True,
                armor=False  # ใช้ Binary mode
            )
            if encrypted_data.ok:
                return BytesIO(encrypted_data.data)
            else:
                raise ValueError(f"Encryption failed: {encrypted_data.stderr}")
        except Exception as e:
            raise e


