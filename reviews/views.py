from io import BytesIO

from PIL import Image
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.images import ImageFile
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .forms import PublisherForm, SearchForm, CommentForm, PostMediaForm
from .models import Post, Contributor, Publisher, Comment
from .utils import average_rating
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

def get_user_by_username(username):
    try:
        user = User.objects.get(username=username)
        return user
    except ObjectDoesNotExist:
        return None

def index(request):
    return render(request, "base.html")


def post_search(request):
    search_text = request.GET.get("search", "")
    search_history = request.session.get('search_history', [])
    form = SearchForm(request.GET)
    posts = set()
    if form.is_valid() and form.cleaned_data["search"]:
        search = form.cleaned_data["search"]
        search_in = form.cleaned_data.get("search_in") or "title"
        if search_in == "tags":
            posts = Post.objects.filter(title__icontains=search)
        else:
            user=get_user_by_username(search_text)
            if user is not None:
                fname_contributors = \
                    Contributor.objects.filter(first_names__icontains=search)
                for contributor in fname_contributors:
                    for post in contributor.post_set.all():
                        posts.add(post)

                lname_contributors = \
                    Contributor.objects.filter(last_names__icontains=search)

                for contributor in lname_contributors:
                    for post in contributor.post_set.all():
                        posts.add(post)
            else:
                new_post = Post()
                new_post.title("asdasdasd")
                new_post.publisher("asdasd")
                new_post.isbn("asdasdasd")
                posts.add(new_post);
        if request.user.is_authenticated:
            search_history.append([search_in, search])
            request.session['search_history'] = search_history
    elif search_history:
        initial = dict(search=search_text,
                       search_in=search_history[-1][0])
        form = SearchForm(initial=initial)

    return render(request, "reviews/search-results.html", {"form": form, "search_text": search_text, "posts": posts})

def post_list(request):
    posts = Post.objects.all()
    posts_with_comments = []
    for post in posts:
        comments = post.comment_set.all()
        if comments:
            number_of_comments = len(comments)
        else:
            number_of_comments = 0
        posts_with_comments.append({"post": post, "number_of_comments": number_of_comments})

    context = {
        "post_list": posts_with_comments
    }
    return render(request, "reviews/post_list.html", context)


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comment_set.all()
    if comments:
        context = {
            "post": post,
            "comments": comments
        }
    else:
        context = {
            "post": post,
            "comments": None
        }
    if request.user.is_authenticated:
        max_viewed_posts_length = 10
        viewed_posts = request.session.get('viewed_posts', [])
        viewed_post = [post.id, post.title]
        if viewed_post in viewed_posts:
            viewed_posts.pop(viewed_posts.index(viewed_post))
        viewed_posts.insert(0, viewed_post)
        viewed_posts = viewed_posts[:max_viewed_posts_length]
        request.session['viewed_posts'] = viewed_posts
    return render(request, "reviews/post_detail.html", context)


def is_staff_user(user):
    return user.is_staff

@user_passes_test(is_staff_user)
def publisher_edit(request, pk=None):
    if pk is not None:
        publisher = get_object_or_404(Publisher, pk=pk)
    else:
        publisher = None

    if request.method == "POST":
        form = PublisherForm(request.POST, instance=publisher)
        if form.is_valid():
            updated_publisher = form.save()
            if publisher is None:
                messages.success(request, "Publisher \"{}\" was created.".format(updated_publisher))
            else:
                messages.success(request, "Publisher \"{}\" was updated.".format(updated_publisher))

            return redirect("publisher_edit", updated_publisher.pk)
    else:
        form = PublisherForm(instance=publisher)

    return render(request, "reviews/instance-form.html",
                  {"form": form, "instance": publisher, "model_type": "Publisher"})


@login_required
def comment_edit(request, post_pk, comment_pk=None):
    post = get_object_or_404(Post, pk=post_pk)

    if comment_pk is not None:
        comment = get_object_or_404(Comment, post_id=post_pk, pk=comment_pk)
        user = request.user
        if not user.is_staff and comment.creator.id != user.id:
            raise PermissionDenied
    else:
        comment = None

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            updated_comment = form.save(False)
            updated_comment.post = post

            if comment is None:
                messages.success(request, "Comment for \"{}\" created.".format(post))
            else:
                updated_comment.date_edited = timezone.now()
                messages.success(request, "Review for \"{}\" updated.".format(post))

            updated_comment.save()
            return redirect("post_detail", post.pk)
    else:
        form = CommentForm(instance=comment)

    return render(request, "reviews/instance-form.html",
                  {"form": form,
                   "instance": comment,
                   "model_type": "Comment",
                   "related_instance": post,
                   "related_model_type": "post"
                   })

@login_required
def post_media(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == "POST":
        form = PostMediaForm(request.POST, request.FILES, instance=post)

        if form.is_valid():
            post = form.save(False)

            cover = form.cleaned_data.get("cover")

            if cover:
                image = Image.open(cover)
                image.thumbnail((300, 300))
                image_data = BytesIO()
                image.save(fp=image_data, format=cover.image.format)
                image_file = ImageFile(image_data)
                post.cover.save(cover.name, image_file)
            post.save()
            messages.success(request, "post \"{}\" was successfully updated.".format(post))
            return redirect("post_detail", post.pk)
    else:
        form = PostMediaForm(instance=post)

    return render(request, "reviews/instance-form.html",
                  {"instance": post, "form": form, "model_type": "post", "is_file_upload": True})