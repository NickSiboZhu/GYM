from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

app_name = 'manager'

urlpatterns = [
    path('', views.manager_dashboard, name='manager_dashboard'),
    path('supplements/', views.supplements, name='supplements'),
    path('equipment/', views.equipment, name='equipment'),
    path('coaches/', views.coaches, name='coaches'),
    path('courses/', views.courses, name='courses'),
    path('membership_cards/', views.membership_cards, name='membership_cards'),
    path('personal_info/', views.personal_info, name='personal_info'),
    path('data_visual/', views.data_visual, name='data_visual'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('add_coach/', views.add_coach, name='add_coach'),
    path('delete_coach/<int:coach_id>/', views.delete_coach, name='delete_coach'),
    path('add_supplement/', views.add_supplement, name='add_supplement'),
    path('delete_supplement/<int:supplement_id>/', views.delete_supplement, name='delete_supplement'),
    path('update_supplement_stock/<int:supplement_id>/',views.update_supplement_stock,name='update_supplement_stock'),
    path('update_supplement_price/<int:supplement_id>/',views.update_supplement_price,name='update_supplement_price'),
    path('add_course/', views.add_course, name='add_course'),
    path('delete_course/<int:course_id>/', views.delete_course, name='delete_course'),
    path('add_equipment/', views.add_equipment, name='add_equipment'),
    path('delete_equipment/<int:equipment_id>/', views.delete_equipment, name='delete_equipment'),
    # Add paths for other views here (e.g. commodities, equipment, coaches, courses, membership_cards, personal_information)
]
