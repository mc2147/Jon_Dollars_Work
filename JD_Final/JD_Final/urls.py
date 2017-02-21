from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    
    #logins here
    url(r'^login/', 'StudentApp.views.Login', name='Login'),
   
    #teacher urls start here
	url(r'^teacher/home$', 'TeacherApp.views.TeacherHome', name='TeacherHome'),
	url(r'^teacher/good-deeds$', 'TeacherApp.views.GoodDeeds', name='GoodDeeds'),
	url(r'^teacher/rewards$', 'TeacherApp.views.Rewards', name='Rewards'),
	url(r'^teacher/settings$', 'TeacherApp.views.TeacherSettings', name='TeacherSettings'),
	url(r'^teacher/point-requests$', 'TeacherApp.views.Requests', name='TeacherRequests'),
	url(r'^teacher/spend-requests$', 'TeacherApp.views.SpendRequests', name='TeacherSpendRequests'),
	url(r'^teacher/manage-classes$', 'TeacherApp.views.ManageClasses', name='TeacherManageClasses'),
	
	#student urls start here
	url(r'^student/home$', 'StudentApp.views.StudentHome', name='StudentHome'),
	url(r'^student/team$', 'StudentApp.views.StudentTeam', name='Team'),
	url(r'^student/shop$', 'StudentApp.views.StudentShop', name='Shop'),
	url(r'^student/inventory$', 'StudentApp.views.StudentInventory', name='Inventory'),
	url(r'^student/request-point$', 'StudentApp.views.StudentPointRequest', name='PointRequest'),
	url(r'^student/settings$', 'StudentApp.views.StudentSettings', name='StudentSettings'),

]