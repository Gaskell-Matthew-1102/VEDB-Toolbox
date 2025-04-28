# written by brian
# just to have this

from flask_login import current_user

# checks if user is logged in
def is_logged_in() -> bool:
    return current_user.is_authenticated
