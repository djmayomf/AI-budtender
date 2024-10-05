import bcrypt

def hash_password(password):
    # Generate a salt
    salt = bcrypt.gensalt()
    # Hash the password with the salt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

# Example usage
password = "my_secure_password"
hashed_password = hash_password(password)
print(hashed_password)
def check_password(hashed_password, user_password):
    # Check if the provided password matches the hashed password
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password)

# Example usage
is_valid = check_password(hashed_password, "my_secure_password")
print(is_valid)  # True if the password matches, False otherwise