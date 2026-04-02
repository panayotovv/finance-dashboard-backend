from datetime import timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from transactions.models import Transaction, Category
from transactions.serializers import TransactionSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Sum
import hashlib


def get_color_from_name(name):
    hash_object = hashlib.md5(name.encode())
    hex_color = hash_object.hexdigest()[:6]
    return f"#{hex_color}"

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def spending_categories(request):
    user = request.user
    categories = Category.objects.filter(user=user)
    data = []

    for cat in categories:
        total = Transaction.objects.filter(user=user, category=cat, type='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or 0
        data.append({
            "name": cat.name,
            "value": float(total),
            "color": get_color_from_name(cat.name),
        })

    return Response({
        "categories": data,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def month_comparison(request):
    user = request.user
    now = timezone.now()
    start_this_month = now.replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    start_last_month = (start_this_month - timedelta(days=1)).replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    def get_total(transaction_type, start_date, end_date=None, category=None):
        qs = Transaction.objects.filter(type=transaction_type, user=user)

        if category:
            qs = qs.filter(category__name=category)
        if end_date:
            qs = qs.filter(created_at__gte=start_date, created_at__lt=end_date)
        else:
            qs = qs.filter(created_at__gte=start_date)

        return qs.aggregate(total=Sum('amount'))['total'] or 0

    def percent_change(current, previous):
        if previous == 0:
            return None
        return ((current - previous) / previous) * 100

    transactions = Transaction.objects.filter(user=user)
    income = transactions.filter(type="INCOME").aggregate(Sum('amount'))['amount__sum'] or 0
    expenses = transactions.filter(type="EXPENSE").aggregate(Sum('amount'))['amount__sum'] or 0

    this_income = get_total('INCOME', start_this_month)
    last_income = get_total('INCOME', start_last_month, start_this_month)

    total_percentage = percent_change(this_income, last_income)
    total = (income - expenses)

    this_expense = get_total('EXPENSE', start_this_month)
    last_expense = get_total('EXPENSE', start_last_month, start_this_month)

    this_investment_income = get_total('INCOME', start_this_month, category='Investment')
    this_investment_expense = get_total('EXPENSE', start_this_month, category='Investment')
    this_investment = this_investment_income - this_investment_expense

    last_investment_income = get_total('INCOME', start_last_month, start_this_month, category='Investment')
    last_investment_expense = get_total('EXPENSE', start_last_month, start_this_month, category='Investment')
    last_investment = last_investment_income - last_investment_expense

    income_change = percent_change(this_income, last_income)
    expense_change = percent_change(this_expense, last_expense)
    investment_change = percent_change(this_investment, last_investment)

    return Response ({
        "total": total,
        "total_percentage": total_percentage,
        "income": {
            "current": this_income,
            "last": last_income,
            "percent_change": income_change,
        },
        "expenses": {
            "current": this_expense,
            "last": last_expense,
            "percent_change": expense_change,
        },
        "investments": {
            "current": this_investment,
            "last": last_investment,
            "percent_change": investment_change,
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transactions_summary(request):
    user = request.user
    transactions = Transaction.objects.filter(user=user)
    recent = Transaction.objects.filter(user=user).order_by('-created_at')

    investments_expense = transactions.filter(category__name='Investment', type='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or 0
    investments_income = transactions.filter(category__name='Investment', type='INCOME').aggregate(Sum('amount'))['amount__sum'] or 0

    serializer = TransactionSerializer(recent, many=True)

    return Response({
        'recent_transactions': serializer.data,
        'investments_income': investments_income,
        'investments_expense': investments_expense
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_transactions(request):
    user = request.user
    data = request.data

    category_name = data.get("category")
    amount = data.get("amount")
    type_ = data.get("type")

    category_name = category_name.strip().capitalize()

    if not category_name or not amount or not type_:
        return Response({"error": "Missing fields"}, status=400)

    category_obj, created = Category.objects.get_or_create(
        name=category_name,
        user=user
    )

    transaction = Transaction.objects.create(
        user=user,
        category=category_obj,
        amount=amount,
        type=type_,
    )

    return Response({
        "message": "Transaction added",
        "id": transaction.id,
    }, status=status.HTTP_201_CREATED)


