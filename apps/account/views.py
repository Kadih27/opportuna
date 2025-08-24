import logging
from django.shortcuts import render, redirect

from apps.account.backends import EmailBackend
from apps.account.forms import *
from apps.utils import generate_username
import django.contrib.messages as messages
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str as force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from apps.account.tokens import account_activation_token, reset_activation_token
from django.contrib.auth import logout, login, update_session_auth_hash

logger = logging.getLogger("django")

User = get_user_model()



def register_student(request):

    form = StudentRegistrationForm(request.POST or None)
    if form.is_valid():
        # form = form.save()
        #
        user = form.save(commit=False)
        user.is_active = False
        user.first_login = True
        to_email = form.cleaned_data.get("email")
        user.username = generate_username(to_email)
        user.role = 3
        user.save()


        print('Account created successfully!')
        logger.info(f"User model {user.id} saved")



        # Send verification mail. Handle any exception that could occur.
        try:
            verify_email(user, request)
            logger.info(f"Send verification email for {user.username}")
            logger.info(f"Send New User {user.username} notification to Project...")

            send_mail(
                user.username + " registered to Project",
                "A new user ("
                + user.username
                + ") with email "
                + " has registered to Project Managemant",
                "berthekadidiatou27@gmail.com",
                ['lougbegnona@gmail.com'],
                fail_silently=False,
            )

            messages.success(request, 'Your account has been  registered successfully!')

            return redirect('/login/')
        except Exception as e:
            print(e)
            msg = "Error sending the verification message"
            messages.error(request, msg)
            logger.error(f"Error sending the verification message: {e}")

        return redirect('login_view')
    else:
        print(form.errors)
    context = {
        'form': form,
    }

    return render(request, 'apps/account/student-registration.html', context)


def register_company(request):
    """
    Handle Employee Registration

    """
    form = EnterpriseRegistrationForm(request.POST or None)
    formCompany = CompanyRegistrationForm(request.POST or None)

    if form.is_valid() and formCompany.is_valid():
        # form = form.save()

        user = form.save(commit=False)
        user.is_active = False
        user.first_login = True
        to_email = form.cleaned_data.get("email")
        user.username = generate_username(to_email)
        user.role = 3
        user.save()

        # Save company with the user as responsible
        company = formCompany.save(commit=False)
        company.responsible = user  # Set the user instance, not just the pk
        company.save()  # Now save with the responsible field set

        # Send verification mail. Handle any exception that could occur.
        try:
            verify_email(user, request)
            logger.info(f"Send verification email for {user.username}")
            logger.info(f"Send New User {user.username} notification to Project...")

            send_mail(
                user.username + " registered to Project",
                "A new user ("
                + user.username
                + ") with email "
                + " has registered to Project Managemant",
                "berthekadidiatou27@gmail.com",
                ['lougbegnona@gmail.com'],
                fail_silently=False,
            )

            messages.success(request, 'Your account has been  registered successfully!')

            return redirect('login_view')
        except Exception as e:
            print(e)
            msg = "Error sending the verification message"
            messages.error(request, msg)
            logger.error(f"Error sending the verification message: {e}")


        return redirect('login_view')

    else:
        # Print errors for debugging
        if not form.is_valid():
            print("User form errors:", form.errors)
        if not formCompany.is_valid():
            print("Company form errors:", formCompany.errors)

    context = {
        'formCompany': formCompany,
        'form': form
    }

    return render(request, 'apps/account/create-company.html', context)


# def register_company(request):
#     if request.method == 'POST':
#         cname = request.POST.get('cname')
#         ceo = request.POST.get('ceo')
#         tagline = request.POST.get('tagline')
#         des = request.POST.get('des')
#         phone = request.POST.get('phone')
#         website = request.POST.get('website')
#         category = request.POST.get('category')
#
#         empno = request.POST.get('empno')
#         started = request.POST.get('started')
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         photo=request.FILES.get('photo')
#         license=request.FILES.get('license')
#         # Check if email already exists
#         if Job_Providers.objects.filter(email=email).exists():
#             msg = 'User Already Exists'
#             return render(request, 'seekera/create-company.html',{'msg':msg})
#
#         # Create Job_Providers object and save to database
#         Job_Providers.objects.create(
#             cname=cname,
#             ceo=ceo,
#             tagline=tagline,
#             category=category,
#             des=des,
#             phone=phone,
#             website=website,
#             empno=empno,
#             started=started,
#             email=email,
#             password=password,
#             license=license,
#             photo=photo
#         )
#
#         # Redirect to login page
#         return redirect('/login2')
#
#     return render(request, 'seekera/create-company.html')



def login_view(request):
    """Login page, only an anonymous user.
    Already logged-in users that are also Individual get redirected to the right page.
    """

    form = LoginForm(request.POST or None)
    msg, municipality = "", None

    if form.is_valid():
      email = form.cleaned_data.get("email")
      password = form.cleaned_data.get("password")
      print(email)
      print(password)

      email_backend = EmailBackend()
      user = email_backend.authenticate(request, username=email, password=password)

      if user is not None:
        login(request, user, backend="apps.account.backends.EmailBackend")
        if user.is_active:
          print(user)
          print(user.get_role)
          print("Je suis bien connecté et je suis redirigé")
          if user.role == 2:
              return redirect("dashboard_student")

          if user.role == 3:
              return redirect("dashboard_enterprise")

          if user.role == 4:
              return redirect("dashboard_professor")


          return redirect("home")
        else:
          msg = "Please confirm your email before logging in."
          messages.error(request, msg)
        return redirect("login")
      else:
        msg = "Please confirm your email before logging in."
        messages.error(request, msg)
    else:
      print(form.errors)
      if request.method == "POST":
        msg = "We couldn't validate your email. Please try again."
        messages.error(request, msg)

    return render(request, "apps/account/login.html", {"form": form, "msg": msg})


def logout_view(request):
    logout(request)
    messages.success(request, "You are successfully logout")
    return redirect('login_view')


def verify_email(user, request):
    """Send verification mail"""
    site_domain = get_current_site(request)
    from_email = settings.DEFAULT_FROM_EMAIL
    mail_subject = "Account Registration Confirmation"
    to_email = user.email

    msge = render_to_string(
      "apps/account/acc_active_email.txt",
      {
        "username": user.username,
        "url": reverse(
          "activate",
          kwargs={
            "uidb64": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": account_activation_token.make_token(user),
          },
        ),
        "domain": site_domain,
        "scheme": "http",
      },
    )

    msge_html = render_to_string(
      "apps/account/acc_active_email.html",
      {
        "username": user.username,
        "url": reverse(
          "activate",
          kwargs={
            "uidb64": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": account_activation_token.make_token(user),
          },
        ),
        "domain": site_domain,
        "scheme": "http",
      },
    )
    send_mail(
      mail_subject,
      msge,
      from_email,
      [to_email, ],
      fail_silently=False,
      html_message=msge_html,
    )


def activate(request, uidb64, token):
    response = None
    try:
      uid = force_text(urlsafe_base64_decode(uidb64))
      user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
      user = None
    if user is not None and account_activation_token.check_token(user, token):
      user.is_active = True
      user.save()
      response = "Thank you for confirming your email. Your account has been activated."
      messages.success(request, "Thank you for confirming your email. Your account has been activated.")
    return render(
      request,
      "apps/account/account_activation_status.html",
      {"response": response},
    )