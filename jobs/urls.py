from django.urls import path
from . import views


urlpatterns = [

    path(
        "",
        views.job_list,
        name="job_list"
    ),

    path(
        "job/<int:job_id>/",
        views.job_detail,
        name="job_detail"
    ),

    path(
        "job/<int:job_id>/apply/",
        views.apply_job,
        name="apply_job"
    ),

    path(
        "my-applications/",
        views.my_applications,
        name="my_applications"
    ),

    path(
        "employer-applications/",
        views.employer_applications,
        name="employer_applications"
    ),

    path(
        "application/<int:application_id>/status/",
        views.update_application_status,
        name="update_application_status"
    ),

    path(
        "post-job/",
        views.post_job,
        name="post_job"
    ),

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard"
    ),

    path(
        "register/",
        views.register,
        name="register"
    ),

    path(
        "login/",
        views.login_user,
        name="login"
    ),

    path(
        "logout/",
        views.logout_user,
        name="logout"
    ),
]