from django.urls import path
from apps.dashboard import views



urlpatterns = [
    path("dashboard", views.dashboard, name="dashboard"),
    path("dashboard_student", views.dashboard_student, name="dashboard_student"),
    path("dashboard_enterprise", views.dashboard_enterprise, name="dashboard_enterprise"),
    path("dashboard_professor", views.dashboard_professor, name="dashboard_professor"),
    # path('edit-seeker', views.editseeker, name='editseeker'),
    path('view_profile', views.viewprofile_seeker, name="view_profile"),
    path('upload', views.upload_resume, name="upload_resume"),
    path('resume/<int:pk>/', views.resume_detail, name="resume_detail"),
    path('postjob', views.post_job, name="postjob"),
    path('postjob_file/', views.post_job_excel, name="post_job_excel"),
    path('postedjob', views.postedjobs, name="postedjob"),
    # path('view_job/<str:reference>', views.single_job_view_provider, name='view_job_provider'),
    path('view_job/<str:reference>/', views.single_job_view, name='view_job_provider'),
    path('view_post/<str:reference>/', views.single_post_view, name='view_post'),
    path('chatbot/', views.chat_page, name='chat_page'),
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
    path('list_posts/public/', views.post_list_public, name='job_list_public'),
]