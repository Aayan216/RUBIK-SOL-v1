from django.urls import path
from . import views

urlpatterns = [
    path('', views.capture, name='capture'),
    path('detect/', views.detect, name='detect'),
    path('detect-face/', views.detect_face, name='detect_face'),
    path('solve/', views.solve, name='solve'),
    path('solve-page/', views.solve_page, name='solve_page'),
    path('save-solve/', views.save_solve, name='save_solve'),
    path('history/', views.history, name='history'),
]
