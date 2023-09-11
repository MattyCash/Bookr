from django import forms

from .models import Publisher, Comment, Post


class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = "__all__"


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ["date_edited", "post"]


class SearchForm(forms.Form):
    search = forms.CharField(required=False, min_length=3)
    search_in = forms.ChoiceField(required=False,
                                  choices=(
                                      ("tag", "Tag"),
                                      ("contributor", "User")
                                  ))

    def clean_search_in(self):
        return self.cleaned_data["search_in"] or "title"


class PostMediaForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["cover"]