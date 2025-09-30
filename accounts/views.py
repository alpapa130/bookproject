from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView as AuthLoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import SignupForm, UserCredentialUpdateForm, LoginForm


class SignupView(CreateView):
    """新規ユーザー登録ビュー。"""

    model = User
    form_class = SignupForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('book:index')


class LoginView(AuthLoginView):
    """ログインビュー。カスタムフォームを差し込む。"""

    authentication_form = LoginForm
    template_name = 'registration/login.html'


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """会員情報編集ビュー。ログインユーザー自身のみ編集可能。"""

    model = User
    form_class = UserCredentialUpdateForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile-edit')

    def get_object(self):
        # 常にログインユーザー本人のみを編集対象にする
        return self.request.user

    def get_form_kwargs(self):
        # フォームでパスワード検証に使用するため user を渡す
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # パスワード変更後もログイン状態を維持する
        response = super().form_valid(form)
        update_session_auth_hash(self.request, self.object)
        return response
