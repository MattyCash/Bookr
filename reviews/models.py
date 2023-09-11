from django.contrib import auth
from django.db import models


class Publisher(models.Model):
    """A company that publishes posts."""
    name = models.CharField(max_length=50,
                            help_text="The name of the Publisher.")
    website = models.URLField(help_text="The Publisher's website.")
    email = models.EmailField(help_text="The Publisher's email address.")

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Post(models.Model):
    """A published post."""
    title = models.CharField(max_length=70,
                             help_text="The title of the post.")
    publication_date = models.DateField(
        verbose_name="Date the post was published.")
    isbn = models.CharField(max_length=20,
                            verbose_name="ISBN number of the post.")
    publisher = models.ForeignKey(Publisher,
                                  on_delete=models.CASCADE)
    contributors = models.ManyToManyField('Contributor',
                                          through="postContributor")
    cover = models.ImageField(null=True,
                              blank=True,
                              upload_to="post_covers/")
    sample = models.FileField(null=True,
                              blank=True,
                              upload_to="post_samples/")
    tags=models.ManyToManyField(Tag)
    def __str__(self):
        return "{} ({})".format(self.title, self.isbn)

    def isbn13(self):
        """ '9780316769174' => '978-0-31-676917-4' """
        return "{}-{}-{}-{}-{}".format(self.isbn[0:3], self.isbn[3:4],
                                       self.isbn[4:6], self.isbn[6:12],
                                       self.isbn[12:13])


class Contributor(models.Model):
    """A contributor to a post, e.g. author, editor, co-author."""
    first_names = models.CharField(max_length=50,
                                   help_text="The contributor's first name or names.")
    last_names = models.CharField(max_length=50,
                                  help_text="The contributor's last name or names.")
    email = models.EmailField(help_text="The contact email for the contributor.")

    def initialled_name(self):
        """ self.first_names='Jerome David', self.last_names='Salinger'
            => 'Salinger, JD' """
        initials = ''.join([name[0] for name
                            in self.first_names.split(' ')])
        return "{}, {}".format(self.last_names, initials)

    def __str__(self):
        return self.initialled_name()

class postContributor(models.Model):
    class ContributionRole(models.TextChoices):
        AUTHOR = "AUTHOR", "Author"
        EDITOR = "EDITOR", "Editor"

    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    contributor = models.ForeignKey(Contributor, on_delete=models.CASCADE)
    role = models.CharField(verbose_name="The role this contributor had in the post.",
                            choices=ContributionRole.choices, max_length=20)
    def __str__(self):
        return "{} {} {}".format(self.contributor.initialled_name(), self.role, self.post.isbn)

class Comment(models.Model):
    content = models.TextField(help_text="")
    date_created = models.DateTimeField(auto_now_add=True,
                                        help_text="The date and time the review was created.")
    date_edited = models.DateTimeField(null=True,
                                       help_text="The date and time the review was last edited.")
    creator = models.ForeignKey(auth.get_user_model(), on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             help_text="The post that this review is for.")
    def __str__(self):
        return "{} - {}".format(self.creator.username, self.post.title)