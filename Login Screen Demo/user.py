class User:

#Reference: https://flask-login.readthedocs.io/en/latest/#your-user-class

    username = ""
    password = ""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def is_authenticated(usrnm: str):
        #For this, need to change the value to something associated to database (I think)
        if usrnm == 'admin':
            return True
        else:
            return False

    def is_active(self, usrnm: str):
        if self.is_authenticated(usrnm):
            return True
        else:
            return False

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username