from rest_framework import serializers
from .models import *
from django.db.models import Avg

class CategorySerailizer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class OwnerSerializer(serializers.ModelSerializer):
    rating = serializers.FloatField(source="avg_rating",read_only=True)
    class Meta:
        model = CustomUser
        fields = ["id","username","city","rating"]
    

class BookSerailizer(serializers.ModelSerializer):
    class Meta:
        model = Books
        fields = "__all__"
        read_only_fields = ["owner","status"]

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



class ReviewSerailizer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ["reviewer","reviewed_user"]

    def validate(self,data):
        user = self.context["request"].user
        trade = data.get("trade",self.instance.trade if self.instance else None)
        rating = data.get("rating",self.instance.rating if self.instance else None)

        if not trade:
            raise serializers.ValidationError("Trade is required")

        if rating is None:
            raise serializers.ValidationError("Rating is required")

        if trade.status != "accepted":
            raise serializers.ValidationError("Trade not accepted")

        if trade.sender != user and trade.requested_book.owner != user:
            raise serializers.ValidationError("Not your trade")

        if rating < 1 or rating > 5:
            raise serializers.ValidationError("Rating must be 1 to 5")

        if self.instance:
            if trade != self.instance.trade:
                raise serializers.ValidationError("Cannot change trade")
        elif Review.objects.filter(trade=trade,reviewer=user).exists():
            raise serializers.ValidationError("Already reviewed")

        return data