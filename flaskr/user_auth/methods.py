# written by brian

# local
from flaskr.models import User

# Only the first user is admin by default, thus avoiding modifying the SQLite DB directly
def is_first_user() -> bool:
    return User.query.first() is None
