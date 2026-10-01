from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.kanban_board, name='kanban'),
    path('kanban/content/', views.kanban_content, name='kanban_content'),
    path('tasks/create/modal/', views.create_task_modal, name='create_task_modal'),
    path('tasks/<int:pk>/move/<str:new_status>/', views.move_task, name='move_task'),
    path('<int:pk>/advance-status/', views.advance_status_modal, name='advance_status'),
]
