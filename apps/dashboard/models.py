from django.db import models
from apps.account.models import CustomUser
import random, string, datetime
from ckeditor.fields import RichTextField

class Company(models.Model):
    responsible = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    name = models.CharField('Company', max_length=50)
    slogan = models.CharField('Company Slogan', max_length=100, default="")
    description = models.CharField('Company Description', max_length=500, default="")
    phone = models.IntegerField('Company Phone Number')
    website = models.CharField('Company Website', max_length=100, default="")
    employee_number = models.IntegerField('No Of Employees', default=1)
    started = models.DateField('Started Rate', default=datetime.date.today)
    photo = models.ImageField('Company Image in jpg/png Format', upload_to='company/')
    license = models.FileField('Company Licence in pdf Format', upload_to='license/')

    def __str__(self):
        return self.name

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('view_license/<int:provider_id>/', self.admin_site.admin_view(self.view_license), name='view_license'),
        ]
        return my_urls + urls

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = "Companies/"


def generer_reference():
    """Génère une référence aléatoire du type POST-ABC123"""
    prefixe = "POST"
    caracteres = string.ascii_uppercase + string.digits
    code = ''.join(random.choices(caracteres, k=6))
    return f"{prefixe}-{code}"


class Post(models.Model):
    prefixe = "POST"
    STATUS_CHOICES = (
        (0, "DRAFT"),
        (1, "OPEN"),
        (2, "EXPIRED"),
        (3, "ARCHIVED"),
    )

    title=models.CharField('Job Title',max_length=75, default="")
    type=models.CharField('Job Type',max_length=60, default="")
    location=models.CharField('Job Location',max_length=50, default="")
    description=models.CharField('Job Description',max_length=500, default="")
    # description = ()
    requirement=models.CharField('Job Requirements',max_length=300, default="")
    reference = models.CharField(max_length=15, unique=True, blank=True, null=True)
    # Company Information
    company_id = models.ForeignKey(Company,on_delete=models.DO_NOTHING)
    # cname = models.ForeignKey(Job_Providers,on_delete=models.CASCADE)
    start_date = models.DateField(auto_now=True)
    application_deadline = models.DateField(auto_now=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, blank=True, null=True, default=1)
    category=models.CharField(max_length=25,default='Not Selected')
    timestamp = models.DateTimeField(auto_now=True)
    salary=models.TextField('Salary Package',default='NOT DISCLOSED')
    deadline=models.DateField(null=True,blank=True)
    other_information = RichTextField(blank=True, null=True, default="<p>Lorem ipsum sit ...</p>")
    # other_information = models.TextField(
    #     verbose_name="Other informations",
    #     help_text="Additional details (special conditions, benefits, recruitment process, etc.)",
    #     blank=True,  # Permet de laisser vide
    #     null=True,  # Valeur NULL autorisée en base
    #     default=None  # Facultatif
    # )

    @property
    def get_status(self):
        status = ""
        if self.status == 1:
            status = 'OPEN'
        if self.status == 2:
            status = "EXPIRED"
        if self.status == 3:
            status = "ARCHIVED"
        if self.status == 0:
            status = "DRAFT"
        return status


    def __str__(self):
        return f"{self.title} By {self.company_id}"


    def save(self, *args, **kwargs):
        if not self.reference:  # On ne génère la référence que si elle n'existe pas
            self.reference = generer_reference()
            # Vérifier que la référence est bien unique (au cas où)
            while Post.objects.filter(reference=self.reference).exists():
                self.reference = generer_reference()
        super().save(*args, **kwargs)


    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = "Posts"



class Resume(models.Model):
    uploaded_file = models.FileField(upload_to='resumes/')
    extracted_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"CV #{self.pk}"


