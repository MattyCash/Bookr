import csv
import re

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from reviews.models import Publisher, Contributor, Post, postContributor, Comment


class Command(BaseCommand):
    help = 'Load the comments data from a CSV file.'

    def add_arguments(self, parser):
        parser.add_argument('--csv', type=str)

    @staticmethod
    def row_to_dict(row, header):
        if len(row) < len(header):
            row += [''] * (len(header) - len(row))
        return dict([(header[i], row[i]) for i, head in enumerate(header) if head])

    def handle(self, *args, **options):
        m = re.compile(r'content:(\w+)')
        header = None
        models = dict()
        try:
            with open(options['csv']) as csvfile:
                model_data = csv.reader(csvfile)
                for i, row in enumerate(model_data):
                    if max([len(cell.strip()) for cell in row[1:] + ['']]) == 0 and m.match(row[0]):
                        model_name = m.match(row[0]).groups()[0]
                        models[model_name] = []
                        header = None
                        continue

                    if header is None:
                        header = row
                        continue

                    row_dict = self.row_to_dict(row, header)
                    if set(row_dict.values()) == {''}:
                        continue
                    models[model_name].append(row_dict)

        except FileNotFoundError:
            raise CommandError('File "{}" does not exist'.format(options['csv']))

        for data_dict in models.get('Publisher', []):
            p, created = Publisher.objects.get_or_create(name=data_dict['publisher_name'], defaults={
                'website': data_dict['publisher_website'],
                'email': data_dict['publisher_email']
            })

            if created:
                print('Created Publisher "{}"'.format(p.name))

        for data_dict in models.get('post', []):
            b, created = Post.objects.get_or_create(title=data_dict['post_title'], defaults={
                'publication_date': data_dict['post_publication_date'].replace('/', '-'),
                'isbn': data_dict['post_isbn'],
                'publisher': Publisher.objects.get(name=data_dict['post_publisher_name'])
            })

            if created:
                print('Created Publisher "{}"'.format(b.title))

        for data_dict in models.get('Contributor', []):
            c, created = Contributor.objects.get_or_create(first_names=data_dict['contributor_first_names'],
                                                           last_names=data_dict['contributor_last_names'],
                                                           email=data_dict['contributor_email'])

            if created:
                print('Created Contributor "{} {}"'.format(data_dict['contributor_first_names'],
                                                           data_dict['contributor_last_names']))

        for data_dict in models.get('postContributor', []):
            post = post.objects.get(title=data_dict['post_contributor_post'])
            contributor = Contributor.objects.get(email=data_dict['post_contributor_contributor'])
            bc, created = postContributor.objects.get_or_create(post=post,
                                                                contributor=contributor,
                                                                role=data_dict['post_contributor_role'])
            if created:
                print('Created postContributor "{}" -> "{}"'.format(contributor.email, post.title))

        for data_dict in models.get('comment', []):
            creator, created = User.objects.get_or_create(email=data_dict['comment_creator'],
                                                          username=data_dict['comment_creator'])

            if created:
                print('Created User "{}"'.format(creator.email))
            post = post.objects.get(title=data_dict['comment_post'])

            comment, created = Comment.objects.get_or_create(content=data_dict['comment_content'],
                                                           post=post,
                                                           creator=creator,
                                                           defaults={
                                                               'rating': data_dict['comment_rating'],
                                                               'date_created': data_dict['comment_date_created'],
                                                               'date_edited': data_dict['comment_date_edited']
                                                           })
            if created:
                print('Created comment: "{}" -> "{}"'.format(post.title, creator.email))

        print("Import complete")