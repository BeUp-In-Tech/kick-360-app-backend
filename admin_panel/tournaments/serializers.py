from rest_framework import serializers
from tournaments.models import Tournament, TournamentParticipation

class AdminTournamentSerializer(serializers.ModelSerializer):
    participant_count = serializers.IntegerField(source='participations.count', read_only=True)

    class Meta:
        model = Tournament
        fields = ['id', 'title', 'description', 'start_date', 'end_date', 'category', 'prize_money', 'is_free', 'is_active', 'participant_count', 'created_at']

class AdminTournamentParticipationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    
    class Meta:
        model = TournamentParticipation
        fields = ['id', 'user', 'user_name', 'total_kicks', 'hours_played', 'rank']
        read_only_fields = ['id', 'user', 'user_name', 'rank']
