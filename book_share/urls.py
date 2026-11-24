from django.urls import path
from . import views

urlpatterns = [
    path('categories/',views.categoryList.as_view()),
    path('categories/create/',views.categoryCreate.as_view()),
    path('categories/<int:pk>/',views.categoryDetail.as_view()),
    path('categories/<int:pk>/update/',views.categoryUpdate.as_view()),
    path('categories/<int:pk>/delete/',views.categoryDelete.as_view()),
]