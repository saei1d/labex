from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_alter_user_managers_alter_user_first_name_and_more"),
        ("labs", "0004_lab_workflow_and_security_fields"),
        ("courses", "0003_course_status_and_audit_fields"),
        ("progress", "0001_initial"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="usercourseprogress",
            constraint=models.UniqueConstraint(fields=("user", "course"), name="uniq_user_course_progress"),
        ),
        migrations.AddConstraint(
            model_name="userlabprogress",
            constraint=models.UniqueConstraint(fields=("user", "lab"), name="uniq_user_lab_progress"),
        ),
        migrations.CreateModel(
            name="UserTaskProgress",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_unlocked", models.BooleanField(default=False)),
                ("completed", models.BooleanField(default=False)),
                ("last_score", models.FloatField(default=0)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("task", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="labs.labtask")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="accounts.user")),
            ],
        ),
        migrations.AddConstraint(
            model_name="usertaskprogress",
            constraint=models.UniqueConstraint(fields=("user", "task"), name="uniq_user_task_progress"),
        ),
    ]
