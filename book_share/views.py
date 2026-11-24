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
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status

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





class TradeCreate(CreateAPIView):
    queryset = Trade.objects.all()
    serializer_class = TradeSerailizer

    def perform_create(self,serializer):
        serializer.save(sender=self.request.user,status="pending")

class TradeDetail(RetrieveAPIView):
    queryset = Trade.objects.all()
    serializer_class = TradeSerailizer

    def get_object(self):
        trade = super().get_object()
        if trade.sender != self.request.user and trade.requested_book.owner != self.request.user:
            raise PermissionDenied("You cannot view this trade")
        return trade

class IncomingTrades(ListAPIView):
    serializer_class = TradeSerailizer

    def get_queryset(self):
        trades = Trade.objects.filter(requested_book__owner=self.request.user).select_related("sender","requested_book__owner","requested_book__category","offered_book__owner","offered_book__category")
        trade_status = self.request.query_params.get("status")
        if trade_status:
            trades = trades.filter(status=trade_status)
        return trades


class OutgoingTrades(ListAPIView):
    serializer_class = TradeSerailizer

    def get_queryset(self):
        trades = Trade.objects.filter(sender=self.request.user).select_related("sender","requested_book__owner","requested_book__category","offered_book__owner","offered_book__category")
        trade_status = self.request.query_params.get("status")
        if trade_status:
            trades = trades.filter(status=trade_status)
        return trades


class TradeAccept(UpdateAPIView):
    permission_classes = [isTradereciever]
    queryset = Trade.objects.all()
    serializer_class = TradeSerailizer

    def update(self,request,*args,**kwargs):
        trade = self.get_object()

        if trade.status != "pending":
            raise ValidationError("Trade is not pending")

        requested_book = trade.requested_book
        offered_book = trade.offered_book

        if requested_book.status != "available" or offered_book.status != "available":
            raise ValidationError("One of the books is not available")

        trade.status = "accepted"
        trade.save()
        requested_book.status = "exchanged"
        requested_book.save()
        offered_book.status = "exchanged"
        offered_book.save()

        trades = Trade.objects.filter(status="pending")
        for item in trades:
            if item.requested_book in [requested_book,offered_book] or item.offered_book in [requested_book,offered_book]:
                item.status = "rejected"
                item.save()
        return Response({"message":"Trade accepted"},status=status.HTTP_200_OK)


class TradeReject(UpdateAPIView):
    permission_classes = [isTradereciever]
    queryset = Trade.objects.all()
    serializer_class = TradeSerailizer

    def update(self,request,*args,**kwargs):
        trade = self.get_object()

        if trade.status != "pending":
            raise ValidationError("Trade is not pending")

        trade.status = "rejected"
        trade.save()
        return Response({"message":"Trade rejected"},status=status.HTTP_200_OK)


class TradeCancel(UpdateAPIView):
    permission_classes = [isTradeSender]
    queryset = Trade.objects.all()
    serializer_class = TradeSerailizer

    def update(self,request,*args,**kwargs):
        trade = self.get_object()

        if trade.status != "pending":
            raise ValidationError("Trade is not pending")

        trade.status = "cancelled"
        trade.save()
        return Response({"message":"Trade cancelled"},status=status.HTTP_200_OK)