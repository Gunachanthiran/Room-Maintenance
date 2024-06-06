from django.urls import path
from . import views

urlpatterns = [
    path('', views.roommate_login),
    path('dashboard/', views.Dashboard.as_view()),
    path('add-roommate/', views.AddRoommateView.as_view()),
    path('add-expense/', views.AddExpenseView.as_view()),
    path('roommate-edit/<int:pk>/', views.AddRoommateEdit.as_view()),
    path('add-roommate/<int:pk>/', views.RoommateDelete.as_view()),
    path('expense-edit/<int:pk>/', views.ExpenseEdit.as_view()),
    path('expense-delete/<int:pk>/', views.ExpenseDelete.as_view()),
    path('calculate-expense/', views.CalculateExpense.as_view()),
    path('pub-bill/', views.PubBill.as_view()),
    path('pub-edit/<int:pk>/', views.PubBillEdit.as_view()),
    path('pub-delete/<int:pk>/', views.PubBillDelete.as_view()),
    path('login/', views.roommate_login),
    path('login_auth/', views.login_auth, name="login_auth"),
    path('logout/', views.roommate_logout, name="roommate_logout"),
]
