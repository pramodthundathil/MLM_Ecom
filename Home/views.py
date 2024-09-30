from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login, logout 
from .models import *

from django.conf import settings
from django.core.mail import send_mail,EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ecom.models import *
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from twilio.rest import Client


client = Client("account_sid", "auth_token")


def Landingpage(request):
    return render(request,"landingpage.html")

@login_required(login_url='SignIn')
def SentRefrelLink(request):
    if request.method == "POST":
        try:
            userdetails = request.user
            activationkey = userdetails.id_number
        except:
            userdetails = request.user
            activationkey = userdetails.id_number
            
        email = request.POST['email']
        current_site = get_current_site(request)
        mail_subject = 'Direct Selling Employees Socity Joining Link'
        path = "SignUp"
        message = render_to_string('emailbody.html', {'user': request.user,
                                                                        'domain': current_site.domain,
                                                                        'path':path,
                                                                        'token':activationkey,})

        email = EmailMessage(mail_subject, message, to=[email])
        email.send(fail_silently=True)
                    
        return redirect("ProfileScreen")

import uuid
import random

def generate_otp(user):
    otp = ''.join([str(random.randint(0, 9)) for _ in range(4)])  # Generate a 4-digit OTP
    if UserOTP.objects.filter(user=user).exists():
        userotp = UserOTP.objects.get(user = user)
        userotp.otp = otp
        userotp.save()
    else:
        UserOTP.objects.create(user=user, otp=otp)
    return otp

def generate_unique_id_number():
    while True:
        id_num = 'ADCOS' + get_random_string(length=5, allowed_chars='0123456789')
        if not CustomUser.objects.filter(id_number=id_num).exists():
            return id_num  # Break the loop and return the unique ID number

def SignUp(request,token):
    form = CustomUserCreationForm()
    sponser = CustomUser.objects.get(id_number = token)
    
    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        dob = request.POST.get('dob')
        age = request.POST.get('age')
        pincode  = request.POST.get('pincode')
        village = request.POST.get('village')
        district = request.POST.get('district')
        state = request.POST.get('state')
        address = request.POST.get('address')
        religion = request.POST.get('religion')
        cast = request.POST.get('cast')
        pan = request.POST.get('pan')
        ac_num = request.POST.get('ac_num')
        branch = request.POST.get('branch')
        ifsc = request.POST.get('ifsc')
        nomine = request.POST.get('nomine')
        id_card = request.FILES.get('id_card')
        pnum = request.POST.get('pnum')
        email = request.POST.get('email')
        pswd = request.POST.get('pswd')
        cpassword = request.POST.get('cpassword')

        if pswd != cpassword:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        try:
            if CustomUser.objects.filter(pancard = pan ).exists():
                messages.info(request,"Pancard Alredy exists...")
                return redirect("SignUp",token = token)
            if CustomUser.objects.filter(email = email ).exists():
                messages.info(request,"Email Id  Already exists...")
                return redirect("SignUp",token = token)
            if CustomUser.objects.filter(phone_number=pnum).exists():
                messages.info(request,"Phonenumber  Already exists...")
                return redirect("SignUp",token = token)
            else:
                user = CustomUser.objects.create(
                    email=email,
                    id_number=generate_unique_id_number(),
                    first_name=fname,
                    last_name=lname,
                    date_of_birth=dob,
                    age=age,
                    pincode = pincode, 
                    village=village,
                    district=district,
                    state = state,
                    address=address,
                    religion=religion,
                    cast=cast,
                    pancard=pan,
                    phone_number=pnum,
                    role='user',
                    parent = sponser,
                    is_active = False
                )
                user.set_password(pswd)
                user.save()
                otp = generate_otp(user)

                Business_Volume.objects.create(user=user)
                AccountDetails.objects.create(
                    user=user,
                    ifsc_code=ifsc,
                    branch_name=branch,
                    account_number=ac_num
                )
                Nominee.objects.create(
                    user=user,
                    nominee_name=nomine,
                    id_proof=id_card
                )
                try:
                    message = client.messages.create(
                                body = f"ADCOS E-COMMERCE COMPANY OTP for Your Account Verification is {otp} ",
                                from_ = '+15109014729',
                                to=f'+91{user.phone_number}'
                            )
                except:
                    print("Failed to sent sms")
                email = request.POST['email']
                current_site = get_current_site(request)
                mail_subject = 'OTP for Account Creation ADCOS E-COMMERCE COMPANY'
                path = "SignUp"
                message = render_to_string('emailbody_otp.html', {'user': user,
                                                                    'domain': current_site.domain,
                                                                    'path':path,
                                                                    'token':otp,})

                email = EmailMessage(mail_subject, message, to=[email])
                email.send(fail_silently=True)

                messages.success(request, "User registered successfully.")
                return redirect('OTPverification', pk = user.id)
        except ValidationError as e:
            messages.error(request, e.messages)
            return redirect('register')

    # return redirect(SignUp, token = token)


    context = {
        "form":form,
        "sponsor":sponser
    }
    return render(request,'register.html',context)

def OTPverification(request,pk):
    user = CustomUser.objects.get(id = pk)

    context = {
        "user":user
    }
    return render(request,"otpvalidation.html",context)

def verify_otp(request, pk):
    if request.method == 'POST':
        otp = request.POST['otp']
        user = CustomUser.objects.get(id = pk)
        try:
            user_otp = UserOTP.objects.get(user=user, otp=otp)
            if user_otp:
                # OTP is correct
                user.is_active = True
                user.save()
                user_otp.delete()
                try:
                    message = client.messages.create(
                                body = f"Welcome! Successfully Registerd your ADCOS Account on id {user.id_number}- adcos.in",
                                from_ = '+15109014729',
                                to=f'+91{user.phone_number}'
                            )
                except:
                    print("Failed to sent sms")
                email = request.POST['email']
                current_site = get_current_site(request)
                mail_subject = 'Accout Activated - ADCOS E-COMMERCE COMPANY'
                path = "SignUp"
                message = render_to_string('emailbody_otp.html', {'user': user,
                                                                    'domain': current_site.domain,
                                                                    'path':path,
                                                                    'user_id':user.id_number,})

                email = EmailMessage(mail_subject, message, to=[email])
                email.send(fail_silently=True)

                return redirect('VeryfiedOTP')
        except UserOTP.DoesNotExist:
            # OTP is incorrect
            messages.info(request,"Invalid OTP")
            return redirect("OTPverification")
    
    return redirect("OTPverification")

def VeryfiedOTP(request):
    return render(request, 'verified_otp.html')

def SignIn(request):
    if request.method == "POST":
        uname = request.POST['uname']
        pswd = request.POST['pswd']
        try:
            user1 = CustomUser.objects.get(id_number = uname)
            if not user1.is_active:
            
                otp = generate_otp(user1)
                email = user1.email
                current_site = get_current_site(request)
                mail_subject = 'OTP for Account Creation DSES'
                path = "SignUp"
                message = render_to_string('emailbody_otp.html', {'user': user1,
                                                                    'domain': current_site.domain,
                                                                    'path':path,
                                                                    'token':otp,})

                email = EmailMessage(mail_subject, message, to=[email])
                email.send(fail_silently=True)

                messages.success(request, "Your OTP verification is pending please verify OTP")
                return redirect('OTPverification', pk = user1.id)
        

            user = authenticate(request,id_number = uname, password = pswd)
            if user is not None:
                user = login(request,user)
                return redirect('Index')
            else:
                messages.error(request,"username or password in correct")
                return redirect("SignIn")
        except:
            messages.error(request,"username or password in correct")
            return redirect("SignIn")
    else:
        return render(request,"login.html")
    
def SignOut(request):
    logout(request)
    return redirect("Index")

def Index(request):
    product = Product.objects.filter(status = True)[:8]
    mainbanner = MainBanner.objects.all().last()
    adds = Adds.objects.all()


    context = {
        "products":product,
        "mainbanner":mainbanner,
        "adds":adds
    }

    return render(request,"index.html",context)





@login_required(login_url='SignIn')
def ProfileScreen(request):
    user = request.user
    BV = Business_Volume.objects.get(user = user)
    bankdetails = AccountDetails.objects.get(user = user)
    noinee = Nominee.objects.get(user = user)
    site = get_current_site(request)
    reflink = f"{site.domain}/SignUp/{request.user.id_number}"
    # print(user.first_name,"------------------------------------")

    first_level_members = CustomUser.objects.filter(parent=user)

    # A dictionary to hold the members for each level
    all_levels_members = {
        "level_1": first_level_members,
        "level_2": [],
        "level_3": [],
        "level_4": [],
        "level_5": []
    }

    # Recursive function to fetch members for each level
    def get_downline_members(members, current_level, max_level):
        if current_level > max_level:
            return

        # Find members sponsored by the current level members
        next_level_members = CustomUser.objects.filter(parent__in=members)

        # Store them in the appropriate level
        all_levels_members[f"level_{current_level}"] = next_level_members

        # Recursive call for the next level
        get_downline_members(next_level_members, current_level + 1, max_level)

    # Call the recursive function to get up to 5 levels of members
    get_downline_members(first_level_members, 2, 5)

    print(all_levels_members)

    
    context = {
        "BV":BV,
        "bankdetails":bankdetails,
        "noinee":noinee,
        "reflink":reflink,
        "first_level_members": first_level_members,
        "all_levels_members": all_levels_members
    }
    return render(request,"userprofile.html",context)


# views.py

@csrf_exempt
def get_child_users(request, user_id):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':

        userid = request.POST.get('userId')

        print(userid,"---------------------------------------------")
        user = CustomUser.objects.get(id=int(userid))
        children = CustomUser.objects.filter(parent = user)  # Use related_name 'children'
        
        child_data = []
        for child in children:
            child_data.append({
                'id': child.id,
                'first_name': child.first_name,
                'status': child.role,  # Assuming status is based on the role
                'left_count': 0,  # Adjust based on actual logic
                'right_count': 0  # Adjust based on actual logic
            })
        
        return JsonResponse(child_data, safe=False)
    


    
def about(request):
    return render(request,'about.html')

def Contact(request):
    return render(request,'contact.html')


from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages

@login_required
def change_password(request):
    if request.method == 'POST':
        new_password = request.POST.get("uname")
        new_password_C = request.POST.get("pswd")
        if new_password == new_password_C:
            user = request.user
            user.set_password(new_password)
            user.save()
            
            messages.success(request, 'Your password was successfully updated!')
            return redirect('password_change_done')
        else:
            messages.error(request, 'Please correct the error below.')
            return redirect("change_password")
    
    return render(request, 'change_password.html')

def password_change_done(request):
    return render(request,"passwordchanged.html")





