# Generated by Django 4.2.6 on 2023-11-07 12:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("lidia", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="annotation",
            name="argcont",
            field=models.BooleanField(
                help_text="True if the annotation is a continuation of the previous argument",
                null=True,
                verbose_name="continuation",
            ),
        ),
        migrations.AlterField(
            model_name="annotation",
            name="arglang",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="lidia.language",
                to_field="code",
                verbose_name="subject language",
            ),
        ),
        migrations.AlterField(
            model_name="annotation",
            name="argname",
            field=models.CharField(
                default="", max_length=100, verbose_name="argument name"
            ),
        ),
        migrations.AlterField(
            model_name="annotation",
            name="page_end",
            field=models.CharField(max_length=16, null=True, verbose_name="end page"),
        ),
        migrations.AlterField(
            model_name="annotation",
            name="page_start",
            field=models.CharField(max_length=16, null=True, verbose_name="start page"),
        ),
        migrations.AlterField(
            model_name="annotation",
            name="parent_attachment",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="lidia.publication",
                to_field="attachment_id",
                verbose_name="publication",
            ),
        ),
        migrations.AlterField(
            model_name="annotation",
            name="textselection",
            field=models.TextField(default="", verbose_name="quoted text"),
        ),
        migrations.AlterField(
            model_name="annotation",
            name="zotero_id",
            field=models.CharField(
                max_length=100, unique=True, verbose_name="Zotero ID"
            ),
        ),
    ]
