from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_alter_user_managers_alter_user_first_name_and_more"),
        ("courses", "0002_alter_coursemodule_options_course_slug_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="course",
            name="is_published",
        ),
        migrations.AddField(
            model_name="course",
            name="created_by",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_courses", to="accounts.user"),
        ),
        migrations.AddField(
            model_name="course",
            name="status",
            field=models.CharField(choices=[("draft", "Draft"), ("published", "Published"), ("archived", "Archived")], default="draft", max_length=20),
        ),
        migrations.AddField(
            model_name="course",
            name="updated_by",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="updated_courses", to="accounts.user"),
        ),
        migrations.AddConstraint(
            model_name="coursemodule",
            constraint=models.UniqueConstraint(fields=("course", "order"), name="uniq_course_module_order"),
        ),
    ]
