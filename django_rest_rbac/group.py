import django
django.setup()
from django.contrib.auth.models import Group

GROUPS = ['admin', 'solution_rovider', 'solution_seeker.']

for group in GROUPS:
    new_group, created = Group.objects.get_or_create(name=group)