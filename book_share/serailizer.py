from rest_framework import serializers
from .models import *

class CategorySerailizer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id","username","city"]

class BookSerailizer(serializers.ModelSerializer):
    class Meta:
        model = Books
        fields = "__all__"

    def to_representation(self,instance):
        data = super().to_representation(instance)
        data["owner"] = OwnerSerializer(instance.owner).data
        data["category"] = CategorySerailizer(instance.category).data
        return data

class TradeSerailizer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = "__all__"
        read_only_fields = ["sender","status"]

    def validate(self,data):
        user = self.context["request"].user
        requested_book = data["requested_book"]
        offered_book = data["offered_book"]

        if requested_book.owner == user:
            raise serializers.ValidationError("You cannot trade your own book")

        if offered_book.owner != user:
            raise serializers.ValidationError("This is not your book")

        if requested_book.status == "exchanged" or offered_book.status == "exchanged":
            raise serializers.ValidationError("Book already exchanged")

        if Trade.objects.filter(sender=user,requested_book=requested_book,offered_book=offered_book,status="pending").exists():
            raise serializers.ValidationError("Trade request already exists")

        return data

    def to_representation(self,instance):
        data = super().to_representation(instance)
        data["requested_book"] = BookSerailizer(instance.requested_book).data
        data["offered_book"] = BookSerailizer(instance.offered_book).data
        return data

