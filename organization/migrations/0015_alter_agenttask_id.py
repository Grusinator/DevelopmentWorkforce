# Generated by Django 5.0.7 on 2024-07-31 19:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("organization", "0014_workitem_remove_agenttask_ado_task_id_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="agenttask",
            name="id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
