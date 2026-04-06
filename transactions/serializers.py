from rest_framework import serializers

from transactions.helpers import time_ago
from transactions.models import Transaction, Category
from users.models import Profile
from django.contrib.auth.models import User


class TransactionSerializer(serializers.ModelSerializer):
    time = serializers.SerializerMethodField()
    category = serializers.StringRelatedField()
    class Meta:
        model = Transaction
        fields = '__all__'

    def get_time(self, obj):
        return time_ago(obj.created_at)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['avatar']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        return user