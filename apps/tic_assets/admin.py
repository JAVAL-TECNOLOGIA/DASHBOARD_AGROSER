from django.contrib import admin
from .models import Asset, Assignment


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ("code", "category", "brand", "model", "status", "current_holder_name")
    list_filter = ("category", "status", "condition")
    search_fields = ("code", "serial_number", "imei", "current_holder_name")


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("asset", "movement_type", "worker_name", "created_at", "registered_by")
    list_filter = ("movement_type", "created_at")
    search_fields = ("asset__code", "worker_document", "worker_name")
