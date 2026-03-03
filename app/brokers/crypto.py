import logging

from cryptography.fernet import Fernet, InvalidToken

from app.config import settings

logger = logging.getLogger(__name__)

_fernet: Fernet | None = None


def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        key = settings.BROKER_TOKEN_ENCRYPTION_KEY
        if not key:
            # Generate a key at runtime if not configured (dev convenience)
            key = Fernet.generate_key().decode()
            logger.warning(
                "BROKER_TOKEN_ENCRYPTION_KEY not set — using a random key. "
                "Stored tokens will not survive restarts."
            )
        _fernet = Fernet(key.encode() if isinstance(key, str) else key)
    return _fernet


def encrypt_token(plaintext: str) -> str:
    return _get_fernet().encrypt(plaintext.encode()).decode()


def decrypt_token(ciphertext: str) -> str:
    try:
        return _get_fernet().decrypt(ciphertext.encode()).decode()
    except InvalidToken:
        logger.error("Failed to decrypt broker token — key may have changed")
        raise ValueError("Failed to decrypt broker token")
