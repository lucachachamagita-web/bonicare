from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class AuditLog(models.Model):
    action = models.CharField(max_length=50)
    model_name = models.CharField(max_length=50)
    record_id = models.IntegerField()
    changed_by = models.ForeignKey(User, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now_add=True)
    old_data = models.JSONField(null=True)
    new_data = models.JSONField(null=True)

    def delete(self, *args, **kwargs):
        raise ValidationError("Audit logs cannot be deleted.")

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("Audit logs cannot be modified once created.")
        super().save(*args, **kwargs)
