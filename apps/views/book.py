from django.db.models import Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.models import Book
from apps.serializers import BookModelSerializer, BookSearchModelSerializer


@extend_schema(
    tags=['Book'])
class BookSetView(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookModelSerializer

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
        return Response({"message": "Book deleted"}, status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=['Book'])
class BookSearchListAPIView(ListAPIView):
    serializer_class = BookSearchModelSerializer

    def get_queryset(self):
        query = self.request.query_params.get('search_value')
        if query:
            return Book.objects.filter(
                Q(name__icontains=query) | Q(level__icontains=query)
            )
        return Book.objects.none()

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
    tags=['Book']
)
class BookGetAPIView(APIView):
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if pk:
            book = get_object_or_404(Book, pk=pk)
            serializer = BookModelSerializer(book)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "ID (pk) topilmadi."},
                status=status.HTTP_400_BAD_REQUEST
            )