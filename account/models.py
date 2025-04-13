from datetime import timedelta
from django.db import models
from django.utils.timezone import now


class LoginAttempt(models.Model):
    username = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    attempt_time = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)

    @classmethod
    def get_failed_attempts(cls, username, ip):
        """Returns the number of failed login attempts for a user + IP within the lockout window."""
        lockout_window = now() - timedelta(minutes=5)
        return cls.objects.filter(
            username=username,
            ip_address=ip,
            success=False,
            attempt_time__gte=lockout_window,
        ).count()

    @classmethod
    def is_locked_out(cls, username, ip, failure_limit=3):
        """Checks if the user is currently locked out."""
        return cls.get_failed_attempts(username, ip) >= failure_limit

    @classmethod
    def record_attempt(cls, username, ip, success):
        cls.objects.create(username=username, ip_address=ip, success=success)

    @classmethod
    def clear_attempts(cls, username, ip):
        cls.objects.filter(username=username, ip_address=ip, success=False).delete()

    class Meta:
        managed = True
        verbose_name = "Login Attempt"
        verbose_name_plural = "Login Attempts"
