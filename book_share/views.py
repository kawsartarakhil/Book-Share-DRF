from .serailizer import *
from .models import *
from .filters import BookFilter
from .pagination import CustomPagination
from rest_framework.generics import ListAPIView,CreateAPIView,UpdateAPIView,RetrieveAPIView,DestroyAPIView
from rest_framework.permissions import AllowAny,IsAdminUser
from .permissions import *
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter,OrderingFilter

class categoryList(ListAPIView):
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerailizer


class categoryCreate(CreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Category.objects.all()
    serializer_class = CategorySerailizer


class categoryDetail(RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerailizer

class categoryUpdate(UpdateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Category.objects.all()
    serializer_class = CategorySerailizer


class categoryDelete(DestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Category.objects.all()
    serializer_class = CategorySerailizer



class BookList(ListAPIView):
    permission_classes = [AllowAny]
    queryset = Books.objects.filter(status="available").select_related("owner","category")
    serializer_class = BookSerailizer
    filterset_class = BookFilter
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    pagination_class = CustomPagination
    search_fields = ["title","author"]
    ordering_fields = ["created_at","title"]


class BookCreate(CreateAPIView):
    queryset = Books.objects.all()
    serializer_class = BookSerailizer
    #automatically request user ro owner besoza
    def perform_create(self,serializer):
        serializer.save(owner=self.request.user,status="available")




class BookUpdate(UpdateAPIView):
    permission_classes = [isBookOwner]
    queryset = Books.objects.all()
    serializer_class = BookSerailizer

    #dega user ho natawanan book owner wa status to change konan
    def perform_update(self,serializer):
        serializer.save(owner=self.request.user,status=serializer.instance.status)


class BookDelete(DestroyAPIView):
    permission_classes = [isBookOwner]
    queryset = Books.objects.all()
    serializer_class = BookSerailizer

    def perform_destroy(self,instance):
        if Trade.objects.filter(requested_book=instance,status="pending").exists() or Trade.objects.filter(offered_book=instance,status="pending").exists():
            raise ValidationError("This book has a pending trade request")
        instance.delete()

class BookDetail(RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Books.objects.all().select_related("owner","category")
    serializer_class = BookSerailizer


class Mybooks(ListAPIView):
    serializer_class = BookSerailizer
    def get_queryset(self):
        return Books.objects.filter(owner = self.request.user).select_related("owner","category")
