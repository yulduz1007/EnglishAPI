from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.db.models import CharField, TextChoices, PositiveIntegerField, EmailField, Model, ImageField, ForeignKey, \
    CASCADE, FileField, TextField, SET_NULL, SmallIntegerField, DateTimeField, ManyToManyField
from django.db.models import Model

from apps import apps


# Create your models here.
class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):

        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )
        email = GlobalUserModel.normalize_username(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    class UserRole(TextChoices):
        ADMIN = "admin", "Admin"
        USER = "user", "User"

    objects = CustomUserManager()
    username = None
    REQUIRED_FIELDS = []
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    email = EmailField(unique=True)
    role = CharField(max_length=255, choices=UserRole.choices, default=UserRole.USER)
    rank = PositiveIntegerField(default=0)


class Book(Model):
    name = CharField(max_length=255, unique=True)
    level = CharField(max_length=255)
    images = ImageField(upload_to="book/", null=True, blank=True)




class Vocab(Model):
    uz = CharField(max_length=255)
    en = CharField(max_length=255)
    audio = FileField(upload_to='vocab/audio/')
    unit = ForeignKey('apps.Unit', CASCADE, related_name='vocabs')


class TestSection(Model):
    title = CharField(max_length=255)
    description = TextField()


class Test(Model):
    class OptionTest(TextChoices):
        A = 'a', "A"
        B = 'b', "B"
        C = 'c', "C"
        D = 'd', "D"

    question = TextField()
    a = CharField(max_length=255)
    b = CharField(max_length=255)
    c = CharField(max_length=255)
    d = CharField(max_length=255)
    right = CharField(max_length=255, choices=OptionTest.choices)
    section_test = ForeignKey('apps.TestSection', CASCADE, related_name='tests')


class Unit(Model):
    name = CharField(max_length=255)
    unit_num = CharField(max_length=255,default=1)
    book = ForeignKey('apps.Book', CASCADE, related_name='units')


class Result(Model):
    class ResultType(TextChoices):
        TEST = 'test', 'Test'
        TEXT = 'text', 'Text'
        AUDIO = 'audio', 'Audio'
        LISTENING = 'listening', 'Listening'
        WRITING = 'writing', 'Writing'
        READING = 'reading', 'Reading'
        SPEAKING = 'speaking', 'Speaking'

    user_id = ForeignKey('apps.User', SET_NULL, null=True, blank=True, related_name='results')
    correct = SmallIntegerField(default=0)
    incorrect = SmallIntegerField(default=0)
    quantity = SmallIntegerField()
    type = CharField(max_length=255, choices=ResultType.choices)
    created_at = DateTimeField(auto_now_add=True)
    units = ManyToManyField('apps.Unit', related_name='results')
    test_sections = ManyToManyField('apps.TestSection', related_name='results')
