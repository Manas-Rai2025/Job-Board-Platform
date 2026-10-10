from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q

from .models import Job, Application, UserProfile


def job_list(request):

    query = request.GET.get("q", "")

    if query:
        jobs = Job.objects.filter(
            Q(title__icontains=query) |
            Q(company__icontains=query) |
            Q(location__icontains=query)
        ).order_by("-created_at")

    else:
        jobs = Job.objects.all().order_by("-created_at")

    return render(
        request,
        "jobs/job_list.html",
        {
            "jobs": jobs,
            "query": query
        }
    )


def job_detail(request, job_id):

    job = get_object_or_404(
        Job,
        id=job_id
    )

    already_applied = False

    if request.user.is_authenticated:

        already_applied = Application.objects.filter(
            user=request.user,
            job=job
        ).exists()

    return render(
        request,
        "jobs/job_detail.html",
        {
            "job": job,
            "already_applied": already_applied
        }
    )


def apply_job(request, job_id):

    job = get_object_or_404(
        Job,
        id=job_id
    )

    if not request.user.is_authenticated:

        messages.error(
            request,
            "Please login as a candidate before applying."
        )

        return redirect("login")

    if not hasattr(request.user, "profile"):

        messages.error(
            request,
            "User profile not found."
        )

        return redirect("job_detail", job_id=job.id)

    if request.user.profile.role != "candidate":

        messages.error(
            request,
            "Only candidates can apply for jobs."
        )

        return redirect(
            "job_detail",
            job_id=job.id
        )

    already_applied = Application.objects.filter(
        user=request.user,
        job=job
    ).exists()

    if already_applied:

        messages.info(
            request,
            "You have already applied for this job."
        )

        return redirect(
            "job_detail",
            job_id=job.id
        )

    if request.method == "POST":

        Application.objects.create(
            user=request.user,
            job=job,
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            phone=request.POST.get("phone"),
            resume=request.FILES.get("resume"),
            cover_letter=request.POST.get(
                "cover_letter",
                ""
            )
        )

        return render(
            request,
            "jobs/application_success.html",
            {"job": job}
        )

    return render(
        request,
        "jobs/apply.html",
        {"job": job}
    )


def my_applications(request):

    if not request.user.is_authenticated:

        messages.error(
            request,
            "Please login to view your applications."
        )

        return redirect("login")

    applications = Application.objects.filter(
        user=request.user
    ).select_related(
        "job"
    ).order_by(
        "-applied_at"
    )

    return render(
        request,
        "jobs/my_applications.html",
        {
            "applications": applications
        }
    )


def employer_applications(request):

    if not request.user.is_authenticated:

        messages.error(
            request,
            "Please login as an employer."
        )

        return redirect("login")

    if not hasattr(request.user, "profile"):

        messages.error(
            request,
            "User profile not found."
        )

        return redirect("job_list")

    if request.user.profile.role != "employer":

        messages.error(
            request,
            "Only employers can view applications."
        )

        return redirect("dashboard")

    applications = Application.objects.select_related(
        "job",
        "user"
    ).order_by(
        "-applied_at"
    )

    return render(
        request,
        "jobs/employer_applications.html",
        {
            "applications": applications
        }
    )


def update_application_status(
    request,
    application_id
):

    if not request.user.is_authenticated:

        return redirect("login")

    if not hasattr(request.user, "profile"):

        return redirect("job_list")

    if request.user.profile.role != "employer":

        messages.error(
            request,
            "Only employers can update application status."
        )

        return redirect("dashboard")

    application = get_object_or_404(
        Application,
        id=application_id
    )

    if request.method == "POST":

        status = request.POST.get("status")

        valid_statuses = [
            "Applied",
            "Reviewing",
            "Shortlisted",
            "Rejected"
        ]

        if status in valid_statuses:

            application.status = status
            application.save()

            messages.success(
                request,
                "Application status updated successfully."
            )

    return redirect(
        "employer_applications"
    )


def post_job(request):

    if not request.user.is_authenticated:

        messages.error(
            request,
            "Please login before posting a job."
        )

        return redirect("login")

    if not hasattr(request.user, "profile"):

        messages.error(
            request,
            "User profile not found."
        )

        return redirect("job_list")

    if request.user.profile.role != "employer":

        messages.error(
            request,
            "Only employers can post jobs."
        )

        return redirect("job_list")

    if request.method == "POST":

        Job.objects.create(
            title=request.POST.get("title"),
            company=request.POST.get("company"),
            location=request.POST.get("location"),
            salary=request.POST.get("salary"),
            description=request.POST.get(
                "description"
            )
        )

        return redirect("job_list")

    return render(
        request,
        "jobs/post_job.html"
    )


def dashboard(request):

    if not request.user.is_authenticated:

        return redirect("login")

    if not hasattr(request.user, "profile"):

        messages.error(
            request,
            "User profile not found."
        )

        return redirect("job_list")

    if request.user.profile.role == "candidate":

        applications = Application.objects.filter(
            user=request.user
        )

        total_applications = applications.count()

        reviewing = applications.filter(
            status="Reviewing"
        ).count()

        shortlisted = applications.filter(
            status="Shortlisted"
        ).count()

        rejected = applications.filter(
            status="Rejected"
        ).count()

        return render(
            request,
            "jobs/dashboard.html",
            {
                "role": "candidate",
                "total_applications": total_applications,
                "reviewing": reviewing,
                "shortlisted": shortlisted,
                "rejected": rejected
            }
        )

    if request.user.profile.role == "employer":

        jobs = Job.objects.all()

        total_jobs = jobs.count()

        total_applications = Application.objects.filter(
            job__in=jobs
        ).count()

        return render(
            request,
            "jobs/dashboard.html",
            {
                "role": "employer",
                "total_jobs": total_jobs,
                "total_applications": total_applications
            }
        )

    return redirect("job_list")


def register(request):

    if request.method == "POST":

        username = request.POST.get(
            "username"
        )

        email = request.POST.get(
            "email"
        )

        password = request.POST.get(
            "password"
        )

        role = request.POST.get(
            "role"
        )

        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                "Username already exists."
            )

            return redirect("register")

        if role not in [
            "candidate",
            "employer"
        ]:

            messages.error(
                request,
                "Please select a valid account type."
            )

            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        UserProfile.objects.create(
            user=user,
            role=role
        )

        login(
            request,
            user
        )

        return redirect("dashboard")

    return render(
        request,
        "jobs/register.html"
    )


def login_user(request):

    if request.method == "POST":

        username = request.POST.get(
            "username"
        )

        password = request.POST.get(
            "password"
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            return redirect(
                "dashboard"
            )

        messages.error(
            request,
            "Invalid username or password."
        )

    return render(
        request,
        "jobs/login.html"
    )


def logout_user(request):

    logout(request)

    return redirect(
        "job_list"
    )