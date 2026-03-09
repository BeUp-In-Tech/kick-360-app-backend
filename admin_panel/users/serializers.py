from rest_framework import serializers
from accounts.models import User
from access_codes.models import AccessCode

class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'access_code', 'country', 'position', 'total_kicks', 'points', 'streak', 'is_active', 'is_staff', 'date_joined']
        read_only_fields = ['id', 'date_joined']
