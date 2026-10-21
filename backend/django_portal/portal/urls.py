from django.urls import include, path

urlpatterns = [path('api/', include('portal_api.urls'))]
