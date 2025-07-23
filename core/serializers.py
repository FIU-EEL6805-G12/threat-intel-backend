from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from .models import ActivityLog, Command, Device, Screenshot


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = "__all__"


class DeviceListSerializer(serializers.ModelSerializer):
    screenshot_count = serializers.SerializerMethodField()
    activity_count = serializers.SerializerMethodField()
    is_online = serializers.SerializerMethodField()
    last_activity = serializers.SerializerMethodField()

    class Meta:
        model = Device
        fields = ["id", "name", "last_seen", "screenshot_count", "activity_count", "is_online", "last_activity"]

    def get_screenshot_count(self, obj):
        return obj.screenshots.count()

    def get_activity_count(self, obj):
        return obj.activity_logs.count()

    def get_is_online(self, obj):
        if not obj.last_seen:
            return False
        five_minutes_ago = timezone.now() - timedelta(minutes=5)
        return obj.last_seen > five_minutes_ago

    def get_last_activity(self, obj):
        if obj.last_seen:
            return obj.last_seen.isoformat()
        return None


class CommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Command
        fields = "__all__"
        read_only_fields = ("executed_at",)


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = "__all__"
        read_only_fields = ("timestamp", "device")


class ScreenshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screenshot
        fields = "__all__"
        read_only_fields = ("timestamp", "id", "device")
