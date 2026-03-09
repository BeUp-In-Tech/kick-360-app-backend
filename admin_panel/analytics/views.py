from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import HttpResponse

from django.db.models import Count
from django.db.models.functions import TruncDate
from accounts.models import User
from tournaments.models import Tournament, TournamentParticipation
from sessions.models import Session
from training.models import TrainingCategory, TrainingSession
from core.models import AdminActionLog, UserActivityLog
from admin_panel.permissions import IsAdminRole, AdminLoggerMixin
from .serializers import AdminOverviewSerializer, AdminActivityLogSerializer

from io import BytesIO
from xhtml2pdf import pisa

class AdminOverviewViewSet(viewsets.ViewSet, AdminLoggerMixin):
    permission_classes = [IsAdminRole]
    serializer_class = AdminOverviewSerializer

    def list(self, request):
        """Returns statistics for the dashboard cards."""
        
        # Registration trend (last 7 days)
        seven_days_ago = timezone.now().date() - timezone.timedelta(days=7)
        registration_trend = User.objects.filter(date_joined__date__gte=seven_days_ago) \
            .annotate(date=TruncDate('date_joined')) \
            .values('date') \
            .annotate(count=Count('id')) \
            .order_by('date')

        # Combined Activity Feed - Now only including user logs as requested
        user_logs = UserActivityLog.objects.all().order_by('-created_at')[:15]
        
        combined_activity = []
        for log in user_logs:
            combined_activity.append({
                'type': 'user',
                'user': log.user.name or 'User',
                'action': log.activity_type.replace('_', ' ').capitalize(),
                'details': log.description or '',
                'created_at': log.created_at
            })
            
        combined_activity.sort(key=lambda x: x['created_at'], reverse=True)

        data = {
            'total_users': User.objects.count(),
            'total_tournaments': Tournament.objects.count(),
            'total_sessions': Session.objects.count(),
            'total_training': TrainingSession.objects.count(),
            'analytics': {
                'daily_active_users': 0, # Placeholder
                'training_sessions': Session.objects.filter(created_at__gte=timezone.now() - timezone.timedelta(days=7)).count(),
                'video_uploads': TrainingSession.objects.count(), # Total admin uploaded videos
                'tournament_participation': TournamentParticipation.objects.count(),
                'new_users_today': User.objects.filter(date_joined__date=timezone.now().date()).count(),
            },
            'recent_activity': combined_activity,
            'registration_trend': list(registration_trend)
        }
        return Response(data)

    @action(detail=False, methods=['get'], url_path='export-excel')
    def export_excel(self, request):
        """Generates and returns an Excel report of system analytics."""
        # This would use openpyxl to generate the sheet
        # For now, a placeholder response
        return Response({'status': 'success', 'message': 'Excel export generated (Mocked).'})

    @action(detail=False, methods=['get'], url_path='export-pdf')
    def export_pdf(self, request):
        """Generates and returns a PDF report of system analytics."""
        # Logic moved into try block below using xhtml2pdf
            
        stats = {
            'total_users': User.objects.count(),
            'total_tournaments': Tournament.objects.count(),
            'total_sessions': Session.objects.count(),
            'total_training': TrainingSession.objects.count(),
            'generated_at': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        html_string = render_to_string('admin/analytics_report.html', {'stats': stats})
        
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)
        
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="analytics_report.pdf"'
            self.log_action(request.user, "Exported Analytics PDF")
            return response
        else:
            return Response({'error': 'PDF generation failed.'}, status=500)
