from rest_framework import serializers
from .models import Tournament, TournamentParticipation
from accounts.serializers import UserSerializer

class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = ['id', 'title', 'description', 'start_date', 'end_date', 'prize_money', 'is_free', 'is_active', 'created_at']

class TournamentParticipationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    tournament = TournamentSerializer(read_only=True)

    class Meta:
        model = TournamentParticipation
        fields = ['id', 'user', 'tournament', 'total_kicks', 'hours_played', 'rank', 'created_at']
