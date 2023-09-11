from django.contrib import admin

from .models import Post, Comment,Tag

class postAdmin(admin.ModelAdmin):
  model = Post
  list_display = ('title', 'isbn', 'get_publisher', 'publication_date')
  search_fields = ['title', 'publisher__name']

  def get_publisher(self, obj):
    return obj.publisher.name

admin.site.register(Post, postAdmin)
admin.site.register(Comment)
admin.site.register(Tag)