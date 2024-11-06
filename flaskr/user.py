class User:

#Reference: https://flask-login.readthedocs.io/en/latest/#your-user-class


    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password


# This property should return True if the user is authenticated, i.e. they have provided valid credentials. (Only authenticated users will fulfill the criteria of login_required.)
    def is_authenticated(usrnm: str) -> bool:
        #For this, need to change the value to something associated to database (I think)
        if usrnm == 'admin':
            return True
        else:
            return False
#This property should return True if this is an active user - in addition to being authenticated, they also have activated their account, not been suspended, or any condition your application has for rejecting an account. Inactive accounts may not log in (without being forced of course).
    def is_active(self, usrnm: str) -> bool:
        if self.is_authenticated(usrnm):
            return True
        else:
            return False

    def is_anonymous(self) -> bool:
        return False

    def get_id(self) -> str:
        return self.username