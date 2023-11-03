# Generated by Django 4.2.6 on 2023-11-03 16:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Annotation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zotero_id', models.CharField(max_length=100, unique=True)),
                ('textselection', models.TextField(default='')),
                ('argname', models.CharField(default='', max_length=100)),
                ('description', models.TextField(default='')),
                ('argcont', models.BooleanField(null=True)),
                ('page_start', models.CharField(max_length=16, null=True)),
                ('page_end', models.CharField(max_length=16, null=True)),
                ('relation_type', models.CharField(choices=[('', 'None'), ('contradicts', 'Contradicts'), ('generalizes', 'Generalizes'), ('invalidates', 'Invalidates'), ('specialcase', 'Is a special case of'), ('supports', 'Supports')], default='', max_length=11)),
            ],
        ),
        migrations.CreateModel(
            name='ArticleTerm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('term', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=3, unique=True)),
                ('name', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LidiaTerm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vocab', models.CharField(choices=[('lol', 'Lexicon of Linguistics'), ('custom', 'Custom')], max_length=6)),
                ('term', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zotero_id', models.CharField(max_length=100, unique=True)),
                ('attachment_id', models.CharField(max_length=16, null=True, unique=True)),
                ('title', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TermGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('termtype', models.CharField(choices=[('', 'Undefined'), ('definiendum', 'Definiendum'), ('definiens', 'Definiens'), ('other', 'Other')], max_length=11)),
                ('annotation_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='lidia.annotation', to_field='zotero_id')),
                ('articleterm', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='lidia.articleterm')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='lidia.category')),
                ('lidiaterm', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='lidia.lidiaterm')),
            ],
        ),
        migrations.AddField(
            model_name='annotation',
            name='arglang',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='lidia.language', to_field='code'),
        ),
        migrations.AddField(
            model_name='annotation',
            name='parent_attachment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='lidia.publication', to_field='attachment_id'),
        ),
        migrations.AddField(
            model_name='annotation',
            name='relation_to',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='lidia.annotation', to_field='zotero_id'),
        ),
    ]
