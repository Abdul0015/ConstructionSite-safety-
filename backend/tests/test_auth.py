import uuid
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)

def test_password_hashing():
    password = "SuperSecretPassword123!"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False

def test_jwt_token_generation_and_decoding():
    user_id = uuid.uuid4()
    role = "admin"

    access_token = create_access_token(subject=user_id, role=role)
    refresh_token = create_refresh_token(subject=user_id, role=role)

    payload_access = decode_token(access_token)
    assert payload_access["sub"] == str(user_id)
    assert payload_access["role"] == "admin"
    assert payload_access["type"] == "access"

    payload_refresh = decode_token(refresh_token)
    assert payload_refresh["sub"] == str(user_id)
    assert payload_refresh["role"] == "admin"
    assert payload_refresh["type"] == "refresh"

if __name__ == "__main__":
    test_password_hashing()
    test_jwt_token_generation_and_decoding()
    print("ALL AUTH UNIT TESTS PASSED SUCCESSFULLY!")
