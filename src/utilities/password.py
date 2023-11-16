from passlib.hash import pbkdf2_sha256 as hashing


def hash_password(password) -> str:
    """
    Hashes the given password using PBKDF2-SHA256 algorithm.

    Parameters:
        password (str): The password to be hashed.

    Returns:
        str: The hashed password.

    """
    return hashing.hash(password)


def verify_password(password, hashed) -> bool:
    """
    Verify if a password matches a hashed password.

    Parameters:
        password (str): The password to be verified.
        hashed (str): The hashed password to compare against.

    Returns:
        bool: True if the password matches the hashed password, False otherwise.
    """
    return hashing.verify(password, hashed)