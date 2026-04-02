from django.urls import path

from users.views import user
from .views import spending_categories, transactions_summary, add_transactions, month_comparison

urlpatterns = [
    path('spending_categories/', spending_categories, name='spending-categories'),
    path('users/user/', user, name='me'),
    path('transactions_summary/', transactions_summary, name='transactions'),
    path('add_transactions/', add_transactions, name='add_transactions'),
    path('month_comparison/', month_comparison, name='month_comparison')
]
