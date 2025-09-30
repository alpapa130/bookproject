"""book アプリのビュー層。書籍・レビューに関する画面処理をまとめている。"""

from django.shortcuts import render, redirect  # HTML の描画や別ページへの遷移に使用
from django.urls import reverse, reverse_lazy  # URL 名から実際のパスを逆引きするユーティリティ
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView  # 汎用的なCBV
from django.contrib.auth.mixins import LoginRequiredMixin  # ログインしていないユーザーをログインページへ誘導
from django.core.exceptions import PermissionDenied  # 権限のない操作を検出したときに 403 を返すための例外
from django.core.paginator import Paginator  # 一覧データをページ分割するクラス
from django.contrib import messages  # フラッシュメッセージ（画面上部に一時的に表示する通知）
from django.http import Http404  # 対象データが見つからなかった場合に 404 を返すための例外
from django.db.models import Avg, Q, Count  # 集計(Avg/Count)や柔軟な検索条件(Q)に使うヘルパー

from .models import Book, Review
from .forms import ReviewForm, BookForm
from .consts import ITEM_PER_PAGE


class ListBookView(LoginRequiredMixin, ListView):
    """書籍一覧ページ。検索キーワードやカテゴリで絞り込みできる。"""

    template_name = 'book/book_list.html'
    model = Book
    paginate_by = None  # ページングはテンプレート側で制御する

    def get_queryset(self):
        """クエリパラメーターを見て、検索条件を適用した本の一覧を返す。"""

        # 最新の投稿が先に表示されるよう、新しいID順で取得
        qs = super().get_queryset().order_by('-id')

        # `q` パラメーターがあればタイトル／本文／カテゴリの部分一致で検索
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(title__icontains=q) | Q(text__icontains=q) | Q(category__icontains=q)
            )

        # `cat` パラメーターがあればカテゴリで絞り込み
        cat = self.request.GET.get('cat', '').strip()
        if cat:
            qs = qs.filter(category=cat)

        return qs

    def get_context_data(self, **kwargs):
        """テンプレートで必要となる補足情報を詰め込んで返す。"""

        ctx = super().get_context_data(**kwargs)

        # DBに登録されているカテゴリを列挙し、テンプレートでタグ表示できるよう整形
        raw_categories = (
            Book.objects.exclude(category='')
            .values_list('category', flat=True)
            .distinct()[:20]
        )
        category_labels = dict(Book._meta.get_field('category').choices)
        ctx['categories'] = [
            {
                'value': value,
                'label': category_labels.get(value, value),
            }
            for value in raw_categories
        ]

        # 検索フォームに入力した値をそのまま戻すため、現在の条件を渡す
        ctx['current_query'] = self.request.GET.get('q', '').strip()
        ctx['current_category'] = self.request.GET.get('cat', '').strip()
        ctx['category_labels'] = category_labels
        ctx['current_category_label'] = category_labels.get(ctx['current_category'], '')

        # テンプレートで冊数を表示できるよう、件数も渡す
        ctx['total_books'] = ctx['object_list'].count()
        return ctx


class DetailBookView(LoginRequiredMixin, DetailView):
    """書籍の詳細ページ。レビュー一覧も同時に描画する。"""

    template_name = 'book/book_detail.html'
    model = Book

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # book -> review が 1:N でつながっているので関連レビューを取得
        ctx['reviews'] = (
            self.object.review_set.select_related('user').order_by('-id')
        )
        # テンプレートで「編集／削除ボタンを表示して良いか」を判定するフラグ
        ctx['is_owner'] = self.object.user == self.request.user
        return ctx


class CreateBookView(LoginRequiredMixin, CreateView):
    """書籍の新規登録フォーム。"""

    template_name = 'book/book_create.html'
    model = Book
    form_class = BookForm
    success_url = reverse_lazy('book:list-book')

    def form_valid(self, form):
        # 投稿者はフォームに表示していないので、ログインユーザーを自動でセット
        form.instance.user = self.request.user
        return super().form_valid(form)


class DeleteBookView(LoginRequiredMixin, DeleteView):
    """書籍削除の確認画面。投稿者本人だけが実行できる。"""

    template_name = 'book/book_confirm_delete.html'
    model = Book
    success_url = reverse_lazy('book:list-book')

    def dispatch(self, request, *args, **kwargs):
        # 既に削除済みのURLへ戻ってきた場合、一覧へ案内してエラー画面を避ける
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            messages.info(request, '指定された書籍は既に削除されています。')
            return redirect('book:list-book')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # 投稿者本人以外が削除しようとした場合は 403 を返す
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj


class UpdateBookView(LoginRequiredMixin, UpdateView):
    """書籍編集フォーム。投稿者本人のみ編集可能。"""

    model = Book
    form_class = BookForm
    template_name = 'book/book_update.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # 編集も投稿者本人に限定
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj

    def get_success_url(self):
        # 編集完了後は詳細ページに戻す
        return reverse('book:detail-book', kwargs={'pk': self.object.id})


def index_view(request):
    """トップページ。新着書籍とレビュー評価ランキングを表示する。"""

    q = request.GET.get('q', '').strip()
    selected_category = request.GET.get('cat', '').strip()

    # 新着一覧（検索条件を適用）
    books = Book.objects.order_by('-id')
    if q:
        books = books.filter(
            Q(title__icontains=q) | Q(text__icontains=q) | Q(category__icontains=q)
        )
    if selected_category:
        books = books.filter(category=selected_category)

    # ランキング用に平均点とレビュー数を計算。レビューが1件以上あるものだけ残す
    ranking_books = (
        books.annotate(
            avg_rating=Avg('review__rate'),  # 平均評価を SQL の集計で計算
            review_count=Count('review'),  # レビュー件数も同時に取得
        )
        .filter(review_count__gt=0)  # レビューが 0 件の書籍はランキングから除外
        .order_by('-avg_rating')  # 平均評価の高い順に並べ替え
    )

    # ランキングは ITEM_PER_PAGE 件ずつページングする
    paginator = Paginator(ranking_books, ITEM_PER_PAGE)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # カテゴリ一覧を描画用に整形
    categories = (
        Book.objects.exclude(category='')
        .values_list('category', flat=True)
        .distinct()
    )
    category_labels = dict(Book._meta.get_field('category').choices)
    current_category_label = category_labels.get(selected_category, '')
    category_list = [
        {
            'value': value,
            'label': category_labels.get(value, value),
        }
        for value in categories
    ]

    return render(
        request,
        'book/index.html',
        {
            'object_list': books,
            'ranking_list': page_obj.object_list,
            'page_obj': page_obj,
            'categories': category_list,
            'current_query': q,
            'current_category': selected_category,
            'category_labels': category_labels,
            'current_category_label': current_category_label,
        },
    )


class CreateReviewView(LoginRequiredMixin, CreateView):
    """レビュー新規作成フォーム。URL の book_id から紐付け先を決める。"""

    model = Review
    form_class = ReviewForm
    template_name = 'book/review_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # URL パラメーター `book_id` で対象書籍を取得し、テンプレートに渡す
        book = Book.objects.get(pk=self.kwargs['book_id'])
        ctx['book'] = book
        ctx['mode'] = 'create'
        return ctx

    def form_valid(self, form):
        # 投稿者と対象書籍はフォームに表示していないのでビュー側でセットする
        form.instance.user = self.request.user
        form.instance.book = Book.objects.get(pk=self.kwargs['book_id'])
        return super().form_valid(form)

    def get_success_url(self):
        # 登録後は対象書籍の詳細ページへ戻る
        return reverse('book:detail-book', kwargs={'pk': self.object.book.id})


class ReviewUpdateView(LoginRequiredMixin, UpdateView):
    """レビュー編集フォーム。投稿者本人だけが利用できる。"""

    model = Review
    form_class = ReviewForm
    template_name = 'book/review_form.html'

    def get_object(self, queryset=None):
        review = super().get_object(queryset)
        if review.user != self.request.user:
            raise PermissionDenied
        return review

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['book'] = self.object.book  # テンプレートで書籍情報を表示するために渡す
        ctx['mode'] = 'update'  # 同じテンプレートを新規／編集で使い回すフラグ
        return ctx

    def get_success_url(self):
        return reverse('book:detail-book', kwargs={'pk': self.object.book.id})


class ReviewDeleteView(LoginRequiredMixin, DeleteView):
    """レビュー削除確認ページ。投稿者本人のみ削除できる。"""

    model = Review
    template_name = 'book/review_confirm_delete.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            messages.info(request, '指定されたレビューは既に削除されています。')
            return redirect('book:list-book')

    def get_object(self, queryset=None):
        review = super().get_object(queryset)
        if review.user != self.request.user:
            raise PermissionDenied
        return review

    def get_success_url(self):
        # 削除後は対象書籍の詳細へ戻る
        return reverse('book:detail-book', kwargs={'pk': self.object.book.id})
