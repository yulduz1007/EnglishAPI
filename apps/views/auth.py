import random
from datetime import timedelta
from http import HTTPStatus

import redis
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.models import User
from apps.serializers import EmailCodeSerializer, \
    UserRegisterSerializer
from apps.serializers import EmailSerializer, UserSerializer
from apps.tasks import send_email


# Create your views here.
@extend_schema(tags=['Auth'])
class CustomTokenObtainPairView(TokenObtainPairView):
    pass


@extend_schema(tags=['Auth'])
class CustomTokenRefreshView(TokenRefreshView):
    pass


@extend_schema(
    request=EmailSerializer,
    tags=['Auth'])
class SendEmailAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        query = User.objects.filter(email=email)
        if not query.exists():
            User.objects.create(email=email, is_active=False)
        elif query.first().is_active:
            raise ValidationError("Bunday email mavjud!", HTTPStatus.BAD_REQUEST)

        code = str(random.randrange(10 ** 4, 10 ** 5))
        send_email.delay(email, code)
        r = redis.Redis()
        r.mset({email: code})
        r.expire(email, time=timedelta(minutes=5))
        return Response({"message": "Success"}, status=HTTPStatus.OK)


@extend_schema(tags=['Auth'])
class CodeUserAPIView(APIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        code = request.data.get('code')
        r = redis.Redis(decode_responses=True)
        verify_code = r.mget(email)[0]
        if verify_code != code:
            raise ValidationError("Not Match Code", HTTPStatus.BAD_REQUEST)
        User.objects.filter(email=email).update(is_active=True)
        return Response({"message": True}, HTTPStatus.OK)


@extend_schema(
    request=EmailCodeSerializer,
    tags=['Auth'])
class CheckPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        code_input = request.data.get('code')
        r = redis.Redis(decode_responses=True)
        code = r.mget(email)[0]
        if code_input == code:
            return Response({"message": "Password match"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Wrong code"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Auth'])
class RegisterUserCreateAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        email = data.get('email')
        password = data.get('password')
        query = User.objects.filter(email=email)
        if not query.exists():
            raise ValidationError("Tasdiqlanmagan email kiritildi!", HTTPStatus.BAD_REQUEST)
        elif not query.first().is_active:
            raise ValidationError("Tasdiqlanmagan email kiritildi!", HTTPStatus.BAD_REQUEST)
        elif query.exists() and not query.first().password:
            query.update(password=password)
        else:
            raise ValidationError('Already exists email !')
        return Response({'response': "Success register"}, HTTPStatus.CREATED)
