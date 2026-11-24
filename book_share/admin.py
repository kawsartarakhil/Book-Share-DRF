from django.contrib import admin
from .models import *

admin.site.register(Category)
admin.site.register(Books)
admin.site.register(Trade)
admin.site.register(Review)