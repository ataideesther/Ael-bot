from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('iniciar/', views.iniciar_conversa, name='iniciar_conversa'),
    path('continuar/', views.continuar_conversa, name='continuar_conversa'),
    path('ask/', views.ask_question, name='ask_question'),
    path('debug/', views.debug_sessoes, name='debug_sessoes'),  # Para teste
]