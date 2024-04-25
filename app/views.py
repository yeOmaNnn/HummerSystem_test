import random
import string
from time import sleep

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from app.serializer import UserSerializer, RefUserSerializer
from .forms import PhoneForm, CodeForm
from .models import User, RefUser
import phonenumbers


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PhoneLoginView(APIView):
    def post(self, request: Request):
        phone = request.data.get("phone")
        if not phone:
            return Response({"error": "not phone number"}, status=400)
        if not self.is_valid_phone_number(phone):
            return Response({"error": "not valid number"}, status=400)
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
        user, created = User.objects.get_or_create(phone=phone)
        request.session['phone_number'] = phone
        request.session['code'] = code
        sleep(2)
        return Response({"message": "Correct number, put invite code: ", "debug_code": code}, status=200)
    def is_valid_phone_number(self, phone_number):
        try:
            parsed_number = phonenumbers.parse(phone_number, None)
            return phonenumbers.is_valid_number(parsed_number)
        except phonenumbers.phonenumberutil.NumberParseException:
            return False


class CodeLoginView(APIView):
    def post(self, request: Request):
        phone = request.session.get("phone_number")
        code = request.session.get("code")
        print(code)
        print(phone)
        input_code = request.data.get("code")
        if not phone:
            return Response({"error": "not phone number"}, status=400)
        if not code:
            return Response({"error": "wrong login code"}, status=400)
        if code != input_code:
            return Response({"error": "wrong login code"}, status=400)
        user, created = User.objects.get_or_create(phone=phone)
        authenticated_user = authenticate(username=phone, password="1234")
        print(authenticated_user)
        if authenticated_user:
            login(request, authenticated_user)
        return Response({"message": "Success login"}, status=200)


class ProfileView(APIView):
    def get(self, request):
        user = request.user
        if not user:
            return Response({"error": "not auth"}, status=401)
        profile = UserSerializer(user, many=False)
        return Response(profile.data, status=200)

    def post(self, request):
        user = request.user
        if not user:
            return Response({"error": "not auth"}, status=401)
        invite_code = request.data.get("invite_code")
        is_invate = True if RefUser.objects.filter(who_user_id=user).exists() else False
        if is_invate:
            return Response({"error": "you already invited"}, status=400)
        if not invite_code:
            return Response({"error": "not invite code"}, status=400)
        if invite_code == user.invite_code:
            return Response({"error": "can`t invite yourself"}, status=400)
        try:
            user_ref = User.objects.get(invite_code=invite_code)
        except User.DoesNotExist:
            return Response({"error": "not found user with invite code"}, status=400)
        ref_user = RefUser(user_id=user_ref, who_user_id=user)
        ref_user.save()
        return Response({"message": "success invite"}, status=200)

def phone_form_view(request):
    if request.method == 'POST':
        form = PhoneForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            code = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
            user, created = User.objects.get_or_create(phone=phone_number)
            request.session['phone_number'] = phone_number
            request.session['code'] = code
            return redirect('code_form_view')
    else:
        form = PhoneForm()
    return render(request, 'phone_form.html', {'form': form})





def code_form_view(request):
    if 'phone_number' in request.session and 'code' in request.session:
        phone_number = request.session['phone_number']
        code_generate = request.session['code']
        if request.method == 'POST':
            form = CodeForm(request.POST)
            if form.is_valid():
                code = form.cleaned_data['code']
                user = User.objects.filter(phone=phone_number).first()
                if code_generate == code:
                    authenticated_user = authenticate(username=phone_number, password="1234")
                    if authenticated_user:
                        login(request, authenticated_user)
                        return redirect('profile')
                else:
                    error_message = "Неверный код. Попробуйте еще раз."
                    return render(request, 'code_form.html',
                                  {'form': form, 'code': request.session['code'], 'error_message': error_message})
        else:
            form = CodeForm()
        return render(request, 'code_form.html', {'form': form, 'code': request.session['code']})
    else:
        return redirect('phone_form')


@login_required
def profile(request):
    user = request.user
    is_invate = True if RefUser.objects.filter(who_user_id=user).exists() else False
    users_refs = [ref.who_user_id for ref in RefUser.objects.filter(user_id=user)]
    if request.method == 'POST':
        invite_code = request.POST.get('invite_code')
        if is_invate:
            return render(request, 'profile.html',
                          {"is_invate": is_invate, "users_refs": users_refs, "error_message": "Вы уже были приглашены"})
        if invite_code == user.invite_code:
            return render(request, 'profile.html', {"is_invate": is_invate, "users_refs": users_refs,
                                                    "error_message": "Вы не можете пригласить сами себя"})
        try:
            user_ref = User.objects.get(invite_code=invite_code)
        except User.DoesNotExist:
            return render(request, 'profile.html',
                          {"is_invate": is_invate, "users_refs": users_refs, "error_message": "Пользователь не найден"})
        ref_user = RefUser(user_id=user_ref, who_user_id=user)
        ref_user.save()
        return render(request, 'profile.html', {"is_invate": True, "users_refs": users_refs})
    return render(request, 'profile.html', {"is_invate": is_invate, "users_refs": users_refs})



