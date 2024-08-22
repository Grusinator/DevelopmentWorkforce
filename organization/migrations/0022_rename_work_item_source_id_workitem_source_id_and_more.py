# Generated by Django 5.0.7 on 2024-08-22 10:32

import organization.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("organization", "0021_workitem_description_workitem_title"),
    ]

    operations = [
        migrations.RenameField(
            model_name="workitem",
            old_name="work_item_source_id",
            new_name="source_id",
        ),
        migrations.AlterField(
            model_name="agenttask",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("completed", "Completed"),
                    ("in_progress", "In Progress"),
                    ("failed", "Failed"),
                ],
                default=organization.models.TaskStatusEnum["PENDING"],
                max_length=50,
            ),
        ),
    ]