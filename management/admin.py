from django.contrib import admin
from .models import AddRoommate, AddExpense, ExpensePaidAmount, PUBBillAmount

# Register your models here
admin.site.register(AddRoommate)
admin.site.register(AddExpense)
admin.site.register(ExpensePaidAmount)
admin.site.register(PUBBillAmount)
