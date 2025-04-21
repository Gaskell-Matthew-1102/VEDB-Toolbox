# written by brian

# local
from flaskr.models import User

def is_first_user() -> bool:
    # Only the first user is admin by default, thus avoiding modifying the SQLite DB directly
    # Certainly the lazy approach, but omits complex communication with the Auth0 API
    return User.query.first() is None
