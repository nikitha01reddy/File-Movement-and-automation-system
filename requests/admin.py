from django.contrib import admin
from .models import Request, RequestStatus, RequestApprover, RequestFormFile, EnclosureFile

class RequestAdmin(admin.ModelAdmin):
    list_display = ('file_no', 'user', 'status', 'current_approver', 'security_classification', 'created_at')
    search_fields = ('file_no', 'user__name', 'status')
    list_filter = ('status', 'security_classification', 'created_at')
    readonly_fields = ('request_id', 'created_at')
    fieldsets = (
        (None, {
            'fields': ('request_id', 'user', 'file_no', 'volume_no')
        }),
        ('Classification', {
            'fields': ('security_classification',)
        }),
        ('Request Details', {
            'fields': ('request_text', 'status', 'current_approver')
        }),
        ('Dates', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

class RequestStatusAdmin(admin.ModelAdmin):
    list_display = ('request', 'approver', 'status', 'timestamp', 'comment')
    list_filter = ('status', 'timestamp')
    search_fields = ('request__file_no', 'approver__name')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'

class RequestApproverAdmin(admin.ModelAdmin):
    list_display = ('request', 'approver', 'get_request_status')
    search_fields = ('request__file_no', 'approver__name')
    
    def get_request_status(self, obj):
        return obj.request.status
    get_request_status.short_description = 'Request Status'

@admin.register(RequestFormFile)
class RequestFormFileAdmin(admin.ModelAdmin):
    list_display = ('request', 'file', 'get_file_no')
    search_fields = ('request__file_no',)
    
    def get_file_no(self, obj):
        return obj.request.file_no
    get_file_no.short_description = 'File No'

@admin.register(EnclosureFile)
class EnclosureFileAdmin(admin.ModelAdmin):
    list_display = ('request', 'file', 'uploaded_at', 'get_file_no')
    search_fields = ('request__file_no',)
    list_filter = ('uploaded_at',)
    
    def get_file_no(self, obj):
        return obj.request.file_no
    get_file_no.short_description = 'File No'

# Register the models
admin.site.register(Request, RequestAdmin)
admin.site.register(RequestStatus, RequestStatusAdmin)
admin.site.register(RequestApprover, RequestApproverAdmin)