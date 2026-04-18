from django.db import models
from core.models import BaseModel

class AccessCode(BaseModel):
    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('not_sent', 'Not Sent'),
    )
    code = models.CharField(max_length=100, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_sent')
    duration_months = models.IntegerField(default=1) # 1, 2, 3, 4, 5, 6 months
    is_active = models.BooleanField(default=True)
    is_consumed = models.BooleanField(default=False)
    consumed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='consumed_codes')
    
    # Shopify data
    shopify_order_id = models.CharField(max_length=100, null=True, blank=True)
    shopify_email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return f"{self.code} - {self.status} - {'Consumed' if self.is_consumed else 'Available'}"

class VerificationPackage(BaseModel):
    CATEGORY_CHOICES = (
        ('basic', 'Basic'),
        ('weekly', 'Weekly'),
        ('advanced', 'Advanced'),
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, unique=True)
    product_purchase_link = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.get_category_display()
