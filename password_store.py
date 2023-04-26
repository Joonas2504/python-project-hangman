import bcrypt

# Define the plain text password
password = "hirttoukko"

# Hash the password using bcrypt
hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# Store the hashed password
password_hash = hashed_password
