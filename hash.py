import bcrypt

# Generate hash for "password"
password = "password"
salt = bcrypt.gensalt()
password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
print(f"Hash for 'password': {password_hash.decode('utf-8')}")

# Test the existing hash
existing_hash = "$2b$12$8y1N.Vo1kFvJJZxS3vXkN.vxHo.UiS9f7yPdQBBwxV9YZS0L4mJti"
is_correct = bcrypt.checkpw("password".encode('utf-8'), existing_hash.encode('utf-8'))
print(f"Does existing hash match 'password'? {is_correct}")