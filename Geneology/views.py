from django.shortcuts import render, redirect
from Home.models import *
from .models import *
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required


@login_required(login_url='SignIn')
def AdminDashView(request):
    return render(request,"dashboard/index.html")


def DesignationCalculations(request):
    user = request.user
    total_bv = calculate_total_bv(user)

    # Optionally update the user's designation if total BV exceeds the threshold
    if total_bv > 50000 and user.designation == "Executive":
        user.designation = "Chief Executive"
        user.save()

    # Check for promotion to Manager
    direct_members = CustomUser.objects.filter(parent=user)
    active_executives_count = sum(1 for member in direct_members if member.designation == "Executive" and member.is_active)

    if user.designation == "Chief Executive" and len(direct_members) >= 7 and active_executives_count >= 5:
        user.designation = "Manager"
        user.save()
        
    # Check for promotion to Manager
    direct_members = CustomUser.objects.filter(parent=user)
    active_cheif_executives_count = sum(1 for member in direct_members if member.designation == "Chief Executive" and member.is_active)

    if user.designation == "Manager" and len(direct_members) >= 10 and active_cheif_executives_count >= 5:
        user.designation = "General Manager"
        user.save()

    active_cheif_executives_count = sum(1 for member in direct_members if member.designation == "Manager" and member.is_active)
    if user.designation == "Manager" and len(direct_members) >= 12 and active_cheif_executives_count >= 6:
        user.designation = "Director"
        user.save()

   
    
    print(total_bv,"----------------------------------------------------------")

    return redirect('ProfileScreen')


def calculate_total_bv(user):
    """
    Recursively calculate the total purchase BV for a user and all their descendants.
    """
    # Get the BV for the current user
    my_bv = Business_Volume.objects.get(user=user)
    total_bv = my_bv.purchase_bv

    # Get all direct children of the user
    direct_members = CustomUser.objects.filter(parent=user)

    # Recursively calculate BV for each child
    for child in direct_members:
        total_bv += calculate_total_bv(child)

    return total_bv


@login_required(login_url='SignIn')
def Franchise_Request(request):
    try:
        frachise_req = Franchise_request.objects.get(user = request.user)
    except:
        frachise_req = "You Dont Have Any Franchise or Request"
    if request.method == "POST":
        frachise = request.POST.get('franchise')
        try:
            if request.user.role == "user":
                frachise_reqest = Franchise_request.objects.create(frachise_type = frachise, user = request.user)
                frachise_reqest.save()
                messages.success(request,"Request was sent to admin for approval")
                return redirect("Franchise_Request")
            else:
                messages.info(request,"You are already a {}".format(request.user.role))
                return redirect("Franchise_Request")
        except:
            messages.info(request,"You Already have a request")
            return redirect("Franchise_Request")
    context = {
        "frachise_req":frachise_req,

    }

    return render(request,"franchise_request.html",context)

@login_required(login_url='SignIn')
def delete_franchise_request(request,pk):
    Franchise_request.objects.get(id = pk).delete()
    messages.error(request,"Request was deleted")
    return redirect("Franchise_Request")
    
@login_required(login_url='SignIn')
def FrachiserequestAdmin(request):
    franchaise = Franchise_request.objects.all()
    context = {
        "franchaise":franchaise
    }
    return render(request,"dashboard/franchaiserequests.html",context)

@login_required(login_url='SignIn')
def FrachiseRequestSingleview(request,pk):
    req  = Franchise_request.objects.get(id = pk)
    context ={
        "req":req
    }
    return render(request,'dashboard/singlefranchiserequest.html',context)

@login_required(login_url='SignIn')
def Approve_franchise(request,pk):
    req  = Franchise_request.objects.get(id = pk)
    member = req.user 
    member.role = req.frachise_type
    member.save()
    req.delete()
    messages.success(request,"Franchise Request approved")
    return redirect("FrachiserequestAdmin")

@login_required(login_url='SignIn')
def delete_franchise_request_admin(request,pk):
    Franchise_request.objects.get(id = pk).delete()
    messages.error(request,"Request was deleted")
    return redirect("FrachiserequestAdmin")

# admin dashboard for mlm transactions 

@login_required(login_url='SignIn')
def UsersAdminPannel(request):
    users = CustomUser.objects.all()
    context = {
        "users":users
    }
    return render(request,"dashboard/users.html",context)


@login_required(login_url='SignIn')
def UsersingleViewAdmin(request,pk):
    user = CustomUser.objects.get(id = pk)
    BV = Business_Volume.objects.get(user = user)
    bankdetails = AccountDetails.objects.get(user = user)
    noinee = Nominee.objects.get(user = user)
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
        "first_level_members": first_level_members,
        "all_levels_members": all_levels_members,
        "bankdetails":bankdetails,
        "noinee":noinee,
        "member":user
    }
    return render(request,"dashboard/adminuserprofile.html",context)

@login_required(login_url='SignIn')
def disableuserAdmin(request,pk):
    member = CustomUser.objects.get(id = pk)
    if member.is_active == False:
        member.is_active = True
    else:
        member.is_active = False
    member.save()
    messages.info(request,"Member status changed")
    return redirect("UsersingleViewAdmin", pk = pk)


@login_required(login_url='SignIn')
def TokenIdentification(request):
    if request.method == "POST":
        token = request.POST.get("name")
    try:
        CustomUser.objects.get(id_number = token)
        return redirect("UserAddByAdmin",token = token)
    except:
        messages.info(request,"Sponser id is invalid..")
        return redirect("UsersAdminPannel")


from django.utils.crypto import get_random_string

def generate_unique_id_number():
    while True:
        id_num = 'ADCOS' + get_random_string(length=5, allowed_chars='0123456789')
        if not CustomUser.objects.filter(id_number=id_num).exists():
            return id_num  # Break the loop and return the unique ID number

@login_required(login_url='SignIn')
def UserAddByAdmin(request,token):
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
            return redirect('UserAddByAdmin',token = token)

        try:
            if CustomUser.objects.filter(pancard = pan ).exists():
                messages.info(request,"Pancard Alredy exists...")
                return redirect("UserAddByAdmin",token = token)
            if CustomUser.objects.filter(email = email ).exists():
                messages.info(request,"Email Id  Already exists...")
                return redirect("UserAddByAdmin",token = token)
            if CustomUser.objects.filter(phone_number=pnum).exists():
                messages.info(request,"Phonenumber  Already exists...")
                return redirect("UserAddByAdmin",token = token)
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
                    is_active = True
                )
                user.set_password(pswd)
                user.save()
               

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
                messages.success(request, "User registered successfully.")
                return redirect("UsersAdminPannel")

        except ValidationError as e:
            messages.error(request, e.messages)
            return redirect('UserAddByAdmin',token = token)
    context = {
        
        "sponsor":sponser
    }
    return render(request,'dashboard/memberregistration.html',context)



# Franchises....................

@login_required(login_url='SignIn')
def StateFranchise(request):
    franchise_type = "State Franchise"
    users = CustomUser.objects.filter(role = "central_franchise")
    context = {
        "franchise_type":franchise_type,
        "users":users
    }
    return render(request,"dashboard/Franchises_category.html",context)

@login_required(login_url='SignIn')
def DistrictFranchise(request):
    franchise_type = "District Franchise"
    users = CustomUser.objects.filter(role = "district_franchise")
    context = {
        "franchise_type":franchise_type,
        "users":users
    }
    return render(request,"dashboard/Franchises_category.html",context)

@login_required(login_url='SignIn')
def ZonelFranchise(request):
    franchise_type = "Zonel Franchise"
    users = CustomUser.objects.filter(role = "zonel_franchise")
    context = {
        "franchise_type":franchise_type,
        "users":users
    }
    return render(request,"dashboard/Franchises_category.html",context)


@login_required(login_url='SignIn')
def MobileFranchise(request):
    franchise_type = "Mobile Franchise"
    users = CustomUser.objects.filter(role = "mobile_franchise")
    context = {
        "franchise_type":franchise_type,
        "users":users
    }
    return render(request,"dashboard/Franchises_category.html",context)



# id card creation 

import qrcode
from io import BytesIO
import base64
from django.shortcuts import render
from .models import CustomUser
from django.contrib.sites.shortcuts import get_current_site

@login_required(login_url='SignIn')
def generate_id_card(request):
    # Get the user instance
    user =  request.user
    
     # Generate the QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    current_site = get_current_site(request)
    domain = current_site.domain
    qr_data = f"{domain}/SignUp/{user.id_number}"
    qr.add_data(qr_data)
    qr.make(fit=True)

    # Generate QR code image
    img = qr.make_image(fill='Green', back_color='white')

    # Save the QR code to a BytesIO object
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    # Encode the image to base64
    qr_code_image = base64.b64encode(buffer.read()).decode('utf-8')

    # Pass the encoded image to the template
    context = {
        'user': user,
        'qr_code_image': qr_code_image
    }

    return render(request, 'id_card.html', context)



@login_required(login_url='SignIn')
def generate_id_card_pdf(request):
    user =  request.user
    
     # Generate the QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    current_site = get_current_site(request)
    domain = current_site.domain
    qr_data = f"{domain}/SignUp/{user.id_number}"
    qr.add_data(qr_data)
    qr.make(fit=True)

    # Generate QR code image
    img = qr.make_image(fill='Green', back_color='white')

    # Save the QR code to a BytesIO object
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    # Encode the image to base64
    qr_code_image = base64.b64encode(buffer.read()).decode('utf-8')

    # Pass the encoded image to the template
    context = {
        'user': user,
        'qr_code_image': qr_code_image
    }

    return render(request, 'id_card_pdf.html', context)

@login_required(login_url='SignIn')
def GeneologyStatistic(request):
    # Fetch first-level members directly sponsored by the logged-in user
    first_level_members = CustomUser.objects.filter(parent=request.user)

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
        "first_level_members": first_level_members,
        "all_levels_members": all_levels_members
    }
    return render(request, 'statistics.html', context)


def StateSponsership(request):
    sponsers = FreeSponsership.objects.all()
    return render(request,"unregistedusers_freesponsership.html",{"sponsers":sponsers})

@login_required(login_url='SignIn')
def FreesponsershipAdd(request):
    sponser = FreeSponsership.objects.all()
    if request.method == "POST":
        sponser = request.POST.get('name')
        idnumber = request.POST.get('idnum')
        sponser = FreeSponsership.objects.create(name = sponser, idnumber = idnumber)
        sponser.save()
        messages.success(request,"State Sponsership Added..")
        return redirect("FreesponsershipAdd")
    return render(request,"dashboard/sponsership.html",{"sponser":sponser})

def DeleteFreeSponsership(request,pk):
    FreeSponsership.objects.get(id = pk).delete()
    messages.info(request,"Sponsership Deleted....")
    return redirect("FreesponsershipAdd")







