from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class SignupForm(UserCreationForm):
    """ユーザー登録フォーム。ラベルと入力欄の見た目を整える。"""

    class Meta:
        model = User
        fields = ("username",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field_labels = {
            "username": "ユーザーID",
            "password1": "パスワード",
            "password2": "パスワード（確認）",
        }
        autocomplete_map = {
            "username": "username",
            "password1": "new-password",
            "password2": "new-password",
        }
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "form-control")
            field.widget.attrs.setdefault("autocomplete", autocomplete_map.get(name, "off"))
            if name in field_labels:
                field.label = field_labels[name]
            field.help_text = ""


class UserCredentialUpdateForm(forms.ModelForm):
    # ユーザー名とパスワードをまとめて更新するフォーム。

    current_password = forms.CharField(
        label="現在のパスワード",
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "current-password"}),
    )
    new_password1 = forms.CharField(
        label="新しいパスワード",
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}),
    )
    new_password2 = forms.CharField(
        label="新しいパスワード（確認）",
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ("username",)
        labels = {
            "username": "ユーザー名",
        }
        help_texts = {"username": ""}
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        # ビューから渡されたログインユーザーを保持して検証に利用
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user is None:
            raise ValueError("UserCredentialUpdateForm requires a user instance")

    def clean_current_password(self):
        current_password = self.cleaned_data.get("current_password")
        if not self.user.check_password(current_password):
            raise forms.ValidationError("現在のパスワードが正しくありません。")
        return current_password

    def clean(self):
        cleaned = super().clean()
        password1 = cleaned.get("new_password1")
        password2 = cleaned.get("new_password2")
        if not password1:
            self.add_error("new_password1", "新しいパスワードを入力してください。")
        if password1 and password2 and password1 != password2:
            self.add_error("new_password2", "新しいパスワードが一致しません。")
        if password1:
            try:
                password_validation.validate_password(password1, self.user)
            except forms.ValidationError as error:
                self.add_error("new_password1", error)
        return cleaned

    def save(self, commit=True):
        # ModelForm の save を利用しつつパスワードのハッシュ化を行う
        user = super().save(commit=False)
        new_password = self.cleaned_data["new_password1"]
        if new_password:
            user.set_password(new_password)
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """ログインフォーム。日本語メッセージと入力欄のスタイルを設定。"""

    error_messages = {
        "invalid_login": "ユーザーIDまたはパスワードが正しくありません。",
        "inactive": "このアカウントは現在利用できません。",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'ユーザーID'
        self.fields['password'].label = 'パスワード'
        self.fields['username'].widget.attrs.setdefault('class', 'form-control')
        self.fields['username'].widget.attrs.setdefault('autocomplete', 'username')
        self.fields['password'].widget.attrs.setdefault('class', 'form-control')
        self.fields['password'].widget.attrs.setdefault('autocomplete', 'current-password')
