from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from .models import *
# Create your views here.
from django.urls import reverse
from django.db.models import Sum,F

from account.forms import RegisterForm, LoginForm


def sign(request):
    if request.method == "GET":
        return render(request, 'sign.html', {"error": ""})
    else:
        if "register" in request.POST:
            form = RegisterForm(request.POST)
            if form.is_valid():
                form.save()
        elif "login" in request.POST:
            form = LoginForm(request.POST)
            if form.is_valid():
                user = User.objects.filter(email=form.cleaned_data["email"]).first()
                if user:
                    valid = user.check_password(form.cleaned_data["password"])
                else:
                    valid = False
                if valid:
                    login(request, user)
                    return HttpResponseRedirect(reverse("home"))
            return render(request, 'sign.html', {"error": "ایمیل یا پسورد اشتباه می باشد."})

    return HttpResponse()


@login_required(login_url="sign")
def home(request, uuid):
    user_groups = request.user.group_members.all()
    user_group_factors = Factor.objects.filter(factor_owner=request.user, factor_group__uuid=uuid)
    this_group = Group.objects.get(uuid=uuid)

    users = User.objects.filter(factor_group=this_group)

    for user in users:
        talab = Factor.objects.filter(factor_owner=user, factor_group=this_group).aggregate(Sum('price')).get(
            "price__sum", 0)
        bedehi = Factor.objects.filter(factor_members=user, factor_group=this_group).aggregate(Sum('price')/F('divided_price')).get(
            "price__sum", 0)
        setattr(user, "talab_me", talab-bedehi)
        talab = Factor.objects.filter(factor_owner=request.user, factor_group=this_group).aggregate(Sum('price')).get(
            "price__sum", 0)
        bedehi = Factor.objects.filter(factor_members=request.user, factor_group=this_group).aggregate(Sum('price')/F('divided_price')).get(
            "price__sum", 0)
        setattr(user, "talab", talab-bedehi)

    contex = {
        "groups": user_groups,
        "user_factors": user_group_factors,
        "users": users,
        "group":this_group
    }
    return render(request, 'index.html', contex)


def send_email(request):
    if request.method == "POST":
        pass
