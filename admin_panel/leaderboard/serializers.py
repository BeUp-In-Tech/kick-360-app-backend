from rest_framework import serializers
from accounts.models import User

class AdminLeaderboardSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='name', read_only=True)
    class Meta:
        model = User
        fields = ['id', 'user_name', 'total_kicks', 'rank', 'points', 'country']
