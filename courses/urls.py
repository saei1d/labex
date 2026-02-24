from django.urls import path , include

urlpatterns = [
    path('', include('courses.api_admin.urls'))
]