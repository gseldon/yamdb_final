import os
from csv import DictReader

from django.core.management import BaseCommand
from reviews.models import (Categories, Comments, Genres, GenreTitle, Review,
                            Title, User)

DATA_DIR = 'static/data'
DATA_PATCH = {
    'users': os.path.join(DATA_DIR, 'users.csv'),
    'category': os.path.join(DATA_DIR, 'category.csv'),
    'genre': os.path.join(DATA_DIR, 'genre.csv'),
    'titles': os.path.join(DATA_DIR, 'titles.csv'),
    'genre_title': os.path.join(DATA_DIR, 'genre_title.csv'),
    'review': os.path.join(DATA_DIR, 'review.csv'),
    'comments': os.path.join(DATA_DIR, 'comments.csv'),
}


class Command(BaseCommand):
    help = 'Loads data from api_yamdb/static/data/*.csv'

    def handle(self, *args, **options):
        # Code to load the data into database
        for row in DictReader(open(DATA_PATCH['users'])):
            user = User(
                id=row['id'],
                username=row['username'],
                email=row['email'],
                role=row['role'],
                bio=row['bio'],
                first_name=row['first_name'],
                last_name=row['last_name'],
            )
            user.save()

        print('Loading data user')

        for row in DictReader(open(DATA_PATCH['category'])):
            category = Categories(
                id=row['id'],
                name=row['name'],
                slug=row['slug'],
            )
            category.save()

        print('Loading data category')

        for row in DictReader(open(DATA_PATCH['genre'])):
            genre = Genres(
                id=row['id'],
                name=row['name'],
                slug=row['slug'],
            )
            genre.save()

        print('Loading data genre')

        for row in DictReader(open(DATA_PATCH['titles'])):
            title = Title(
                id=row['id'],
                name=row['name'],
                year=row['year'],
                category_id=row['category'],
            )
            title.save()

        print('Loading data title')

        for row in DictReader(open(DATA_PATCH['genre_title'])):
            genre_title = GenreTitle(
                id=row['id'],
                title_id=row['title_id'],
                genre_id=row['genre_id'],
            )
            genre_title.save()

        print('Loading data genre_title')

        for row in DictReader(open(DATA_PATCH['review'])):
            review = Review(
                id=row['id'],
                title_id=row['title_id'],
                text=row['text'],
                author_id=row['author'],
                score=row['score'],
                pub_date=row['pub_date'],
            )
            review.save()

        print('Loading data review')

        for row in DictReader(open(DATA_PATCH['comments'])):
            comments = Comments(
                id=row['id'],
                review_id=row['review_id'],
                text=row['text'],
                author_id=row['author'],
                pub_date=row['pub_date'],
            )
            comments.save()

        print('Loading data comments')
