from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from courses.models import Course, CourseModule
from labs.models import Lab, LabSection, TestCase
import uuid

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample data for LabEx'

    def handle(self, *args, **options):
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            email='admin@labex.com',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('Created admin user: admin@labex.com')

        # Create sample course
        course, created = Course.objects.get_or_create(
            slug='python-basics',
            defaults={
                'title': 'Python Basics',
                'description': 'Learn the fundamentals of Python programming',
                'level': 'beginner',
                'is_published': True
            }
        )
        if created:
            self.stdout.write('Created course: Python Basics')

        # Create module
        module, created = CourseModule.objects.get_or_create(
            course=course,
            title='Variables and Data Types',
            defaults={'order': 1}
        )
        if created:
            self.stdout.write('Created module: Variables and Data Types')

        # Create lab
        lab, created = Lab.objects.get_or_create(
            module=module,
            title='Python Variables Lab',
            defaults={
                'docker_image': 'labex/python:latest',
                'difficulty': 'easy',
                'order': 1
            }
        )
        if created:
            self.stdout.write('Created lab: Python Variables Lab')

        # Create lab sections
        theory_section, created = LabSection.objects.get_or_create(
            lab=lab,
            title='Introduction to Variables',
            defaults={
                'content_md': '''# Python Variables

Variables are containers for storing data values.

## Creating Variables

```python
x = 5
y = "Hello"
name = "John Doe"
age = 25
```

## Variable Naming Rules

- Variable names must start with a letter or underscore
- Variable names cannot start with a number
- Variable names can only contain alphanumeric characters and underscores
- Variable names are case-sensitive

## Data Types

Python has various data types:
- Text Type: `str`
- Numeric Types: `int`, `float`, `complex`
- Sequence Types: `list`, `tuple`, `range`
- Mapping Type: `dict`
- Set Types: `set`, `frozenset`
- Boolean Type: `bool`''',
                'order': 1,
                'type': 'theory'
            }
        )

        task_section, created = LabSection.objects.get_or_create(
            lab=lab,
            title='Create Variables',
            defaults={
                'content_md': '''# Task: Create Variables

Create the following variables:
1. A variable named `name` with your name as a string
2. A variable named `age` with your age as an integer
3. A variable named `height` with your height as a float
4. A variable named `is_student` with value True

Print all variables to verify they work correctly.''',
                'order': 2,
                'type': 'task'
            }
        )

        # Create test cases for the task
        if created:
            TestCase.objects.get_or_create(
                lab_section=task_section,
                defaults={
                    'input_data': '',
                    'expected_output': 'Variables created successfully',
                    'test_code': '''def test_variables_exist():
    # Check if variables are defined
    assert 'name' in globals(), "Variable 'name' is not defined"
    assert 'age' in globals(), "Variable 'age' is not defined"
    assert 'height' in globals(), "Variable 'height' is not defined"
    assert 'is_student' in globals(), "Variable 'is_student' is not defined"

def test_variable_types():
    # Check variable types
    assert isinstance(name, str), "Variable 'name' should be a string"
    assert isinstance(age, int), "Variable 'age' should be an integer"
    assert isinstance(height, float), "Variable 'height' should be a float"
    assert isinstance(is_student, bool), "Variable 'is_student' should be a boolean"

def test_variable_values():
    # Check if variables have reasonable values
    assert len(name) > 0, "Variable 'name' should not be empty"
    assert age > 0, "Variable 'age' should be positive"
    assert height > 0, "Variable 'height' should be positive"
    print("All tests passed!")''',
                    'points': 10.0,
                    'order': 1
                }
            )
            self.stdout.write('Created test cases for task section')

        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
