from django.contrib import admin
from django.utils.html import format_html

from core.models import ActivityLog, Command, Device, Screenshot

admin.site.site_header = "Group 12 - Command and Control Center"
admin.site.site_title = "Group 12 Admin Portal"
admin.site.index_title = "Welcome to the Admin Dashboard"


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("hardware_id", "name", "ip", "os_version", "app_version", "status", "last_seen")
    search_fields = ("hardware_id", "name")
    list_filter = ("status",)
    readonly_fields = ("last_seen", "status", "ip", "os_version", "app_version")
    fieldsets = (
        (None, {"fields": ("hardware_id", "name", "status", "settings")}),
        ("Device Information", {"fields": ("os_version", "app_version", "ip")}),
        ("Time Information", {"fields": ("last_seen",), "classes": ("collapse",)}),
    )


@admin.register(Command)
class CommandAdmin(admin.ModelAdmin):
    list_display = ("device", "command_type", "status", "created_at", "executed_at")
    list_filter = ("command_type", "status", "device")
    search_fields = ("device__hardware_id", "device__name", "command_type")
    readonly_fields = ("created_at", "executed_at", "status")


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    # Read only admin panel
    list_display = ("device", "timestamp")
    list_filter = ("device",)
    search_fields = ("device__hardware_id", "device__name")
    readonly_fields = ("timestamp",)
    raw_id_fields = ("device",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(Screenshot)
class ScreenshotAdmin(admin.ModelAdmin):
    list_display = ["id", "device", "image_thumbnail", "timestamp"]
    list_filter = ["timestamp", "device__name"]
    search_fields = ["device__hardware_id"]
    readonly_fields = ["id", "device", "image_data", "image_preview", "image", "timestamp"]

    def has_add_permission(self, request):
        return False  # Read only admin panel

    def has_change_permission(self, request, obj=None):
        return False  # Read only admin panel

    def has_delete_permission(self, request, obj=None):
        return True  # Allow deletion only

    def image_thumbnail(self, obj):
        """List view'da küçük thumbnail göster"""
        if obj.image:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="width: 100px; height: auto; border-radius: 4px;" /></a>',
                obj.image.url,
                obj.image.url,
            )
        return "No Image"

    def image_preview(self, obj):
        """Detail view'da büyük resim göster"""
        if obj.image:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="max-width: 800px; max-height: 600px; border: 1px solid #ddd; border-radius: 8px;" /></a>',
                obj.image.url,
                obj.image.url,
            )
        return "No Image"

    image_preview.short_description = "Screenshot Preview"

    image_thumbnail.short_description = "Screenshot"
