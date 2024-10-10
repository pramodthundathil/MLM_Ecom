from django.urls import path 
from .import views 
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("Landingpage",views.Landingpage,name="Landingpage"),
    path("",views.Index,name="Index"),
    path("SignUp/<str:token>",views.SignUp,name="SignUp"),
    path("SignIn",views.SignIn,name="SignIn"),
    path("about",views.about,name="about"),
    path("Contact",views.Contact,name="Contact"),
    path("ProfileScreen",views.ProfileScreen,name="ProfileScreen"),
    path("SignOut",views.SignOut,name="SignOut"),
    path("SentRefrelLink",views.SentRefrelLink,name="SentRefrelLink"),
    path("OTPverification/<int:pk>",views.OTPverification,name="OTPverification"),
    path("verify_otp/<int:pk>",views.verify_otp,name="verify_otp"),
    path("VeryfiedOTP",views.VeryfiedOTP,name="VeryfiedOTP"),
    path('get_child_users/<int:user_id>/', views.get_child_users, name='get_child_users'),

    path('change_password', views.change_password, name='change_password'),
    path('password_change_done', views.password_change_done, name='password_change_done'),
    path("TeamsAndConditions",views.TeamsAndConditions,name="TeamsAndConditions"),
    path("PrivacyPolicy",views.PrivacyPolicy,name="PrivacyPolicy"),


    # password reset

    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),


    # for testing only 
    path("TestingPage",views.TestingPage,name="TestingPage"),
    path("SentTestMail",views.SentTestMail,name="SentTestMail")
    
]