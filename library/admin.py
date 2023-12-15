from django.contrib import admin
from .models import Book
from .models import Members
from .models import Transactions
# Register your models here.

admin.site.register(Book)
admin.site.register(Members)
admin.site.register(Transactions)

