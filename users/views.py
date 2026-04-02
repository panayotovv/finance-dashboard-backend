from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from transactions.models import Transaction
from transactions.serializers import RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user(request):
    user = request.user

    total_transactions = Transaction.objects.filter(user=user).count()

    return Response({
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'total_transactions': total_transactions
    })


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

