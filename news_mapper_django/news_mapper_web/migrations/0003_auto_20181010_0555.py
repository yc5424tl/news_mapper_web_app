# Generated by Django 2.1.2 on 2018-10-10 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news_mapper_web', '0002_auto_20180926_0432'),
    ]

    operations = [
        migrations.AlterField(
            model_name='query',
            name='_choropleth',
            field=models.FileField(blank=True, default=None, null=True, upload_to='E:\\Alpha\\Software Development Capstone - 2905-01\\My Files\\Projects\\news_mapper_django\\news_mapper_django\\news_mapper_web/media/news_mapper_web/html/'),
        ),
    ]