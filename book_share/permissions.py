from rest_framework.permissions import BasePermission

class isBookOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class isTradereciever(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.requested_book.owner == request.user


class isTradeSender(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.sender == request.user