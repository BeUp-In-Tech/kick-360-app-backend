from rest_framework import serializers
from .models import Tournament, TournamentParticipation
from accounts.serializers import UserSerializer

class TournamentSerializer(serializers.ModelSerializer):
    joined_count = serializers.SerializerMethodField()

    class Meta:
        model = Tournament
        fields = ['id', 'title', 'description', 'category', 'start_date', 'end_date', 'prize_money', 'is_free', 'is_active', 'joined_count', 'created_at']

    def get_joined_count(self, obj):
        return obj.participations.count()

class TournamentParticipationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    tournament = TournamentSerializer(read_only=True)

    class Meta:
        model = TournamentParticipation
        fields = ['id', 'user', 'tournament', 'total_kicks', 'hours_played', 'rank', 'created_at']
