from flask_login import UserMixin, AnonymousUserMixin


class User(UserMixin):
    def __init__(self, user: dict):
        self.id = user['id']
        self.username = user['username']
        self.password = bytes(user['password'], encoding="UTF-8")
        self.name = user['name']
        self.photo = user['photo']
        self.active = bool(user['active'])
        self.admin = bool(user['admin'])
        self.account_type = user['accountType']

    def is_active(self):
        return self.active

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id


class Anonymous(AnonymousUserMixin):
    name = u"Anonymous"
