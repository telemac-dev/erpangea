from django.urls import path
from . import views

app_name = 'commercial'

urlpatterns = [
    path('proposals/', views.proposal_list, name='proposal_list'),
    path('proposals/create/modal/', views.create_proposal_modal, name='create_proposal_modal'),
    path('proposals/<int:pk>/approve/', views.approve_proposal, name='approve_proposal'),
]
