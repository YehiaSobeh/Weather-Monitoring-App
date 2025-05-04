from app.services.user import hash_password, compare_password_with_hash

def test_hash_password():
    raw = "secret123"
    hashed = hash_password(raw)
    assert hashed != raw
    assert compare_password_with_hash(raw, hashed)
