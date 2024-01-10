import json

from geeohdotnet.pages import find
from geeohdotnet.models import User
from django.contrib.auth.backends import BaseBackend


with open('credentials.json', 'r') as f:
    credentials = json.loads(f.read())


class AuthBackend(BaseBackend):
    def authenticate(self, request, username: str = None, password: str = None) -> User | None:
        if username and password:
            account = find(lambda a: a['username'] == username, credentials['accounts'])
            if account and password == account['password']:
                user = User(username=username, password=password)
                user.id = account['id']
                return user
        return None

    def get_user(self, user_id: int) -> User | None:
        account = find(lambda a: a['id'] == user_id, credentials['accounts'])
        if account:
            user = User(username=account['username'], password=account['password'])
            user.id = account['id']
            return user
        return None
