from django.contrib.auth.hashers import make_password
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import (
    Serializer, EmailField, CharField, ModelSerializer,IntegerField)

from apps.models import Book, Unit
from apps.models import Vocab
from apps.utils import generate_audio_world, generate_audio_from_excel


# =======================================AUTH============================================================
class UserSerializer(Serializer):
    email = EmailField(max_length=255)
    code = CharField(max_length=5, min_length=5)


class UserRegisterSerializer(Serializer):
    email = EmailField(max_length=255)
    password = CharField(max_length=5, min_length=5)

    def validate_password(self, value):
        return make_password(value)


class EmailSerializer(Serializer):
    email = CharField(max_length=255)


class EmailCodeSerializer(Serializer):
    code = CharField(max_length=255)
    email = EmailField()


# ==========================================BOOK==========================================================
class BookModelSerializer(ModelSerializer):
    class Meta:
        model = Book
        fields = 'id', 'name', 'level', 'images'


class BookSearchModelSerializer(ModelSerializer):
    class Meta:
        model = Book
        exclude = 'images',


# ============================================UNIT==========================================================
class UnitModelSerializer(ModelSerializer):
    class Meta:
        model = Unit
        fields = '__all__'


class UnitSearchModelSerializer(ModelSerializer):
    search_value = CharField(max_length=255, write_only=True)

    class Meta:
        model = Unit
        fields = "__all__"
        read_only_fields = "name", "unit_num", "book"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # data['book'] = Book.objects.filter(id=data.get('book')).values('id' , 'name' , 'level').first()
        data['book'] = BookModelSerializer(instance=instance.book).data
        return data


class UnitFilterModelSerializer(ModelSerializer):
    class Meta:
        model = Unit
        exclude = 'book',


# ================================================VOCAB=======================================================
class VocabModelSerializer(ModelSerializer):
    class Meta:
        model = Vocab
        exclude = ()
        extra_kwargs = {
            "id": {"read_only": True},
            "audio": {"read_only": True}
        }

    def validate(self, attrs):
        en = attrs.get('en')
        path = generate_audio_world(en)
        attrs['audio'] = path
        return attrs


class VocabAudioModelSerializer(ModelSerializer):
    class Meta:
        model = Vocab
        fields = '__all__'

    def validate(self, attrs):
        file = attrs.get("audio")
        path = generate_audio_from_excel(file)
        attrs['audio'] = path
        return attrs


class VocabFilterModelSerializer(ModelSerializer):
    class Meta:
        model = Vocab
        fields = '__all__'


class VocabSearchModelSerializer(ModelSerializer):
    class Meta:
        model = Vocab
        exclude = "audio", "unit"


class VocabTryWordSerializer(Serializer):
    unit_id = IntegerField()


class VocabCheckWordSerializer(Serializer):
    vocab_id = IntegerField()
    word = CharField()


class VocabTestSerializer(Serializer):
    type = CharField()
    quantity = IntegerField()
    units = PrimaryKeyRelatedField(
        queryset=Unit.objects.all(),
        many=True
    )
