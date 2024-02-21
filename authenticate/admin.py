from authenticate.user import User


def verify_permissions(user: User) -> bool:
    return user.is_authenticated() and \
        user.is_active() and \
        not user.is_anonymous() and \
        user.account_type == 'google' and \
        user.admin
