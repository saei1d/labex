from django.urls import path , include

urlpatterns = [
    path('',include('courses.admin.urls'))
]