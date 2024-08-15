from django.shortcuts import render, redirect
from Home.models import *
from .models import *
from django.contrib import messages



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
    




