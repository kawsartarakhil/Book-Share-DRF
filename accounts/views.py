from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serailizers import *
from rest_framework_simplejwt.exceptions import TokenError
from django.db.models import Avg
from .models import CustomUser
from drf_spectacular.utils import extend_schema

@extend_schema(request=RegisterSerailizer,responses=[201,400])
@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerailizer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response({"message":"Registration successful","user":serializer.data},status=status.HTTP_201_CREATED)

    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

@extend_schema(request=Loginserailizer,responses=[200,400])
@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    serializer = Loginserailizer(data=request.data)

    if serializer.is_valid():
        user = authenticate(username=serializer.validated_data["username"],password=serializer.validated_data["password"])
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({"access":str(refresh.access_token),"refresh":str(refresh)},status=status.HTTP_200_OK)

        return Response({"error":"Invalid username or password"},status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

@extend_schema(request=LogoutSerailizer,responses=[200,400])
@api_view(["POST"])
def logout_view(request):
    serializer = LogoutSerailizer(data=request.data)

    if serializer.is_valid():
        try:
            token = RefreshToken(serializer.validated_data["refresh"])
            token.blacklist()
            return Response({"message":"Logout successful"},status=status.HTTP_200_OK)
        except TokenError:
            return Response({"error":"Invalid refresh token"},status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

@extend_schema(request=UserProfileSerializer,responses=UserProfileSerializer,methods=["PUT","PATCH"])
@extend_schema(request=None,responses=UserProfileSerializer,methods=["GET"])
@api_view(["GET","PUT"])
def profile_view(request):
    user = CustomUser.objects.filter(id=request.user.id).annotate(avg_rating=Avg("reviews_received__rating")).first()

    if request.method == "GET":
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

    serializer = UserProfileSerializer(user,data=request.data,partial=request.method=="PATCH")
    if serializer.is_valid():
        serializer.save()
        user = CustomUser.objects.filter(id=request.user.id).annotate(avg_rating=Avg("reviews_received__rating")).first()
        return Response(UserProfileSerializer(user).data)

    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

@extend_schema(request=RefreshSerailizer,responses=[200,400])
@api_view(["POST"])
def refresh_view(request):
    serializer = RefreshSerailizer(data=request.data)

    if serializer.is_valid():
        try:
            refresh = RefreshToken(serializer.validated_data["refresh"])
            return Response({"access":str(refresh.access_token)},status=status.HTTP_200_OK)
        except TokenError:
            return Response({"error":"Invalid refresh token"},status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)