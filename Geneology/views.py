from django.shortcuts import render, redirect
from Home.models import *
from .models import *
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



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

def delete_franchise_request(request,pk):
    Franchise_request.objects.get(id = pk).delete()
    messages.error(request,"Request was deleted")
    return redirect("Franchise_Request")
    
def FrachiserequestAdmin(request):
    franchaise = Franchise_request.objects.all()
    context = {
        "franchaise":franchaise
    }
    return render(request,"dashboard/franchaiserequests.html",context)

def FrachiseRequestSingleview(request,pk):
    req  = Franchise_request.objects.get(id = pk)
    context ={
        "req":req
    }
    return render(request,'dashboard/singlefranchiserequest.html',context)

def Approve_franchise(request,pk):
    req  = Franchise_request.objects.get(id = pk)
    member = req.user 
    member.role = req.frachise_type
    member.save()
    req.delete()
    messages.success(request,"Franchise Request approved")
    return redirect("FrachiserequestAdmin")

def delete_franchise_request_admin(request,pk):
    Franchise_request.objects.get(id = pk).delete()
    messages.error(request,"Request was deleted")
    return redirect("FrachiserequestAdmin")

# admin dashboard for mlm transactions 

def UsersAdminPannel(request):
    users = CustomUser.objects.all()
    context = {
        "users":users
    }
    return render(request,"dashboard/users.html",context)


def UsersingleViewAdmin(request,pk):
    user = CustomUser.objects.get(id = pk)
    BV = Business_Volume.objects.get(user = user)
    bankdetails = AccountDetails.objects.get(user = user)
    noinee = Nominee.objects.get(user = user)
    # print(user.first_name,"------------------------------------")
    context = {
        "BV":BV,
        "bankdetails":bankdetails,
        "noinee":noinee,
        "member":user
    }
    return render(request,"dashboard/adminuserprofile.html",context)

def disableuserAdmin(request,pk):
    member = CustomUser.objects.get(id = pk)
    if member.is_active == False:
        member.is_active = True
    else:
        member.is_active = False
    member.save()
    messages.info(request,"Member status changed")
    return redirect("UsersingleViewAdmin", pk = pk)


def TokenIdentification(request):
    if request.method == "POST":
        token = request.POST.get("name")
    try:
        CustomUser.objects.get(id_number = token)
        return redirect("UserAddByAdmin",token = token)
    except:
        messages.info(request,"Sponser id is invalid..")
        return redirect("UsersAdminPannel")

def generate_unique_id_number():
    return str(uuid.uuid4().hex[:5]).upper()

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
                return redirect("UsersingleViewAdmin", pk = user.id )

        except ValidationError as e:
            messages.error(request, e.messages)
            return redirect('register')
    context = {
        
        "sponsor":sponser
    }
    return render(request,'dashboard/memberregistration.html',context)



# Franchises....................

def StateFranchise(request):
    franchise_type = "State Franchise"
    users = CustomUser.objects.filter(role = "central_franchise")
    context = {
        "franchise_type":franchise_type,
        "users":users
    }
    return render(request,"dashboard/Franchises_category.html",context)

def DistrictFranchise(request):
    franchise_type = "District Franchise"
    users = CustomUser.objects.filter(role = "district_franchise")
    context = {
        "franchise_type":franchise_type,
        "users":users
    }
    return render(request,"dashboard/Franchises_category.html",context)

def ZonelFranchise(request):
    franchise_type = "Zonel Franchise"
    users = CustomUser.objects.filter(role = "zonel_franchise")
    context = {
        "franchise_type":franchise_type,
        "users":users
    }
    return render(request,"dashboard/Franchises_category.html",context)


def MobileFranchise(request):
    franchise_type = "Mobile Franchise"
    users = CustomUser.objects.filter(role = "mobile_franchise")
    context = {
        "franchise_type":franchise_type,
        "users":users
    }
    return render(request,"dashboard/Franchises_category.html",context)




