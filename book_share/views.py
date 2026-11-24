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
from drf_spectacular.utils import extend_schema

@extend_schema(responses=CategorySerailizer)
class categoryList(ListAPIView):
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerailizer
    pagination_class = CustomPagination

@extend_schema(request=CategorySerailizer,responses=CategorySerailizer)
class categoryCreate(CreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Category.objects.all()
    serializer_class = CategorySerailizer
    
    

@extend_schema(responses=CategorySerailizer)
class categoryDetail(RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerailizer

@extend_schema(request=CategorySerailizer,responses=CategorySerailizer)
class categoryUpdate(UpdateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Category.objects.all()
    serializer_class = CategorySerailizer

@extend_schema(responses=None)
class categoryDelete(DestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Category.objects.all()
    serializer_class = CategorySerailizer


@extend_schema(responses=BookSerailizer)
class BookList(ListAPIView):
    permission_classes = [AllowAny]
    queryset = Books.objects.filter(status="available").select_related("owner","category")
    serializer_class = BookSerailizer
    filterset_class = BookFilter
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    pagination_class = CustomPagination
    search_fields = ["title","author"]
    ordering_fields = ["created_at","title"]

@extend_schema(request=BookSerailizer,responses=BookSerailizer)
class BookCreate(CreateAPIView):
    queryset = Books.objects.all()
    serializer_class = BookSerailizer
    #automatically request user ro owner besoza
    def perform_create(self,serializer):
        serializer.save(owner=self.request.user,status="available")



@extend_schema(request=BookSerailizer,responses=BookSerailizer)
class BookUpdate(UpdateAPIView):
    permission_classes = [isBookOwner]
    queryset = Books.objects.all()
    serializer_class = BookSerailizer

    #dega user ho natawanan book owner wa status to change konan
    def perform_update(self,serializer):
        serializer.save(owner=self.request.user,status=serializer.instance.status)

@extend_schema(responses=None)
class BookDelete(DestroyAPIView):
    permission_classes = [isBookOwner]
    queryset = Books.objects.all()
    serializer_class = BookSerailizer

    def perform_destroy(self,instance):
        if Trade.objects.filter(requested_book=instance,status="pending").exists() or Trade.objects.filter(offered_book=instance,status="pending").exists():
            raise ValidationError("This book has a pending trade request")
        instance.delete()

@extend_schema(responses=BookSerailizer)
class BookDetail(RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Books.objects.filter(status="available").select_related("owner","category")
    serializer_class = BookSerailizer

@extend_schema(responses=BookSerailizer)
class Mybooks(ListAPIView):
    serializer_class = BookSerailizer
    pagination_class = CustomPagination
    def get_queryset(self):
        return Books.objects.filter(owner = self.request.user).select_related("owner","category")




@extend_schema(request=TradeSerailizer,responses=TradeSerailizer)
class TradeCreate(CreateAPIView):
    queryset = Trade.objects.all()
    serializer_class = TradeSerailizer

    def perform_create(self,serializer):
        serializer.save(sender=self.request.user,status="pending")

@extend_schema(responses=TradeSerailizer)
class TradeDetail(RetrieveAPIView):
    queryset = Trade.objects.all()
    serializer_class = TradeSerailizer

    def get_object(self):
        trade = super().get_object()
        if trade.sender != self.request.user and trade.requested_book.owner != self.request.user:
            raise PermissionDenied("You cannot view this trade")
        return trade

@extend_schema(responses=TradeSerailizer)
class IncomingTrades(ListAPIView):
    serializer_class = TradeSerailizer
    pagination_class = CustomPagination

    def get_queryset(self):
        trades = Trade.objects.filter(requested_book__owner=self.request.user).select_related("sender","requested_book__owner","requested_book__category","offered_book__owner","offered_book__category")
        trade_status = self.request.query_params.get("status")
        if trade_status:
            trades = trades.filter(status=trade_status)
        return trades

@extend_schema(responses=TradeSerailizer)
class OutgoingTrades(ListAPIView):
    serializer_class = TradeSerailizer
    pagination_class = CustomPagination

    def get_queryset(self):
        trades = Trade.objects.filter(sender=self.request.user).select_related("sender","requested_book__owner","requested_book__category","offered_book__owner","offered_book__category")
        trade_status = self.request.query_params.get("status")
        if trade_status:
            trades = trades.filter(status=trade_status)
        return trades


@extend_schema(request=None,responses=dict)
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


@extend_schema(request=None,responses=dict)
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

@extend_schema(request=None,responses=dict)
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


@extend_schema(responses=ReviewSerailizer)
class ReviewList(ListAPIView):
    permission_classes = [AllowAny]
    queryset = Review.objects.all().select_related("reviewer","reviewed_user","trade")
    serializer_class = ReviewSerailizer
    pagination_class = CustomPagination

@extend_schema(request=ReviewSerailizer,responses=ReviewSerailizer)
class ReviewCreate(CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerailizer
    def perform_create(self,serializer):
        trade = serializer.validated_data["trade"]
        if trade.sender == self.request.user:
            reviewed_user = trade.requested_book.owner
        else:
            reviewed_user = trade.sender

        serializer.save(reviewer=self.request.user,reviewed_user=reviewed_user)

@extend_schema(responses=ReviewSerailizer)
class ReviewDetail(RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Review.objects.all().select_related("reviewer","reviewed_user","trade")
    serializer_class = ReviewSerailizer

@extend_schema(request=ReviewSerailizer,responses=ReviewSerailizer)
class ReviewUpdate(UpdateAPIView):
    serializer_class = ReviewSerailizer
    def get_queryset(self):
        return Review.objects.filter(reviewer=self.request.user)

@extend_schema(responses=None)
class ReviewDelete(DestroyAPIView):
    serializer_class = ReviewSerailizer
    def get_queryset(self):
        return Review.objects.filter(reviewer=self.request.user)