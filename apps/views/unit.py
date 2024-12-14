from django.db.models import Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.models import Unit
from apps.serializers import UnitModelSerializer
from apps.serializers import UnitSearchModelSerializer, UnitFilterModelSerializer


@extend_schema(
    tags=['Unit'])
class UnitSetView(ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitModelSerializer

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
        return Response({"message": "Unit deleted"}, status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=['Unit']
)
class UnitSearchListAPIView(ListAPIView):
    queryset = Unit.objects.all()
    serializer_class = UnitSearchModelSerializer

    def get_queryset(self):
        value = self.request.query_params.get('search_value').strip()
        query = super().get_queryset()
        # query = Unit.objects.all()
        if value:
            query = query.filter(
                Q(name__icontains=value) | Q(book__name__icontains=value) | Q(book__level__icontains=value) |  Q(unit_num=value)
            )
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
    tags=['Unit']
)
class UnitFilterListAPIView(ListAPIView):
    queryset = Unit.objects.all()
    serializer_class = UnitFilterModelSerializer

    def get_queryset(self):
        query = super().get_queryset()
        book_id = self.kwargs.get("book_id")
        return query.filter(book_id=book_id)

@extend_schema(
        tags=['Unit']
    )
class UnitGetAPIView(APIView):
        def get(self, request, *args, **kwargs):
            pk = kwargs.get('pk')
            if pk:
                unit = get_object_or_404(Unit, pk=pk)
                serializer = UnitModelSerializer(unit)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "ID (pk) topilmadi."},
                    status=status.HTTP_400_BAD_REQUEST
                )
