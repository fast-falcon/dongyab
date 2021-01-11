from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from .models import *
# Create your views here.
from django.urls import reverse
from django.db.models import Sum, F

from account.forms import RegisterForm, LoginForm


def first_page(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("home"))
    return HttpResponseRedirect(reverse("signin"))


def sign(request):
    if request.method == "GET":
        return render(request, 'sign.html', {"error": ""})
    else:
        if "register" in request.POST:
            form = RegisterForm(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse("sign"))
            else:
                return render(request, 'sign.html', {"error": form.errors})
        elif "login" in request.POST:
            form = LoginForm(request.POST)
            if form.is_valid():
                user = User.objects.filter(username=form.cleaned_data["username"]).first()
                if user:
                    valid = user.check_password(form.cleaned_data["password"])
                else:
                    valid = False
                if valid:
                    login(request, user)
                    return HttpResponseRedirect(reverse("home"))
                else:
                    return render(request, 'sign.html', {"error": "نام کاربری یا رمز عبور اشتباه است"})
            return render(request, 'sign.html', {"error": form.errors})

    return HttpResponse()


def add_balance(request):
    profile = request.user.profile
    profile.wallet += int(request.GET.get("price", 0))
    profile.save()
    return HttpResponseRedirect(reverse("home"))


@login_required(login_url="sign")
def home(request, uuid=None):
    user_group_factors = []
    user_groups = request.user.group_members.all()
    users = []
    this_group = None
    if user_groups:
        if not uuid:
            uuid = user_groups.first().uuid
        this_group = Group.objects.get(uuid=uuid)
        user_group_factors = Factor.objects.filter(factor_owner=request.user, factor_group__uuid=uuid)
        users = User.objects.filter(factor_group=this_group)

    for user in users:
        talab = Factor.objects.filter(factor_owner=user, factor_group=this_group).aggregate(Sum('price')).get(
            "price__sum", 0)
        bedehi = Factor.objects.filter(factor_members=user, factor_group=this_group).aggregate(
            Sum('price') / F('divided_price')).get(
            "price__sum", 0)
        setattr(user, "talab_me", talab - bedehi)
        talab = Factor.objects.filter(factor_owner=request.user, factor_group=this_group).aggregate(Sum('price')).get(
            "price__sum", 0)
        bedehi = Factor.objects.filter(factor_members=request.user, factor_group=this_group).aggregate(
            Sum('price') / F('divided_price')).get(
            "price__sum", 0)
        setattr(user, "talab", talab - bedehi)

    contex = {
        "groups": user_groups,
        "user_factors": user_group_factors,
        "users": users,
        "group": this_group
    }
    return render(request, 'index.html', contex)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("sign"))
