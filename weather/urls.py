from django.urls  import path
from . import views

app_name = "weather"

urlpatterns = [
  path('', views.home, name='home'),
  path('api/get_weather/', views.get_weather, name='get_weather'),
  path("queries/create/", views.create_query, name="create_query"),
  path("records/<int:pk>/update/", views.update_record, name="update_record"),
  path("queries/<int:pk>/delete/", views.delete_query, name="delete_query")
]
