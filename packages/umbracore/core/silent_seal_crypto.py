import os
import json
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pathlib import Path

import subprocess
import hashlib

def get_hardware_id() -> str:
    """Retrieves the machine's hardware UUID to lock the encryption key."""
    try:
        if os.name == 'nt':
            output = subprocess.check_output("wmic csproduct get uuid", shell=True, stderr=subprocess.DEVNULL)
            hwid = output.decode().split('\n')[1].strip()
            if hwid: return hwid
    except Exception:
        pass
    import uuid
    return str(uuid.getnode())

class CryptoEngine:
    """
    💎 VESPERA Military-Grade AES-256 Encryption Engine
    Features "Silent Seal" Hardware-Locked Encryption.
    """
    def __init__(self, key_path: Path):
        self.key_path = key_path
        self._key = self._load_or_generate_key()
        self.aesgcm = AESGCM(self._key)

    def _load_or_generate_key(self) -> bytes:
        hwid = get_hardware_id()
        if self.key_path.exists():
            with open(self.key_path, 'rb') as f:
                salt = base64.b64decode(f.read())
        else:
            salt = os.urandom(16)
            self.key_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.key_path, 'wb') as f:
                f.write(base64.b64encode(salt))
        
        # Derive a 256-bit key from the HWID and the random salt
        return hashlib.pbkdf2_hmac('sha256', hwid.encode('utf-8'), salt, 100000, 32)

    def encrypt_data(self, data: dict) -> bytes:
        """Encrypts a Python dictionary to AES-256-GCM bytes."""
        nonce = os.urandom(12) # 96-bit nonce
        json_bytes = json.dumps(data).encode('utf-8')
        ciphertext = self.aesgcm.encrypt(nonce, json_bytes, None)
        # Prepend nonce to ciphertext for decryption
        return nonce + ciphertext

    def decrypt_data(self, encrypted_bytes: bytes) -> dict:
        """Decrypts AES-256-GCM bytes back to a Python dictionary."""
        try:
            nonce = encrypted_bytes[:12]
            ciphertext = encrypted_bytes[12:]
            decrypted_json_bytes = self.aesgcm.decrypt(nonce, ciphertext, None)
            return json.loads(decrypted_json_bytes.decode('utf-8'))
        except Exception as e:
            # If decryption fails (corrupt or wrong key), return empty state safely
            print(f"[CryptoEngine] Decryption failed: {e}")
            return {}

# Singleton instance to be injected
from core.paths import get_data_dir
engine = CryptoEngine(get_data_dir() / "vespera_aes256.key")
