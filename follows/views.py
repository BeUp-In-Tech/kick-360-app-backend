from rest_framework import generics, status, serializers
from rest_framework.permissions import IsAuthenticated
from core.permissions import HasActiveSubscription
from .models import Follow
from accounts.models import User
from .serializers import FollowSerializer, DiscoverUserSerializer
from core.exceptions import APIResponse
from django.db import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend

class FollowUserView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, HasActiveSubscription)
    serializer_class = FollowSerializer

    def create(self, request, *args, **kwargs):
        following_id = request.data.get('following_id') or request.data.get('following')
        if not following_id:
            return APIResponse(message="following_id is required.", status=status.HTTP_400_BAD_REQUEST)

        if str(request.user.id) == str(following_id):
            return APIResponse(message="You cannot follow yourself.", status=status.HTTP_400_BAD_REQUEST)

        try:
            following_user = User.objects.get(id=following_id, is_active=True)
            
            # Check follow limit (11 players)
            if Follow.objects.filter(follower=request.user).count() >= 11:
                return APIResponse(message="You can follow maximum 11 players.", status=status.HTTP_400_BAD_REQUEST)
                
            follow = Follow.objects.create(follower=request.user, following=following_user)
            return APIResponse(data=FollowSerializer(follow).data, message=f"Successfully followed {following_user.name}")
        except (User.DoesNotExist, ValueError, ValidationError):
            return APIResponse(message="User not found or invalid ID.", status=status.HTTP_404_NOT_FOUND)
        except IntegrityError:
            return APIResponse(message="You are already following this user.", status=status.HTTP_400_BAD_REQUEST)

class UnfollowUserSerializer(serializers.Serializer):
    pass

class UnfollowUserView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UnfollowUserSerializer

    def delete(self, request, user_id, *args, **kwargs):
        try:
            follow = Follow.objects.get(follower=request.user, following_id=user_id)
            follow.delete()
            return APIResponse(message="Successfully unfollowed user.")
        except Follow.DoesNotExist:
            return APIResponse(message="You are not following this user.", status=status.HTTP_404_NOT_FOUND)

class DiscoverUsersView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, HasActiveSubscription)
    serializer_class = DiscoverUserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['country', 'position']

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return User.objects.none()
        # Exclude self and users already followed
        following_ids = Follow.objects.filter(follower=self.request.user).values_list('following_id', flat=True)
        return User.objects.filter(is_active=True).exclude(id=self.request.user.id).exclude(id__in=following_ids).order_by('-total_kicks')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse(data=serializer.data, message="Discover users retrieved.")

class FollowersListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = DiscoverUserSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return User.objects.none()
        follower_ids = Follow.objects.filter(following=self.request.user).values_list('follower_id', flat=True)
        return User.objects.filter(id__in=follower_ids)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse(data=serializer.data, message="Followers retrieved.")

class FollowingListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = DiscoverUserSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return User.objects.none()
        following_ids = Follow.objects.filter(follower=self.request.user).values_list('following_id', flat=True)
        return User.objects.filter(id__in=following_ids)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse(data=serializer.data, message="Following retrieved.")
