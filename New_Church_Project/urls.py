"""
URL configuration for library_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from main import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('dashboard', views.dashboard, name='dashboard'),

    path('members', views.members, name='members'),

    path('church_projects/', views.church_projects, name='church_projects'),

    path('members/delete/<int:member_id>', views.delete_member, name='delete_member'),

    path('add/member', views.add_member, name='add_member'),

    path('member_reg', views.member_reg, name='member_reg'),

    path('members/details/<int:member_id>', views.member_details, name='member_details'),

    path('members/deposit/<int:member_id>', views.deposit, name='deposit'),

    path('members/transaction/<int:member_id>', views.deposit, name='deposit'),

    path('members/update/<int:member_id>', views.update_member, name='update_member'),

    path('profile_view/<int:member_id>/', views.profile_view, name='profile_view'),

    # path('members/search', views.search_member, name='search_member'),

    path('handle/payment/transactions', views.callback, name='callback'),

    path('pie-chart', views.pie_chart, name='pie_chart'),

    path('line-chart', views.line_chart, name='line_chart'),

    path('bar-chart', views.bar_chart, name='bar_chart'),

    path('register/', views.register, name='register'),

    path('', views.login_page, name='login'),

    path('logout/', views.logout_page, name='logout'),

    # path('project/', views.project, name='project'),

    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
