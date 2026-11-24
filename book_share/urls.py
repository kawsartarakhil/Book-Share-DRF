from django.urls import path
from . import views

urlpatterns = [
    path('categories/',views.categoryList.as_view()),
    path('categories/create/',views.categoryCreate.as_view()),
    path('categories/<int:pk>/',views.categoryDetail.as_view()),
    path('categories/<int:pk>/update/',views.categoryUpdate.as_view()),
    path('categories/<int:pk>/delete/',views.categoryDelete.as_view()),

    path('books/',views.BookList.as_view()),
    path('books/create/',views.BookCreate.as_view()),
    path('my-books/',views.Mybooks.as_view()),
    path('books/<int:pk>/',views.BookDetail.as_view()),
    path('books/<int:pk>/update/',views.BookUpdate.as_view()),
    path('books/<int:pk>/delete/',views.BookDelete.as_view()),

    path('trades/create/',views.TradeCreate.as_view()),
    path('trades/incoming/',views.IncomingTrades.as_view()),
    path('trades/outgoing/',views.OutgoingTrades.as_view()),
    path('trades/<int:pk>/',views.TradeDetail.as_view()),
    path('trades/<int:pk>/accept/',views.TradeAccept.as_view()),
    path('trades/<int:pk>/reject/',views.TradeReject.as_view()),
    path('trades/<int:pk>/cancel/',views.TradeCancel.as_view()),

    path('reviews/',views.ReviewList.as_view()),
    path('reviews/create/',views.ReviewCreate.as_view()),
    path('reviews/<int:pk>/',views.ReviewDetail.as_view()),
    path('reviews/<int:pk>/update/',views.ReviewUpdate.as_view()),
    path('reviews/<int:pk>/delete/',views.ReviewDelete.as_view()),
    ]