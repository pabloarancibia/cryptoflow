import jwt
import datetime
import bcrypt

# Configuration
SECRET_KEY = "super_secret_key_for_week_5"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password, hashed_password):
    """
    Checks if the plain password matches the hashed password.
    Bcrypt requires bytes, so we .encode('utf-8').
    """
    # Ensure inputs are bytes
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')

    return bcrypt.checkpw(plain_password, hashed_password)


def get_password_hash(password):
    """
    Hashes a password with a random salt.
    """
    # bcrypt.hashpw returns bytes, we decode to string for storage
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt