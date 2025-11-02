from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from .models import *
from django.shortcuts import render, redirect, get_object_or_404
from authentication.models import UserProfile

@login_required
def submit_request(request):
    if request.method == "POST":
        send_to = request.POST.getlist('sendTo')
        file_no = request.POST.get('fileNo')
        volume_no = request.POST.get('volumeNo')
        security_classification = request.POST.get('securityClassification')
        request_text = request.POST.get('request')
        form_files = request.FILES.getlist('uploadForm')
        enclosure_files = request.FILES.getlist('enclosures')

        try:
            user_profile = UserProfile.objects.get(userid=request.session.get('userid'))
        except UserProfile.DoesNotExist:
            messages.error(request, "User profile not found.")
            return redirect('login')

        # Create request
        request_instance = Request.objects.create(
            user=user_profile,
            file_no=file_no,
            volume_no=volume_no,
            security_classification=security_classification,
            request_text=request_text
        )

        # Add files
        for f in form_files:
            RequestFormFile.objects.create(request=request_instance, file=f)
        for ef in enclosure_files:
            EnclosureFile.objects.create(request=request_instance, file=ef)

        # Add approvers in order
        approvers = []
        for user_id in send_to:
            try:
                approver = UserProfile.objects.get(userid=user_id)
                approvers.append(approver)
                RequestApprover.objects.create(request=request_instance, approver=approver)
            except UserProfile.DoesNotExist:
                messages.error(request, f"User with ID {user_id} not found.")
                continue

        if approvers:
            # Set first approver as current
            request_instance.current_approver = approvers[0]
            request_instance.save()
            # Create initial status
            RequestStatus.objects.create(
                request=request_instance,
                approver=approvers[0],
                status='pending',
                comment='Initial submission'
            )

        messages.success(request, "Request submitted successfully!")
        return redirect('requests:user_dashbd')

    return redirect('requests:user_dashbd')

@login_required
def user_received_requests(request):
    user_id = request.session.get('userid')
    if not user_id:
        return redirect('login')

    try:
        user_profile = UserProfile.objects.get(userid=user_id)
    except UserProfile.DoesNotExist:
        return redirect('login')

    # Get requests where user is current approver
    received_requests = RequestStatus.objects.filter(
        approver=user_profile,
        status='pending',
        request__current_approver=user_profile
    ).select_related('request')

    return render(request, 'user/u_received.html', {
        'received_requests': received_requests,
        'details': user_profile,
        'userid': user_id,
    })

@login_required
def handle_request_action(request, request_id):
    user_id = request.session.get('userid')
    if not user_id:
        return redirect('login')

    try:
        req = Request.objects.get(request_id=request_id)
        user_profile = UserProfile.objects.get(userid=user_id)
        if req.current_approver != user_profile:
            messages.error(request, "This request is not currently awaiting your action.")
            return redirect('requests:user_received')
            
        current_status = RequestStatus.objects.get(
            request=req,
            approver=user_profile,
            status='pending'
        )
    except (Request.DoesNotExist, UserProfile.DoesNotExist, RequestStatus.DoesNotExist):
        return redirect('requests:user_received')

    # Get ordered approvers
    approvers = list(req.approvers.all().order_by('id'))
    current_index = [a.approver_id for a in approvers].index(user_profile.userid)
    is_last = current_index == len(approvers) - 1

    
    if request.method == 'POST':
        action = request.POST.get('action')
        comment = request.POST.get('comment', '')
        
        # Map action to status choice
        action_status_map = {
            'approve': 'approved',
            'reject': 'rejected',
            'forward': 'forwarded'
        }
        
        if action not in action_status_map:
            return redirect('requests:user_received')
            
        status = action_status_map[action]

        if action == 'approve' and not is_last:
            messages.error(request, "Only the last approver can approve.")
            return redirect('requests:user_received')
            
        if action == 'forward' and is_last:
            messages.error(request, "Last approver cannot forward.")
            return redirect('requests:user_received')

        # Update status using the correct choice
        current_status.status = status  # Now uses 'rejected' instead of 'reject'
        current_status.comment = comment
        current_status.save()

        if action == 'forward':
            next_approver = approvers[current_index + 1].approver
            req.current_approver = next_approver
            req.save()
            
            RequestStatus.objects.create(
                request=req,
                approver=next_approver,
                status='pending',
                comment=f'Forwarded from {user_profile.name}'
            )
            messages.success(request, f"Request forwarded to {next_approver.name}")
        else:
            # For both approve and reject
            req.current_approver = None
            req.status = status  # Uses the mapped status ('approved' or 'rejected')
            req.save()
            messages.success(request, f"Request {status} successfully")

        return redirect('requests:user_received')

    return render(request, 'user/u_received.html', {
        'detail_view': True,
        'request': req,
        'is_last_approver': is_last,
        'form_files': req.form_files.all(),
        'enclosure_files': req.enclosure_files.all(),
        'approval_flow': RequestStatus.objects.filter(request=req).order_by('timestamp'),
    })
@login_required
def admin_dashboard(request):
    # Check if user is actually admin
    if request.session.get('userid') != 'admin':
        return redirect('requests:user_dashbd')  # Redirect non-admins
    
    # Count requests by status
    total_approved = Request.objects.filter(status='approved').count()
    total_rejected = Request.objects.filter(status='rejected').count()
    total_pending = Request.objects.filter(status='pending').count()

    # Admin dashboard logic
    context = {
        'userid': request.session.get('userid'),
        'is_admin': True,
        'total_approved': total_approved,
        'total_rejected': total_rejected,
        'total_pending': total_pending,
    }
    return render(request, 'admin/a_dashbd.html', context)
@login_required
def user_dashboard(request):
    user_id = request.session.get('userid')
    if not user_id:
        return redirect('login')

    try:
        user_profile = UserProfile.objects.get(userid=user_id)
    except UserProfile.DoesNotExist:
        return redirect('login')

    # Sent requests (initiated by user and still pending)
    sent_count = Request.objects.filter(
        user=user_profile,
        status='pending'  # Using the new status field
    ).count()

    # Received requests (where user is current approver and status is pending)
    received_count = Request.objects.filter(
        current_approver=user_profile,
        status='pending'
    ).count()

    # History count (split into two simple queries)
    # 1. Requests created by user that are completed (approved/rejected)
    created_history = Request.objects.filter(
        user=user_profile
    ).exclude(status='pending').count()

    # 2. Requests approved/rejected by user (but not created by them)
    acted_history = RequestStatus.objects.filter(
        approver=user_profile,
        status__in=['approved', 'rejected','forwarded']
    ).values('request').distinct().count()

    history_count = created_history + acted_history

    return render(request, 'user/u_dashbd.html', {
        'sent_count': sent_count,
        'received_count': received_count,
        'history_count': history_count,
        'details': user_profile,
        'userid': user_id,
        'users': UserProfile.objects.exclude(userid=user_id),
    })

@login_required
def user_sent_requests(request):
    user_id = request.session.get('userid')
    if not user_id:
        return redirect('login')
        
    try:
        user_profile = UserProfile.objects.get(userid=user_id)
    except UserProfile.DoesNotExist:
        return redirect('login')
    
    # Get requests created by the user which are pending or forwarded
    sent_requests = Request.objects.filter(
        user=user_profile,
        status__in=['pending', 'forwarded']
    ).order_by('-created_at')
    
    return render(request, 'user/u_sent.html', {
        'sent_requests': sent_requests,
        'details': user_profile,
        'userid': user_id,
    })

@login_required
def user_history(request):
    user_id = request.session.get('userid')
    if not user_id:
        return redirect('login')

    try:
        user_profile = UserProfile.objects.get(userid=user_id)
    except UserProfile.DoesNotExist:
        return redirect('login')

    # Sent requests
    sent_requests = Request.objects.filter(
        user=user_profile
    ).exclude(status='pending').prefetch_related(
        'statuses',
        'form_files',
        'enclosure_files'
    ).order_by('-created_at')

    # Received requests
    received_statuses = RequestStatus.objects.filter(
        approver=user_profile
    ).exclude(status='pending').select_related(
        'request',
        'request__user'
    ).order_by('-timestamp')

    received_requests = []
    seen_request_ids = set()
    for status in received_statuses:
        if status.request.request_id not in seen_request_ids:
            received_requests.append({
                'request': status.request,
                'status': status,
                'files': list(status.request.form_files.all()) + list(status.request.enclosure_files.all()),
                'all_statuses': status.request.statuses.all().order_by('timestamp')
            })
            seen_request_ids.add(status.request.request_id)

    context = {
        'details': user_profile,
        'userid': user_id,
        'sent_requests': sent_requests,
        'received_requests': received_requests,
    }
    return render(request, 'user/u_history.html', context)

@login_required
def resubmit_request(request, request_id):
    try:
        original_request = Request.objects.get(
            request_id=request_id,
            user__userid=request.session.get('userid'),
            status='rejected'
        )
    except Request.DoesNotExist:
        messages.error(request, "Request not found or cannot be resubmitted")
        return redirect('requests:user_history')
    
    if request.method == 'POST':
        # Get new files from form
        new_files = request.FILES.getlist('new_files')
        new_enclosures = request.FILES.getlist('new_enclosures')
        
        # Create resubmission with new files
        new_request = original_request.create_resubmission(
            new_files=new_files,
            new_enclosures=new_enclosures
        )
        
        if new_request:
            messages.success(request, "Request resubmitted with additional files!")
            return redirect('requests:user_sent')
        else:
            messages.error(request, "Could not resubmit this request")
    
    return render(request, 'user/resubmit_request.html', {
        'original_request': original_request,
        'existing_files': original_request.form_files.all(),
        'existing_enclosures': original_request.enclosure_files.all()
    })
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login or home page after logout


def request_form(request):
    users = UserProfile.objects.all()  # Fetch all users
    return render(request, 'u_dashbd.html', {
        'users': users,  # Pass users to the template
    })

@login_required
def approved_requests(request):
    if request.session.get('userid') != 'admin':
        return redirect('requests:user_dashbd')
    
    approved_requests = Request.objects.filter(status='approved').select_related('user')
    
    return render(request, 'admin/approved_requests.html', {
        'approved_requests': approved_requests,
        'is_admin': True,
    })

# requests/views.py
@login_required
def disapproved_requests(request):
    if request.session.get('userid') != 'admin':
        return redirect('requests:user_dashbd')
    
    disapproved_requests = Request.objects.filter(status='rejected') \
        .select_related('user') \
        .prefetch_related('form_files', 'enclosure_files', 'statuses')
    
    # Add rejection details to each request
    for req in disapproved_requests:
        req.rejection = req.statuses.filter(status='rejected').last()
    
    return render(request, 'admin/disapproved_requests.html', {
        'disapproved_requests': disapproved_requests,
        'is_admin': True,
    })
@login_required
def request_detail(request, request_id):
    # Check if user is admin
    if request.session.get('userid') != 'admin':
        return redirect('requests:user_dashbd')
    
    # Get the request with all related data
    req = get_object_or_404(
        Request.objects.select_related('user', 'current_approver', 'original_request')
                      .prefetch_related('form_files', 'enclosure_files', 'statuses'),
        request_id=request_id
    )
    
    context = {
        'userid': request.session.get('userid'),
        'is_admin': True,
        'request': req,
    }
    return render(request, 'admin/request_detail_partial.html', context)

@login_required
def approved_requests(request):
    # if request.session.get('role') != 'admin':
    #     return redirect('requests:user_dashbd')
    
    # Get approved requests with basic user relation
    approved_requests = Request.objects.filter(status='approved') \
        .select_related('user') \
        .order_by('-created_at')
    
    # Add last approver to each request
    for req in approved_requests:
        last_approval = req.statuses.filter(status='approved').order_by('-timestamp').first()
        req.last_approver = last_approval.approver if last_approval else None
    
    return render(request, 'admin/approved_requests.html', {
        'approved_requests': approved_requests,
        'is_admin': True,
        'page_title': 'Approved Requests'
    })


@login_required
def disapproved_requests(request):
    # Get disapproved requests with basic user relation
    disapproved_requests = Request.objects.filter(status='rejected') \
        .select_related('user') \
        .prefetch_related('statuses', 'form_files', 'enclosure_files') \
        .order_by('-created_at')
    
    # Add last rejector to each request
    for req in disapproved_requests:
        last_rejection = req.statuses.filter(status='rejected').order_by('-timestamp').first()
        req.last_rejector = last_rejection.approver if last_rejection else None
        req.rejection_date = last_rejection.timestamp if last_rejection else None
    
    return render(request, 'admin/disapproved_requests.html', {
        'disapproved_requests': disapproved_requests,
        'is_admin': True,
        'page_title': 'Disapproved Requests'
    })

def pending_requests(request):
    pending_requests = []

    all_requests = Request.objects.select_related('user', 'current_approver').all()

    for req in all_requests:
        last_status = req.statuses.order_by('-timestamp').first()
        if last_status and last_status.status == 'pending':
            req.current_pending_with = last_status.approver
            pending_requests.append(req)

    return render(request, 'admin/pending_requests.html', {'pending_requests': pending_requests})

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserProfile

def user_list(request):
    # Handle form submissions
    if request.method == "POST":
        mode = request.POST.get("mode", "add")
        userid = request.POST.get("userid")
        
        if mode == "edit":
            try:
                user = UserProfile.objects.get(userid=userid)
            except UserProfile.DoesNotExist:
                messages.error(request, "User not found.")
                return redirect("requests:user_list")
        elif mode == "add":
            if UserProfile.objects.filter(userid=userid).exists():
                messages.error(request, "User ID already exists.")
                return redirect("requests:user_list")
            user = UserProfile(userid=userid, password=userid)  # Default password same as userid
        
        # Update all fields
        required_fields = ['name', 'department']
        optional_fields = ['school', 'section', 'cell', 'center', 'laboratory', 'club', 'office']
        
        for field in required_fields:
            value = request.POST.get(field)
            if not value:
                messages.error(request, f"Please fill the {field} field.")
                return redirect("requests:user_list")
            setattr(user, field, value)
        
        for field in optional_fields:
            setattr(user, field, request.POST.get(field) or None)
        
        user.save()
        messages.success(request, f"User {'updated' if mode == 'edit' else 'added'} successfully.")
        return redirect("requests:user_list")
    
    # Handle delete
    if 'delete' in request.GET:
        try:
            user = UserProfile.objects.get(userid=request.GET.get('delete'))
            user.delete()
            messages.success(request, "User deleted successfully.")
        except UserProfile.DoesNotExist:
            messages.error(request, "User not found.")
        return redirect("requests:user_list")
    
    # Handle edit form pre-fill
    edit_user = None
    if 'edit' in request.GET:
        try:
            edit_user = UserProfile.objects.get(userid=request.GET.get('edit'))
        except UserProfile.DoesNotExist:
            messages.error(request, "User not found.")
    
    users = UserProfile.objects.all().order_by("name")
    return render(request, "admin/user_list.html", {
        "users": users,
        "edit_user": edit_user
    })


def change_password(request):
    if request.method == "POST":
        new_password = request.POST.get("newPassword", "").strip()
        user_id = request.session.get("userid")  # Changed from 'user_id' to 'userid'
        
        if not user_id:
            messages.error(request, "User not authenticated.")
            return redirect("requests:user_dashbd")
            
        if not new_password:
            messages.error(request, "Password cannot be empty.")
            return redirect("requests:user_dashbd")
            
        try:
            user = UserProfile.objects.get(userid=user_id)
            user.password = new_password  # Storing plain text (INSECURE)
            user.save()
            messages.success(request, "Password changed successfully.")
        except UserProfile.DoesNotExist:
            messages.error(request, "User not found.")
        
    return redirect("requests:user_dashbd")

