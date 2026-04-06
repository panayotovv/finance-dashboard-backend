from django.db.models import Sum
from django.utils.timesince import timesince
from django.utils.timezone import now
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from transactions.helpers import time_ago
from transactions.models import Transaction
from transactions.serializers import RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from transactions.throttles import RegisterThrottle


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user(request):
    user = request.user
    transactions = Transaction.objects.filter(user=user)

    total_transactions = transactions.count()
    income = transactions.filter(type="INCOME").aggregate(Sum('amount'))['amount__sum'] or 0
    expense = transactions.filter(type="EXPENSE").aggregate(Sum('amount'))['amount__sum'] or 0
    net_worth = income - expense

    return Response({
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'total_transactions': total_transactions,
        'net_worth': net_worth,
        'date_joined': user.date_joined.strftime("%B %Y")
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_activity(request):
    user = request.user

    transactions = Transaction.objects.filter(user=user).order_by('-created_at')[:5]

    data = []

    for t in transactions:
        data.append({
            "id": t.id,
            "label": f"{t.type.title()}: {t.category.name}",
            # "time": timesince(t.created_at, now()) + " ago",
            "time": time_ago(t.created_at),
            "type": "income" if t.type == "INCOME" else "expense",
            "icon": "↑" if t.type == "INCOME" else "↓",
            "created_at": t.created_at
        })

    return Response(data)

def get_tokens_for_user(userr):
    refresh = RefreshToken.for_user(userr)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@api_view(['POST'])
def user_register(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        tokens = get_tokens_for_user(user)

        return Response({
            "message": "User created successfully",
            "tokens": tokens
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

