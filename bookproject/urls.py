"""
URL configuration for bookproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # 管理サイト。運営者向け UI を `/admin/` で提供する
    path('admin/', admin.site.urls),
    # 認証関連 URL を accounts アプリに委譲（ログイン・ログアウト・会員登録など）
    path('accounts/', include('accounts.urls')),
    # 書籍アプリのルーティングをプロジェクト配下のトップパスに割り当てる
    path('', include('book.urls')),
]

# 画像アップロード（MEDIA）を開発環境で配信できるよう、static() を利用して URL を追加
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
