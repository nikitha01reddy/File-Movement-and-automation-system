from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.contrib.auth import login  # Import login function
from django.contrib.auth.models import User  # Import Django's User model

def login_view(request):
    if request.method == "POST":
        uid = request.POST.get("uid")  # Get User ID from form
        pswd = request.POST.get("pswd")  # Get Password from form

        print(f"Login Attempt: {uid}")  # Debugging Output

        # Special case for Admin user
        if uid == "admin" and pswd == "password":
            # Create a temporary Django user for authentication
            temp_user, created = User.objects.get_or_create(username="admin")
            login(request, temp_user)  # Log in the user
            request.session['userid'] = "admin"  # Store user ID in session
            request.session['is_admin'] = True  # Flag user as admin
            request.session.modified = True
            print("Admin Login Successful!")  # Debugging Output
            return redirect('requests:admin_dashbd')  # Redirect to admin dashboard
        
        # Normal login flow for other users
        with connection.cursor() as cursor:
            cursor.execute("SELECT userid, password FROM authentication_userprofile WHERE userid = %s", [uid])
            user = cursor.fetchone()  # Fetch only one row

        if user:  # If a user is found
            db_userid, db_password = user[0], user[1]
            if pswd == db_password:  # Verify password securely
                # Create a temporary Django user for authentication
                temp_user, created = User.objects.get_or_create(username=db_userid)
                login(request, temp_user)  # Log in the user
                request.session['userid'] = db_userid  # Store user ID in session
                request.session['is_admin'] = False  # Flag user as not admin
                request.session.modified = True
                print("Login Successful!")  # Debugging Output
                return redirect('requests:user_dashbd')  # Use the correct namespace
            else:
                messages.error(request, "Incorrect password.")
                print("Incorrect Password!")  # Debugging Output
        else:
            messages.error(request, "User ID not found.")
            print("User ID Not Found!")  # Debugging Output

    return render(request, "authentication/index.html")  # Render login page