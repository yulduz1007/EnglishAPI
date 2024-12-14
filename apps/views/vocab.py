import json
from http import HTTPStatus
from random import random, shuffle
import random

from django.db.models import Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from redis import Redis
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, ListAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.models import Vocab, Result, Unit
from apps.serializers import VocabFilterModelSerializer, VocabSearchModelSerializer, VocabTryWordSerializer, \
    VocabCheckWordSerializer, VocabTestSerializer
from apps.serializers import VocabModelSerializer, VocabAudioModelSerializer


@extend_schema(tags=['vocab'])
class VocabSetView(ModelViewSet):
    queryset = Vocab.objects.all()
    serializer_class = VocabModelSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({"message": "Vocab deleted"}, status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["vocab"])
class VocabAudioCreateAPIView(CreateAPIView):
    queryset = Vocab.objects.all()
    serializer_class = VocabAudioModelSerializer


@extend_schema(
    tags=['vocab']
)
class VocabFilterListAPIView(ListAPIView):
    queryset = Vocab.objects.all()
    serializer_class = VocabFilterModelSerializer

    def get_queryset(self):
        query = super().get_queryset()
        unit_id = self.kwargs.get("unit_id")
        return query.filter(unit_id=unit_id)


@extend_schema(
    tags=['vocab']
)
class VocabSearchListAPIView(ListAPIView):
    queryset = Vocab.objects.all()
    serializer_class = VocabSearchModelSerializer

    def get_queryset(self):
        value = self.request.query_params.get('search_value')
        query = super().get_queryset()
        query = query.filter(Q(uz__icontains=value) | Q(en__icontains=value))
        return query

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='search_value',
                type=OpenApiTypes.STR,
                required=True
            ),
        ])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(
    tags=['vocab']
)
class VocabGetAPIView(APIView):
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if pk:
            vocab = get_object_or_404(Vocab, pk=pk)
            serializer = VocabModelSerializer(vocab)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "ID (pk) topilmadi."},
                status=status.HTTP_400_BAD_REQUEST
            )


# =================================Vocab-try==========================================

class VocabTryWordAPIView(APIView):
    @extend_schema(
        request=VocabTryWordSerializer,
        responses=VocabFilterModelSerializer,
        tags=['vocab']
    )
    def post(self, request):
        unit_id = request.data.get('unit_id')
        redis = Redis()
        vocabs = list(Vocab.objects.filter(unit_id=unit_id).values_list('id', flat=True))
        if not vocabs:
            raise ValidationError("Vocab not found", HTTPStatus.BAD_REQUEST)
        random_vocab = random.choice(vocabs)
        vocabs.remove(random_vocab)
        data = {"correct": 0, "incorrect": 0, "unit_id": unit_id, "vocabs_id": vocabs, "finish": False}
        redis.set(request.user.id, json.dumps(data))
        vocab = Vocab.objects.filter(id=random_vocab).first()
        data = VocabFilterModelSerializer(instance=vocab).data
        return Response(data=data, status=status.HTTP_200_OK)


class VocabCheckWordAPIView(APIView):
    @extend_schema(
        request=VocabCheckWordSerializer,
        responses=VocabFilterModelSerializer,
        tags=['vocab']
    )
    def post(self, request):
        vocab_id = request.data.get('vocab_id')
        word = request.data.get('word')
        vocab = Vocab.objects.filter(id=vocab_id).first()
        is_correct = vocab.en.lower() == word.lower()
        redis = Redis(decode_responses=True)
        data = redis.get(request.user.id)
        data = json.loads(data)
        data["correct"] = is_correct
        data["incorrect"] = not is_correct
        vocabs_id = data["vocabs_id"]
        if not vocabs_id:
            data['finish'] = True
            data['last_question'] = is_correct
            redis.delete(request.user.id)
            # Result.objects.create()
            return Response(data, status=status.HTTP_200_OK)
        r = random.choice(vocabs_id)
        vocabs_id.remove(r)
        redis.set(request.user.id, json.dumps(data))
        vocab = Vocab.objects.filter(id=r).first()
        data = VocabFilterModelSerializer(instance=vocab).data
        data['finish'] = False
        data['last_question'] = is_correct
        return Response(data, status=status.HTTP_200_OK)


# =====================================Vocab-test==============================================

class VocabTestAPIView(APIView):
    @extend_schema(
        request=VocabTestSerializer,
        responses=VocabModelSerializer,
        tags=['vocab']
    )
    def post(self, request):
        type = request.data.get('type')
        quantity = int(request.data.get('quantity'))
        units = request.data.get('units').split(",")
        redis = Redis(decode_responses=True)
        vocabs = list(Vocab.objects.filter(unit_id__in=units).values_list('id', flat=True))
        shuffle(vocabs)
        vocabs = vocabs[:quantity]
        if not vocabs:
            raise ValidationError("Vocab not found", HTTPStatus.BAD_REQUEST)
        random_vocab = random.choice(vocabs)
        vocabs.remove(random_vocab)
        r_data = {"correct": 0, "quantity": quantity, "incorrect": 0, "units": units, "vocabs_id": vocabs,
                  "finish": False, "type": type}
        redis.set(request.user.id, json.dumps(r_data))
        vocab = Vocab.objects.filter(id=random_vocab).first()
        data = VocabModelSerializer(instance=vocab).data
        data['type'] = r_data.get('type')
        data['finish'] = False
        return Response(data=data, status=status.HTTP_200_OK)


class VocabTestCheckAPIView(APIView):
    @extend_schema(
        request=VocabCheckWordSerializer,
        responses=VocabModelSerializer,
        tags=['vocab']
    )
    def post(self, request):
        vocab_id = request.data.get('vocab_id')
        word = request.data.get('word')
        vocab = Vocab.objects.filter(id=vocab_id).first()
        is_correct = vocab.en.lower() == word.lower()
        redis = Redis(decode_responses=True)
        r_data = redis.get(request.user.id)
        r_data = json.loads(r_data)
        r_data["correct"] = is_correct
        r_data["incorrect"] = not is_correct
        vocabs_id = r_data["vocabs_id"]
        if not vocabs_id:
            del r_data['finish']
            del r_data['vocabs_id']
            redis.delete(request.user.id)
            r_data['user'] = request.user
            units = Unit.objects.filter(id__in=r_data.get('units'))
            del r_data['units']
            instance = Result.objects.create(**r_data)
            instance.units.add(*units)
            r_data['finish'] = True
            r_data['last_question'] = is_correct
            del r_data['user']
            return Response(r_data, status=status.HTTP_200_OK)
        r = random.choice(vocabs_id)
        vocabs_id.remove(r)
        redis.set(request.user.id, json.dumps(r_data))
        vocab = Vocab.objects.filter(id=r).first()
        data = VocabModelSerializer(instance=vocab).data
        data['finish'] = False
        data['last_question'] = is_correct
        data['type'] = r_data.get('type')
        return Response(data, status=status.HTTP_200_OK)
