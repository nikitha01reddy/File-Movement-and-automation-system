# from django.db import models
# from authentication.models import UserProfile
# from django.utils.timezone import now
# import uuid

# class Request(models.Model):
#     REQUEST_STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('approved', 'Approved'),
#         ('rejected', 'Rejected'),
#         ('forwarded', 'Forwarded'),
#     ]
    
#     request_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
#     file_no = models.CharField(max_length=50)
#     volume_no = models.CharField(max_length=50, blank=True, null=True)
#     security_classification = models.CharField(max_length=20, choices=[
#         ('confidential', 'Confidential'),
#         ('restricted', 'Restricted'),
#         ('public', 'Public'),
#     ])
#     request_text = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     current_approver = models.ForeignKey(
#         UserProfile,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='current_approvals'
#     )
#     status = models.CharField(
#         max_length=20,
#         choices=REQUEST_STATUS_CHOICES,
#         default='pending'
#     )
#     resubmitted = models.BooleanField(default=False)
#     original_request = models.ForeignKey(
#         'self',
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='resubmissions'
#     )
#     def can_be_resubmitted(self):
#         return self.status == 'rejected' and not self.resubmitted
    
#     def create_resubmission(self, new_files=None, new_enclosures=None):
#         if not self.can_be_resubmitted():
#             return None
        
#         # Create new request with same details
#         new_request = Request.objects.create(
#             user=self.user,
#             file_no=self.file_no,
#             volume_no=self.volume_no,
#             security_classification=self.security_classification,
#             request_text=self.request_text,
#             original_request=self,
#             resubmitted=True
#         )
        
#         # Copy existing files
#         for form_file in self.form_files.all():
#             RequestFormFile.objects.create(
#                 request=new_request,
#                 file=form_file.file
#             )
            
#         for enclosure_file in self.enclosure_files.all():
#             EnclosureFile.objects.create(
#                 request=new_request,
#                 file=enclosure_file.file
#             )
        
#         # Add new files if provided
#         if new_files:
#             for file in new_files:
#                 RequestFormFile.objects.create(
#                     request=new_request,
#                     file=file
#                 )
        
#         if new_enclosures:
#             for file in new_enclosures:
#                 EnclosureFile.objects.create(
#                     request=new_request,
#                     file=file
#                 )
        
#         # Get last rejector and set as approver
#         last_rejector = self.statuses.filter(status='rejected').last().approver
        
#         RequestApprover.objects.create(
#             request=new_request,
#             approver=last_rejector
#         )
        
#         new_request.current_approver = last_rejector
#         new_request.save()
        
#         RequestStatus.objects.create(
#             request=new_request,
#             approver=last_rejector,
#             status='pending',
#             comment='Resubmitted with additional files'
#         )
        
#         return new_request
#     def get_current_status(self):
#         """Get the most recent status for this request"""
#         return self.statuses.order_by('-timestamp').first()
    
#     def get_current_approver(self):
#         """Get the current approver based on status"""
#         status = self.get_current_status()
#         return status.approver if status else None
    
#     def get_status_for_approver(self, approver):
#         """Get status for a specific approver"""
#         if not isinstance(approver, UserProfile):
#             try:
#                 approver = UserProfile.objects.get(pk=approver)
#             except UserProfile.DoesNotExist:
#                 return None
#         return self.statuses.filter(approver=approver).first()
#     def __str__(self):
#         return f"Request {self.file_no} - {self.request_id}"

# class RequestStatus(models.Model):
#     request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name="statuses")
#     approver = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
#     status = models.CharField(max_length=20, choices=[
#         ('pending', 'Pending'),
#         ('approved', 'Approved'),
#         ('rejected', 'Rejected'),
#         ('forwarded', 'Forwarded'),
#     ], default='pending')
#     timestamp = models.DateTimeField(default=now)
#     comment = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return f"{self.approver.name} - Status: {self.status}"

# class RequestApprover(models.Model):
#     request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='approvers')
#     approver = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

#     def __str__(self):
#         return f"{self.approver.name} (Request: {self.request.file_no})"

#     class Meta:
#         ordering = ['id']

# class RequestFormFile(models.Model):
#     request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name="form_files")
#     file = models.FileField(upload_to="requests/forms/")

#     def __str__(self):
#         return f"Form File for Request {self.request.file_no}"

# class EnclosureFile(models.Model):
#     request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name="enclosure_files")
#     file = models.FileField(upload_to="requests/enclosures/")
#     uploaded_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Enclosure File for Request {self.request.file_no}"
from django.db import models
from authentication.models import UserProfile
from django.utils.timezone import now
import uuid

class Request(models.Model):
    REQUEST_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('forwarded', 'Forwarded'),
    ]
    
    request_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    file_no = models.CharField(max_length=50)
    volume_no = models.CharField(max_length=50, blank=True, null=True)
    security_classification = models.CharField(max_length=20, choices=[
        ('confidential', 'Confidential'),
        ('restricted', 'Restricted'),
        ('public', 'Public'),
    ])
    request_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    current_approver = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_approvals'
    )
    status = models.CharField(
        max_length=20,
        choices=REQUEST_STATUS_CHOICES,
        default='pending'
    )
    resubmitted = models.BooleanField(default=False)
    original_request = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resubmissions'
    )

    def can_be_resubmitted(self):
        return self.status == 'rejected' and not self.resubmitted
    
    def create_resubmission(self, new_files=None, new_enclosures=None):
        if not self.can_be_resubmitted():
            return None
        
        # Create new request with same details
        new_request = Request.objects.create(
            user=self.user,
            file_no=self.file_no,
            volume_no=self.volume_no,
            security_classification=self.security_classification,
            request_text=self.request_text,
            original_request=self,
            resubmitted=True
        )
        
        # Copy existing files
        for form_file in self.form_files.all():
            RequestFormFile.objects.create(
                request=new_request,
                file=form_file.file
            )
            
        for enclosure_file in self.enclosure_files.all():
            EnclosureFile.objects.create(
                request=new_request,
                file=enclosure_file.file
            )
        
        # Add new files if provided
        if new_files:
            for file in new_files:
                RequestFormFile.objects.create(
                    request=new_request,
                    file=file
                )
        
        if new_enclosures:
            for file in new_enclosures:
                EnclosureFile.objects.create(
                    request=new_request,
                    file=file
                )
        
        # Get last rejector and set as approver
        last_rejector = self.statuses.filter(status='rejected').last().approver
        
        RequestApprover.objects.create(
            request=new_request,
            approver=last_rejector
        )
        
        new_request.current_approver = last_rejector
        new_request.save()
        
        RequestStatus.objects.create(
            request=new_request,
            approver=last_rejector,
            status='pending',
            comment='Resubmitted with additional files'
        )
        
        return new_request

    def __str__(self):
        return f"Request {self.file_no} - {self.request_id}"

class RequestStatus(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name="statuses")
    approver = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('forwarded', 'Forwarded'),
    ], default='pending')
    timestamp = models.DateTimeField(default=now)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.approver.name} - Status: {self.status}"

class RequestApprover(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='approvers')
    approver = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.approver.name} (Request: {self.request.file_no})"

    class Meta:
        ordering = ['id']

class RequestFormFile(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name="form_files")
    file = models.FileField(upload_to="requests/forms/")

    def __str__(self):
        return f"Form File for Request {self.request.file_no}"

class EnclosureFile(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name="enclosure_files")
    file = models.FileField(upload_to="requests/enclosures/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Enclosure File for Request {self.request.file_no}"

