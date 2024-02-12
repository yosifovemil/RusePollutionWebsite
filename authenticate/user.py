from flask_login import UserMixin, AnonymousUserMixin


class User(UserMixin):
    def __init__(self, user_dict: dict):
        self.id = user_dict['id']
        self.name = user_dict['name']
        self.email = user_dict['email']


class Anonymous(AnonymousUserMixin):
    name = u"Anonymous"
