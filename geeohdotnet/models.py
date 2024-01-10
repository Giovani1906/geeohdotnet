from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    def save(self, **kwargs):
        pass
