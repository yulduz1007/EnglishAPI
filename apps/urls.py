from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import BookSetView, UnitSetView
from apps.views import (CheckPasswordView,
                        CodeUserAPIView,
                        SendEmailAPIView,
                        RegisterUserCreateAPIView,
                        VocabAudioCreateAPIView,
                        UnitSearchListAPIView,
                        UnitFilterListAPIView,
                        VocabSearchListAPIView,
                        VocabSetView,
                        VocabFilterListAPIView,
                        BookSearchListAPIView,
                        VocabGetAPIView,
                        BookGetAPIView,
                        UnitGetAPIView,
                        VocabCheckWordAPIView,
                        VocabTryWordAPIView,
                        VocabTestAPIView,
                        VocabTestCheckAPIView)


router = DefaultRouter()
router.register(r'books', BookSetView, basename='book')
router.register(r'units', UnitSetView, basename='unit')
router.register(r'vocabs', VocabSetView, basename='vocab')

urlpatterns = [
    path('Auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('Auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('Auth/send/mail/', SendEmailAPIView.as_view(), name='send-mail'),
    path('Auth/check/password/',CheckPasswordView.as_view(), name='check-password'),
    path('Auth/register/',RegisterUserCreateAPIView.as_view(), name='register'),
    path('Auth/send/verify',CodeUserAPIView.as_view(), name='verify'),



    path('Vocab/audio', VocabAudioCreateAPIView.as_view(), name='audio'),
    path('Vocab/search', VocabSearchListAPIView.as_view(), name='search'),
    path('Vocab/filter/<int:unit_id>', VocabFilterListAPIView.as_view(), name='filter'),
    path('Vocab/get/<int:pk>/', VocabGetAPIView.as_view(), name='vocab-detail'),
    path('Unit/vocab/try', VocabTryWordAPIView.as_view(), name='vocab-try'),
    path('Unit/vocab/check', VocabCheckWordAPIView.as_view(), name='vocab-check'),
    path('Unit/test/filter', VocabTestAPIView.as_view(), name='vocab-test'),
    path('Unit/test/check', VocabTestCheckAPIView.as_view(), name='test-check'),


    path('Unit/search', UnitSearchListAPIView.as_view(), name='search'),
    path('Unit/filter', UnitFilterListAPIView.as_view(), name='filter'),
    path('Unit/get/<int:pk>/', UnitGetAPIView.as_view(), name='get'),


    path('Book/search', BookSearchListAPIView.as_view(), name='search'),
    path('Book/get/<int:pk>/', BookGetAPIView.as_view(), name='get'),


    path('Api/', include(router.urls)),

]