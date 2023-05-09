from django.urls import path
from . import views

urlpatterns = [
    path('', views.showc, name='customer_dashboard'),
    path('coaches/',views.showc),
    path('commodities/',views.showcommodities, name='commodities'),
    path('c_equipment/',views.showequipment),
    path('c_cards/',views.showcards),
    path('c_block/',views.showblock),
    path('courses/',views.showcourses),
    path('c_order/',views.showorder),
    path('update_balance/', views.update_balance, name='update_balance'),
    path('register_membership/', views.register_membership, name='join_membership'),
    path('purchase/', views.purchase, name='purchase'),
    path('select_course/', views.select_course, name='select_course'),
    path('c_personal_info/',views.showpp),
]
