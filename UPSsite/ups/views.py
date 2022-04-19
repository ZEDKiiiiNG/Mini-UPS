from django.shortcuts import render
from . import models
# Create your views here.
from django.shortcuts import render,redirect
from .forms import UserForm, RegisterForm, ChangeDestinationForm, SearchPackageForm
def index(request):
    serachForm = SearchPackageForm()
    if request.method == "POST" and request.POST:
        if 'Search' in request.POST:
            serachForm = SearchPackageForm(request.POST)
            if serachForm.is_valid():
                searchId = serachForm.cleaned_data['pkgId']
                searchList = models.Package.objects.filter(pkgId=searchId)
                if len(searchList) == 0:
                    message = "No matched package found！"
    if request.session.get('is_login', None):
        username = request.session.get('user_name', None)
        user = models.User.objects.get(name=username)
        pkgs_list = models.Package.objects.filter(user = user)
        change_form = ChangeDestinationForm()
        if request.method == "POST" and request.POST:
            if 'Change' in request.POST:
                change_form = ChangeDestinationForm(request.POST)
                # message = "Please check the content！"
                if change_form.is_valid():  # get the detaile data
                    newDestX = change_form.cleaned_data['newDestX']
                    newDestY = change_form.cleaned_data['newDestY']
                    change_id = request.POST.get('Change')
                    pkg_item = models.Package.objects.get(pkgId=change_id)
                    pkg_item.destX = newDestX
                    pkg_item.destY = newDestY
                    pkg_item.save()

    return render(request,'login/index.html',locals())


def login(request):
    # if already logged in redirect
    if request.session.get('is_login', None):
        return redirect("/index/")

    if request.method == "POST":
        login_form = UserForm(request.POST)
        message = "please check the content！"
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = models.User.objects.get(name=username)
                if user.password == password:
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    return redirect('/index/')
                else:
                    message = "password incorrect！"
            except:
                message = "user does not exist！"
        return render(request, 'login/login.html', locals())
    else:
        login_form = UserForm()
        return render(request, 'login/login.html', locals())

def register(request):
    if request.session.get('is_login', None):
        # if already signed in, then cannot register
        return redirect("/index/")
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        message = "Please check the content！"
        if register_form.is_valid():  # get the detaile data
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            if password1 != password2:  # pass word are not the same
                message = "The passwords are not the same！"
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user:  # found the same user name
                    message = 'user already exists！'
                    return render(request, 'login/register.html', locals())
                same_email_user = models.User.objects.filter(email=email)
                if same_email_user:  #  found the same email
                    message = 'email already exits！'
                    return render(request, 'login/register.html', locals())

                # all rules passed

                new_user = models.User.objects.create()
                new_user.name = username
                new_user.password = password1
                new_user.email = email
                new_user.save()
                return redirect('/login/')  # return to login page
    register_form = RegisterForm()
    return render(request, 'login/register.html', locals())

# log out in login page
def logout(request):
    if not request.session.get('is_login', None):

        return redirect('/login/')
    request.session.flush()

    return redirect('/login/')
def search(request):
    if not request.session.get('is_login', None):
        message = "Please log in first！"

        return render(request, 'login/login.html', locals())
    username = request.session.get('user_name', None)
    user = models.User.objects.get(name=username)
