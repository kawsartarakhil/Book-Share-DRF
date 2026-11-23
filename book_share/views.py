from .serailizer import *
from .models import *
from .filters import BookFilter
from .pagination import CustomPagination
from rest_framework.generics import ListAPIView,CreateAPIView,UpdateAPIView,RetrieveAPIView,DestroyAPIView
from rest_framework.permissions import AllowAny,IsAdminUser

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