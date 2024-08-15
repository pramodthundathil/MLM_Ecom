from django.urls import path 
from .import views 

urlpatterns = [
            
        path("AdminDashView",views.AdminDashView,name="AdminDashView"),
        path("DesignationCalculations",views.DesignationCalculations,name="DesignationCalculations"),
        path("Franchise_Request",views.Franchise_Request,name="Franchise_Request"),
        path("delete_franchise_request/<int:pk>",views.delete_franchise_request,name="delete_franchise_request"),
]