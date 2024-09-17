from django.urls import path 
from .import views 

urlpatterns = [
            
        path("AdminDashView",views.AdminDashView,name="AdminDashView"),
        path("DesignationCalculations",views.DesignationCalculations,name="DesignationCalculations"),
        path("Franchise_Request",views.Franchise_Request,name="Franchise_Request"),
        path("delete_franchise_request/<int:pk>",views.delete_franchise_request,name="delete_franchise_request"),
        path("FrachiserequestAdmin",views.FrachiserequestAdmin,name="FrachiserequestAdmin"),
        path("UsersAdminPannel",views.UsersAdminPannel,name="UsersAdminPannel"),
        path("UsersingleViewAdmin/<int:pk>",views.UsersingleViewAdmin,name="UsersingleViewAdmin"),
        path("disableuserAdmin/<int:pk>",views.disableuserAdmin,name="disableuserAdmin"),
        path("UserAddByAdmin/<str:token>",views.UserAddByAdmin,name="UserAddByAdmin"),
        path("TokenIdentification",views.TokenIdentification,name="TokenIdentification"),

        
]