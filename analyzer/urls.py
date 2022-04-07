from django.urls import path
from . import views

urlpatterns = [
    path('', views.AiAnalyzer.as_view(), name='analyzer'),
    path('result', views.result, name='result'),
    path('analisador_store/', views.analyzer_store, name='analyzer_store'),
    path('get_result', views.get_result, name='get_result'),
    path('download/', views.download_file, name='download'),
    # path('download/<str:results_path>', views.download_file, name='download'),
]
