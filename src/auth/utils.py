from passlib.context import CryptContext
import bcrypt, hashlib
from datetime import datetime, timedelta
import jwt
from src.config import Config
import uuid
import logging


jwt_secret_key = Config.JWT_SECRET 
jwt_algorithm = Config.JWT_ALGORITHM

ACCESS_TOKEN_EXPIRY = 3600

"""using only passlib"""
"""password_context = CryptContext(
    schemes=['bcrypt']
)
def generate_password_hash(password: str) -> str:
    hash = password_context.hash(password)
    return hash

def verify_password(password: str, hash: str) -> bool:
    return password_context.verify(password, hash)
    """


"""using bcrypt directly"""

def hash_password(password: str) -> str:
    digest = hashlib.sha256(password.encode('utf-8')).digest()
    hashed = bcrypt.hashpw(digest, bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    digest = hashlib.sha256(password.encode('utf-8')).digest()
    return bcrypt.checkpw(digest, hashed.encode('utf-8'))

def create_access_token(user_data: dict, expiry: timedelta | None = None, refresh: bool = False):
    payload = {}

    payload['user'] = user_data

    if expiry is None:
        expiry = timedelta(seconds=ACCESS_TOKEN_EXPIRY)
    payload['exp'] = datetime.now() + expiry 

    payload['jti'] = str(uuid.uuid4())
    payload['refresh'] = refresh

    token = jwt.encode(
        payload=payload,
        key=jwt_secret_key,
        algorithm=jwt_algorithm
    )
    return token

def decode_token(token: str) -> dict | None:
    try:
        token_data = jwt.decode(
            jwt=token,
            key=jwt_secret_key,
            algorithms=[jwt_algorithm]
        )
        return token_data
    except jwt.PyJWTError as e:
        logging.exception(e)
        return None