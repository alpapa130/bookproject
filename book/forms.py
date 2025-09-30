from django import forms

from .models import Review, Book


class BookImageInput(forms.ClearableFileInput):
    """書籍サムネイル用入力。ラベルを日本語化し表示テキストを調整する。"""

    clear_checkbox_label = "削除"
    template_name = "book/widgets/book_clearable_file_input.html"


class ReviewForm(forms.ModelForm):
    """レビュー投稿・編集共通フォーム。タイトル/本文/評価のみ入力させる"""

    class Meta:
        model = Review
        fields = ("title", "text", "rate")
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "レビュータイトル",
            }),
            "text": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "読み終えた感想を入力してください",
            }),
            "rate": forms.Select(attrs={
                "class": "form-control",
            }),
        }
        labels = {
            "title": "タイトル",
            "text": "本文",
            "rate": "星の数",
        }


class BookForm(forms.ModelForm):
    """書籍の登録・更新フォーム。日本語ラベルやプレースホルダーを設定する。"""

    class Meta:
        model = Book
        fields = ("title", "text", "category", "thumbnail")
        labels = {
            "title": "書籍タイトル",
            "text": "紹介文",
            "category": "カテゴリ",
            "thumbnail": "サムネイル画像",
        }
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "例）達人に学ぶSQL徹底指南書",
                }
            ),
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "書籍の概要やおすすめポイントを記入してください",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "thumbnail": BookImageInput(
                attrs={
                    "class": "form-control",
                }
            ),
        }
