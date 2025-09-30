from django.urls import path

from . import views

# URL 名前空間。テンプレートで `{% url 'book:...' %}` と書けるようにする設定
app_name = "book"

urlpatterns = [
    # トップページ（新着・ランキング表示）。関数ビューを直接指定
    path('', views.index_view, name='index'),
    # 書籍一覧ページ。Class-Based View は `as_view()` を通して登録する
    path('book/', views.ListBookView.as_view(), name='list-book'),
    # 書籍詳細ページ。URL 中の `<int:pk>` は対象書籍のIDを指す
    path('book/<int:pk>/detail/', views.DetailBookView.as_view(), name='detail-book'),
    # 書籍の新規登録フォーム
    path('book/create/', views.CreateBookView.as_view(), name='create-book'),
    # 書籍削除確認ページ（投稿者本人のみアクセス可能）
    path('book/<int:pk>/delete/', views.DeleteBookView.as_view(), name='delete-book'),
    # 書籍編集フォーム
    path('book/<int:pk>/update/', views.UpdateBookView.as_view(), name='update-book'),
    # 書籍に紐づくレビュー投稿フォーム。URL の `<int:book_id>` で対象書籍を指定
    path('book/<int:book_id>/review/', views.CreateReviewView.as_view(), name='review'),
    # レビュー編集フォーム
    path('review/<int:pk>/edit/', views.ReviewUpdateView.as_view(), name='review-edit'),
    # レビュー削除確認ページ
    path('review/<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='review-delete'),
]
