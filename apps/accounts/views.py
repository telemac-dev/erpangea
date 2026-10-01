from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from .forms import UserAuthenticationForm, UserProfileForm

class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = UserAuthenticationForm
    redirect_authenticated_user = True

class UserLogoutView(LogoutView):
    next_page = 'accounts:login'

class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        profile = getattr(request.user, 'profile', None)
        form = UserProfileForm(instance=profile)
        return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})

    def post(self, request):
        profile = getattr(request.user, 'profile', None)
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado com sucesso!")
            return redirect('accounts:profile')
        return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})
