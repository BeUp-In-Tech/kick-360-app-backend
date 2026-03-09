from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    help = 'Seeds the initial admin user'

    def handle(self, *args, **options):
        admin_email = 'admin@kick360.com'
        admin_password = 'adminpassword123'
        
        if not User.objects.filter(email=admin_email).exists():
            User.objects.create_superuser(
                email=admin_email,
                name='Super Admin',
                password=admin_password
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created admin user: {admin_email}'))
        else:
            self.stdout.write(self.style.WARNING(f'Admin user {admin_email} already exists.'))
