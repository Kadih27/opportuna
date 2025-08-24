from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.db.models import Q
from .forms import *
from .models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import fitz  # PyMuPDF
from openai import OpenAI, APIError, AuthenticationError
import os, json, re
from django.core.files.storage import FileSystemStorage
import django.contrib.messages as messages
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.core.paginator import Paginator




client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@login_required(login_url='login_view')
def dashboard(request):
    """Login page, only an anonymous user.
    Already logged-in users that are also Individual get redirected to the right page.
    """
    user = request.user

    if user.role == 2:
      return redirect("dashboard_student")

    if user.role == 3:
      return redirect("dashboard_enterprise")

    if user.role == 4:
      return redirect("dashboard_professor")
    else:
        return redirect("home")



@login_required(login_url='login_view')
def dashboard_student(request):
    print("je suis venu ici")
    print("User:", request.user)
    print("Is authenticated:", request.user.is_authenticated)
    context = {

    }
    return render(request, "apps/dashboard/jobseekerhome.html", context)


@login_required(login_url='login_view')
def dashboard_enterprise(request):
    jobs = []
    savedjobs = []
    appliedjobs = []
    total_applicants = {}
    print(request.user.role)
    if request.user.role == 3:
        company = Company.objects.get(responsible=request.user.id)

        posts = Post.objects.filter(company_id=company.id)
        # jobs = Post.objects.filter(user=request.user.id)
        # jobs = Job.objects.filter(user=request.user.id)
        for job in jobs:
            count = Applicant.objects.filter(job=job.id).count()
            total_applicants[job.id] = count

    if request.user.role == 'employee':
        savedjobs = BookmarkJob.objects.filter(user=request.user.id)
        appliedjobs = Applicant.objects.filter(user=request.user.id)
    context = {
        'posts': posts,
        'jobs': jobs,
        'savedjobs': savedjobs,
        'appliedjobs': appliedjobs,
        'total_applicants': total_applicants
    }

    return render(request, "apps/dashboard/jobproviderhome.html", context)


def post_job(request):
    company = Company.objects.get(responsible=request.user.id)
    formPost = PostForm(request.POST or None)
    if request.method == 'POST' and formPost.is_valid():
        form = formPost.save(commit=False)
        print(formPost)
        other_information = formPost
        title = request.POST['title']
        job_type = request.POST['type']
        location = request.POST['location']
        des = request.POST['des']
        requirement = request.POST['requirement']
        deadline = request.POST['deadline']
        # pid = request.session['pid']
        company_id = company
        # cname = Job_Providers.objects.get(cname=request.session['cname'])
        category = request.POST['category']
        salary = request.POST.get('salary', 'NOT DISCLOSED')

        # create a new instance of Post_Job model with the data
        job_post = Post(
            title=title,
            type=job_type,
            location=location,
            description=des,
            reqirement=requirement,
            company_id=company_id,
            other_information=other_information,
            category=category,
            salary=salary,
            deadline=deadline)
        job_post.save()

        messages.success(request, 'Job posted successfully')
        return redirect('http://127.0.0.1:8000/postedjob')
    else:
        print(formPost.errors)

        # pid = request.session['pid']

        # print(pid)
        # b = Job_Providers.objects.filter(pid=pid)
        # noti = Apply.objects.filter(pid=pid).order_by('-timestamp')[:10]
        context = {
            # 'b': b,
            'b': {},
            'company': company,
            "formPost": formPost
            # 'noti':noti
        }

        return render(request, 'apps/dashboard/postjob.html', context)


# views.py
import pandas as pd

def post_job_excel(request):
    company = Company.objects.get(responsible=request.user.id)
    form = PostForm(request.POST or None, request.FILES or None)  # Inclure les fichiers

    if request.method == 'POST':
        if 'file' in request.FILES:  # Si un fichier a été uploadé
            excel_file = request.FILES['file']
            if not excel_file.name.endswith('.xlsx'):
                messages.error(request, "Veuillez uploader un fichier Excel (.xlsx).")
                return render(request, 'apps/dashboard/post_jobs_file.html', {'form': form})

            try:
                # Lire le fichier Excel
                df = pd.read_excel(excel_file, sheet_name=0)  # Première feuille
                df.dropna(how='all', inplace=True)  # Supprimer les lignes vides

                # Vérifier que les colonnes existent
                required_columns = ['title', 'type', 'location', 'description', 'requirement', 'category', 'salary', 'deadline']
                missing_cols = [col for col in required_columns if col not in df.columns]
                if missing_cols:
                    messages.error(request, f"Colonnes manquantes : {missing_cols}")
                    print(f"Colonnes manquantes : {missing_cols}")
                    return render(request, 'apps/dashboard/post_jobs_file.html', {'form': form})

                # Créer les posts
                created_count = 0
                for _, row in df.iterrows():
                    try:
                        post = Post(
                            title=row['title'],
                            type=row['type'],
                            other_information=row['other_information'],
                            location=row['location'],
                            description=row['description'],
                            requirement=row['requirement'],
                            category=row['category'],
                            salary=row['salary'] if pd.notna(row['salary']) else 'NOT DISCLOSED',
                            deadline=row['deadline'] if pd.notna(row['deadline']) else None,
                            company_id=company,
                        )
                        post.save()
                        created_count += 1
                    except Exception as e:
                        print(f"Erreur lors de la création du post : {e}")

                messages.success(request, f"{created_count} offres créées avec succès !")

            except Exception as e:
                messages.error(request, f"Erreur lors de l'analyse du fichier : {str(e)}")

        # else:
        #     # Cas classique : formulaire rempli manuellement
        #     if form.is_valid():
        #         job_post = form.save(commit=False)
        #         job_post.company_id = company
        #         job_post.save()
        #         messages.success(request, 'Offre publiée avec succès')
        #         return redirect('postedjob')

    return render(request, 'apps/dashboard/post_jobs_file.html', {'form': form})


def postedjobs(request):
    company = Company.objects.get(responsible=request.user.id)
    b = Company.objects.get(responsible=request.user.id)
    # pid = request.session['pid']
    a = Post.objects.filter(company_id=company)
    # b = Job_Providers.objects.filter(pid=pid)
    # noti = Apply.objects.filter(pid=pid).order_by('-timestamp')[:10]
    all = {
        'a': a,
        # 'b': b,
        "company": company,
        # 'noti':noti
    }
    return render(request, 'apps/dashboard/jobproviderhome.html', all)


@login_required(login_url='login_view')
def dashboard_professor(request):
    context = {

    }
    return render(request, "seekera/jobproviderhome.html", context)


# def view_profile(request):


def viewprofile_seeker(request):
    try:
        # sid = request.session['sid']
        # print(sid)

        # b = Job_Seekers.objects.filter(sid=sid)
        # noti = Post_Job.objects.filter(status='Open').order_by('-timestamp')[:3]
        # noti2 = Apply.objects.filter(sid=sid).order_by('-timestamp')[:3]
        context = {
            'b': request.user,
            # 'noti2':noti2,
            # 'noti':noti
        }
        return render(request, 'apps/dashboard/view_profile_seeker.html', context)
    except Exception as e:
        print(e)
        pass
        # return login(request)


def single_job_view_provider(request,reference):
    company = Company.objects.get(responsible=request.user.id)
    b = Company.objects.get(responsible=request.user.id)
    a = Post.objects.filter(reference=reference)
    # b = Job_Providers.objects.filter(pid=pid)
    # noti = Apply.objects.filter(pid=pid).order_by('-timestamp')[:10]
    all = {
        'a': a,
        # 'b': b,
        # 'noti':noti
        "company": company,
    }
    return render(request, 'apps/dashboard/single-provider.html',all)


@login_required(login_url='login_view')
def single_job_view(request, reference):
    id = reference
    """
    Provide the ability to view job details
    """
    # if cache.get(id):
    #     job = cache.get(id)
    # else:
    job = get_object_or_404(Post, reference=id)
    print(job.company_id)
    company = Company.objects.get(id=job.company_id_id)

        # cache.set(id,job , 60 * 15)
    # related_job_list = job.tags.similar_objects()

    # paginator = Paginator(related_job_list, 5)
    page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)

    context = {
        'job': job,
        "company": company,
        # 'page_obj': page_obj,
        # 'total': len(related_job_list)

    }
    return render(request, 'apps/dashboard/job-single.html', context)



def single_post_view(request, reference):
    id = reference
    """
    Provide the ability to view job details
    """
    # if cache.get(id):
    #     job = cache.get(id)
    # else:
    job = get_object_or_404(Post, reference=id)
    print(job.company_id)
    company = Company.objects.get(id=job.company_id_id)

        # cache.set(id,job , 60 * 15)
    # related_job_list = job.tags.similar_objects()

    # paginator = Paginator(related_job_list, 5)
    page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)

    context = {
        'job': job,
        "company": company,
        # 'page_obj': page_obj,
        # 'total': len(related_job_list)

    }
    return render(request, 'apps/dashboard/view_post.html', context)



def extract_job_criteria(question):
    prompt = f"""
    Analyse cette question et extrais les critères. Réponds uniquement en JSON.
    - "metier": mot-clé métier (ex: développement, data, marketing, etc.)
    - "lieu": ville ou région (ex: Lyon, Paris)
    - "type": type de poste (stage, alternance, freelance, etc.)
    - "category": catégorie si mentionnée (ex: informatique, finance)
    - "deadline_before": date limite avant un mois (ex: juin → 2025-06-30)

    Question : "{question}"
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un assistant qui extrait des critères d'offres d'emploi. Réponds uniquement en JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=150
        )
        import json
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print("Erreur OpenAI:", e)
        return {}



@csrf_exempt
def chatbot_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question = data.get('question', '').strip()

        # Extraire les critères via OpenAI
        criteria = extract_job_criteria(question)

        # Filtrer uniquement les offres OUVERTES
        results = Post.objects.filter(status=1)  # status=1 → OPEN

        # Appliquer les filtres extraits
        if criteria.get('metier'):
            results = results.filter(
                Q(title__icontains=criteria['metier']) |
                Q(description__icontains=criteria['metier']) |
                Q(requirement__icontains=criteria['metier'])
            )
        if criteria.get('lieu'):
            results = results.filter(location__icontains=criteria['lieu'])
        if criteria.get('type'):
            results = results.filter(type__icontains=criteria['type'])
        if criteria.get('category'):
            results = results.filter(category__icontains=criteria['category'])
        if criteria.get('deadline_before'):
            # Ex: "avant juin" → filtrer deadline <= 2025-06-30
            # Tu peux améliorer avec une conversion mois → date
            pass  # À implémenter si besoin

        # Générer la réponse
        if results.exists():
            jobs = []
            for job in results[:5]:
                jobs.append(
                    f"🔹 <strong>{job.title}</strong><br>"
                    f"   Entreprise : {job.company_id.name}<br>"
                    f"   Lieu : {job.location} | Type : {job.type}<br>"
                    f"   Réf : {job.reference} | Publié le : {job.start_date}<br>"
                    f"   <a href='/view_post/{job.reference}/'>Voir l'offre</a>"
                )
            response = "Voici les offres correspondantes :\n" + "\n".join(jobs)
        else:
            response = "Aucune offre trouvée. Essayez avec d'autres mots-clés."

        return JsonResponse({'response': response})

    # Message de bienvenue
    return JsonResponse({'response': "Bonjour ! Posez-moi une question sur le stage que vous cherchez."})


def chat_page(request):
    return render(request, 'apps/dashboard/chatbot.html')


def post_list_public(request):
    post_list = Post.objects.filter().order_by('-timestamp')
    paginator = Paginator(post_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {

        'page_obj': page_obj,

    }
    return render(request, 'apps/dashboard/post_list_public.html', context)


def post_list_public_other(request):
    """

    """
    job_list = Job.objects.filter(is_published=True,is_closed=False).order_by('-timestamp')
    paginator = Paginator(job_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {

        'page_obj': page_obj,

    }
    return render(request, 'jobapp/job-list.html', context)


def extract_text_from_pdf(file_path):
    """Extrait le texte d'un PDF avec PyMuPDF"""
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()


def extract_text_from_file(file_path):
    text = ""
    if file_path.lower().endswith('.pdf'):
        pdf = fitz.open(file_path)
        for page in pdf:
            text += page.get_text()
    else:
        import textract
        text = textract.process(file_path).decode("utf-8")
    return text


def parse_with_openai(text):
    """Analyse un CV avec OpenAI et retourne un JSON structuré"""
    prompt = f"""
    Analyse le texte suivant d'un CV et retourne UNIQUEMENT un JSON valide.
    Ne mets pas de texte avant ou après, pas de balises markdown.
    Le JSON doit contenir :
    - nom
    - email
    - téléphone
    - compétences (liste)
    - expériences professionnelles (poste, entreprise, dates, description)
    - formations (diplôme, établissement, dates)
    - langues (liste)

    Texte :
    {text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Tu es un parseur JSON strict, tu ne renvoies que du JSON pur."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    raw_content = response.choices[0].message.content.strip()

    # Supprimer éventuelles balises ```json ... ```
    raw_content = re.sub(r"^```json\s*|\s*```$", "", raw_content, flags=re.MULTILINE)

    try:
        return json.loads(raw_content)
    except json.JSONDecodeError:
        return {
            "erreur": "Impossible de parser la réponse OpenAI",
            "contenu_recu": raw_content
        }


# def upload_resume(request):
#     if request.method == "POST":
#         form = ResumeForm(request.POST, request.FILES)
#         if form.is_valid():
#             resume = form.save()  # Enregistrement du fichier
#
#             # Extraction du texte
#             file_path = resume.uploaded_file.path
#             raw_text = extract_text_from_pdf(file_path)
#
#             # Analyse avec OpenAI
#             extracted_data = parse_with_openai(raw_text)
#
#             # Sauvegarde des données extraites
#             resume.extracted_data = extracted_data
#             resume.save()
#
#             return redirect("resume_detail", pk=resume.pk)
#     else:
#         form = ResumeForm()
#
#     return render(request, 'apps/dashboard/upload_resume.html', {'form': form})


def upload_resume(request):
    extracted_data = None
    error = None

    if request.method == "POST" and request.FILES.get("resume"):
        resume_file = request.FILES["resume"]
        fs = FileSystemStorage()
        file_path = fs.save(resume_file.name, resume_file)
        file_path = fs.path(file_path)

        raw_text = extract_text_from_pdf(file_path)

        prompt = f"""
        Voici le texte brut d'un CV :

        {raw_text}

        Tâche : Extrais uniquement les informations présentes, sans inventer.
        Réponds en JSON strict avec la structure suivante :
        {{
            "nom": "...",
            "email": "...",
            "telephone": "...",
            "competences": ["...", "..."],
            "experiences_professionnelles": [
                {{"poste": "...", "entreprise": "...", "dates": "...", "description": "..."}}
            ],
            "formations": [
                {{"diplome": "...", "ecole": "...", "dates": "..."}}
            ],
            "langues": ["...", "..."]
        }}
        Si une information est manquante, mets null ou [].
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Tu es un assistant qui extrait des données de CV."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )

            content = response.choices[0].message.content

            try:
                extracted_data = json.loads(content)
            except json.JSONDecodeError:
                error = "Impossible de parser la réponse d’OpenAI"
                extracted_data = {"brut": content}

        except Exception as e:
            error = str(e)

    return render(request, "apps/dashboard/upload_resume.html", {
        "extracted_data": extracted_data,
        "error": error
    })


# def upload_resume(request):
#     if request.method == "POST" and request.FILES["resume"]:
#         resume_file = request.FILES["resume"]
#         fs = FileSystemStorage()
#         file_path = fs.save(resume_file.name, resume_file)
#         file_path = fs.path(file_path)
#
#         # Extraction du texte brut
#         raw_text = extract_text_from_pdf(file_path)
#
#         # Prompt structuré
#         prompt = f"""
#         Voici le texte brut d'un CV :
#
#         {raw_text}
#
#         Tâche : Extrais uniquement les informations présentes, sans inventer.
#         Réponds en JSON strict avec la structure suivante :
#         {{
#             "nom": "...",
#             "email": "...",
#             "telephone": "...",
#             "competences": ["...", "..."],
#             "experiences_professionnelles": [
#                 {{"poste": "...", "entreprise": "...", "dates": "...", "description": "..."}}
#             ],
#             "formations": [
#                 {{"diplome": "...", "ecole": "...", "dates": "..."}}
#             ],
#             "langues": ["...", "..."]
#         }}
#         Si une information est manquante, mets null ou [].
#         """
#
#         try:
#             response = openai.ChatCompletion.create(
#                 model="gpt-4o-mini",
#                 messages=[
#                     {"role": "system", "content": "Tu es un assistant qui extrait des données de CV."},
#                     {"role": "user", "content": prompt}
#                 ],
#                 temperature=0
#             )
#
#             content = response.choices[0].message["content"]
#
#             try:
#                 extracted_data = json.loads(content)
#             except json.JSONDecodeError:
#                 extracted_data = {"error": "Impossible de parser la réponse d’OpenAI", "brut": content}
#
#         except Exception as e:
#             extracted_data = {"error": str(e)}
#
#         return render(request, "apps/dashboard/resume_detail.html", {"extracted_data": extracted_data})
#
#     return render(request, "apps/dashboard/upload_resume.html")

# def resume_detail(request, pk):
#     resume = get_object_or_404(Resume, pk=pk)
#
#     extracted_items = []
#     for key, value in resume.extracted_data.items():
#         if isinstance(value, list):
#             processed_list = []
#             for sub in value:
#                 if isinstance(sub, (dict, list)):
#                     sub_type = "complex"
#                 else:
#                     sub_type = "string"
#                 processed_list.append({"type": sub_type, "value": sub})
#             extracted_items.append({"key": key, "type": "list", "value": processed_list})
#
#         elif isinstance(value, dict):
#             extracted_items.append({"key": key, "type": "dict", "value": value})
#
#         else:
#             extracted_items.append({"key": key, "type": "string", "value": value})
#
#     return render(request, 'apps/dashboard/resume_detail.html', {
#         'resume': resume,
#         'extracted_items': extracted_items
#     })


def resume_detail(request, pk):
    resume = get_object_or_404(Resume, pk=pk)

    # 1️⃣ Extraction brute
    file_path = resume.uploaded_file.path
    raw_text = extract_text_from_pdf(file_path)

    # 2️⃣ Analyse OpenAI
    extracted_data = parse_with_openai(raw_text)

    return render(request, "apps/dashboard/resume_detail.html", {
        "resume": resume,
        "extracted_data": extracted_data
    })


