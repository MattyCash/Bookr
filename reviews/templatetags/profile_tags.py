from django import template
from reviews.models import Comment, Post

register = template.Library()


@register.inclusion_tag('post_list.html')
def post_list(username):
    post_list = list(Post.objects.filter(creator__username_contains=username))
    return {'posts_read': post_list}
