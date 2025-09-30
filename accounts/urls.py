from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import SignupView, ProfileUpdateView, LoginView

# 認証まわりの URL をまとめる。`app_name` で名前空間を付けて衝突を防ぐ
app_name = 'accounts'

urlpatterns = [
    # ログインページ（Django の LoginView をカスタムフォーム付きで利用）
    path('login/', LoginView.as_view(), name='login'),
    # ログアウトは Django が用意する汎用ビューをそのまま使用
    path('logout/', LogoutView.as_view(), name='logout'),
    # 会員登録フォーム
    path('signup/', SignupView.as_view(), name='signup'),
    # プロフィール（ユーザー名＋パスワード変更）ページ
    path('profile/', ProfileUpdateView.as_view(), name='profile-edit'),
]
