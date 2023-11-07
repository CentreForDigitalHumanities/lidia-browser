# Generated by Django 4.2.7 on 2023-11-07 14:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("lidia", "0004_alter_annotation_relation_to"),
    ]

    operations = [
        migrations.AddField(
            model_name="annotation",
            name="sort_index",
            field=models.CharField(
                default="",
                help_text="Index to keep order of annotation in document",
                max_length=100,
            ),
        ),
    ]
