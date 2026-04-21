import os
import django
import sys

# Setup django
sys.path.append('/Users/beuptechagency/kick-360-app-backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from tournaments.models import Tournament, TournamentParticipation
from training.models import TrainingSession, TrainingCompletion
from sessions.models import Session
from accounts.models import User
from tournaments.serializers import TournamentParticipationSerializer
from training.serializers import TrainingSessionSerializer
from sessions.serializers import SessionSerializer

def verify():
    print("--- Verifying Tournament Changes ---")
    # Check participation fields
    participation = TournamentParticipation()
    if hasattr(participation, 'score'):
        print("[OK] TournamentParticipation has 'score' field.")
    else:
        print("[FAIL] TournamentParticipation missing 'score' field.")

    print("\n--- Verifying Video Thumbnail Changes ---")
    models_to_check = [
        (TrainingSession, 'thumbnail'),
        (TrainingCompletion, 'thumbnail'),
        (Session, 'thumbnail')
    ]
    for model, field in models_to_check:
        instance = model()
        if hasattr(instance, field):
            print(f"[OK] {model.__name__} has '{field}' field.")
        else:
            print(f"[FAIL] {model.__name__} missing '{field}' field.")

    print("\n--- Verifying Serializer Changes ---")
    # We can check field names in serializers
    tp_fields = TournamentParticipationSerializer().get_fields()
    if 'score' in tp_fields:
        print("[OK] TournamentParticipationSerializer includes 'score'.")
    else:
        print("[FAIL] TournamentParticipationSerializer missing 'score'.")

    ts_fields = TrainingSessionSerializer().get_fields()
    if 'thumbnail' in ts_fields:
        print("[OK] TrainingSessionSerializer includes 'thumbnail'.")
    else:
        print("[FAIL] TrainingSessionSerializer missing 'thumbnail'.")

    s_fields = SessionSerializer().get_fields()
    if 'thumbnail' in s_fields:
        print("[OK] SessionSerializer includes 'thumbnail'.")
    else:
        print("[FAIL] SessionSerializer missing 'thumbnail'.")

if __name__ == "__main__":
    verify()
