import django_filters
from .models import Books

class BookFilter(django_filters.FilterSet):
    author = django_filters.CharFilter(field_name="author",lookup_expr="icontains")
    category = django_filters.CharFilter(field_name="category__name",lookup_expr="icontains")
    condition = django_filters.CharFilter(field_name="condition",lookup_expr="icontains")
    city = django_filters.CharFilter(field_name="city",lookup_expr="icontains")

    class Meta:
        model = Books
        fields = ["author","category","condition","city"]