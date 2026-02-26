from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_alter_user_managers_alter_user_first_name_and_more"),
        ("courses", "0003_course_status_and_audit_fields"),
        ("labs", "0003_remove_lab_order"),
    ]

    operations = [
        migrations.AddField(
            model_name="lab",
            name="created_by",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_labs", to="accounts.user"),
        ),
        migrations.AddField(
            model_name="lab",
            name="status",
            field=models.CharField(choices=[("draft", "Draft"), ("published", "Published"), ("archived", "Archived")], default="draft", max_length=20),
        ),
        migrations.AddField(
            model_name="lab",
            name="time_limit_minutes",
            field=models.PositiveIntegerField(default=90),
        ),
        migrations.AddField(
            model_name="lab",
            name="updated_by",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="updated_labs", to="accounts.user"),
        ),
        migrations.AlterField(
            model_name="labsection",
            name="type",
            field=models.CharField(choices=[("theory", "Theory"), ("task", "Task"), ("solution", "Solution")], max_length=20),
        ),
        migrations.AddField(
            model_name="labsession",
            name="access_token",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="labsession",
            name="expires_at",
            field=models.DateTimeField(auto_now_add=False, default=None, null=True),
        ),
        migrations.AddField(
            model_name="labsession",
            name="last_activity_at",
            field=models.DateTimeField(auto_now=True, null=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="labsession",
            name="port",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="labsession",
            name="workspace_path",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name="labsession",
            name="status",
            field=models.CharField(choices=[("running", "Running"), ("stopped", "Stopped"), ("finished", "Finished"), ("expired", "Expired")], max_length=20),
        ),
        migrations.CreateModel(
            name="LabTask",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("prompt_md", models.TextField()),
                ("order", models.PositiveIntegerField(default=0)),
                ("is_required", models.BooleanField(default=True)),
                ("max_attempts", models.PositiveIntegerField(default=10)),
                ("lab", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="tasks", to="labs.lab")),
                ("section", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="tasks", to="labs.labsection")),
            ],
            options={"ordering": ["order"]},
        ),
        migrations.CreateModel(
            name="TaskValidationRule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("type", models.CharField(choices=[("command", "Command"), ("script", "Script"), ("http", "HTTP")], default="command", max_length=20)),
                ("config_json", models.JSONField(default=dict)),
                ("timeout_seconds", models.PositiveIntegerField(default=15)),
                ("task", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="validation_rules", to="labs.labtask")),
            ],
        ),
        migrations.CreateModel(
            name="TaskAttempt",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("attempt_no", models.PositiveIntegerField(default=1)),
                ("status", models.CharField(choices=[("passed", "Passed"), ("failed", "Failed")], max_length=20)),
                ("score", models.FloatField(default=0)),
                ("feedback", models.TextField(blank=True)),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("finished_at", models.DateTimeField(auto_now=True)),
                ("session", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attempts", to="labs.labsession")),
                ("task", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attempts", to="labs.labtask")),
            ],
            options={"ordering": ["-started_at"]},
        ),
        migrations.AddConstraint(
            model_name="labsection",
            constraint=models.UniqueConstraint(fields=("lab", "order"), name="uniq_lab_section_order"),
        ),
        migrations.AddConstraint(
            model_name="labtask",
            constraint=models.UniqueConstraint(fields=("lab", "order"), name="uniq_lab_task_order"),
        ),
    ]
