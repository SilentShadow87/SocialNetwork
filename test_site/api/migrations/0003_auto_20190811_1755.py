# Generated by Django 2.2.4 on 2019-08-11 17:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20190811_1748'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postmodel',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blog_posts', to='api.ProfileModel'),
        ),
        migrations.AlterField(
            model_name='postmodel',
            name='likes',
            field=models.ManyToManyField(blank=True, related_name='liked_posts', to='api.ProfileModel'),
        ),
    ]
