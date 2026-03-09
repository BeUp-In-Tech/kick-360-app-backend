from rest_framework import serializers
from .models import Follow
from accounts.models import User
from accounts.serializers import UserSerializer

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['follower']

class DiscoverUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'profile_image', 'country', 'position', 'total_kicks', 'rank', 'streak', 'points']
