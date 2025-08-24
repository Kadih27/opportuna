from django.shortcuts import render

def index(request):
    return render(request, 'apps/home/index.html')


def error_404(request):
    return render(request, 'apps/home/404.html')


def contact(request):
    return render(request, 'apps/home/contact-us.html')


def search_results_seeker(request):
    try:
        sid = request.session['sid']
        print(sid)
        b = Job_Seekers.objects.filter(sid=sid)
        noti = Post_Job.objects.filter(status='Open').order_by('-timestamp')[:3]
        noti2 = Apply.objects.filter(sid=sid).order_by('-timestamp')[:3]
        title = request.GET.get('title')
        location = request.GET.get('location')

        if title and location:
            results = Post_Job.objects.filter(title__icontains=title, location__iexact=location)
        elif title:
            results = Post_Job.objects.filter(title__icontains=title)
        elif location:
            results = Post_Job.objects.filter(location__iexact=location)
        else:
            results = Post_Job.objects.none()
        all = {
            'b': b,
            'results': results,
            'noti':noti,
            'noti2':noti2
        }
        return render(request, 'seekera/search_results-seeker.html',all)
    except:
        return login(request)
