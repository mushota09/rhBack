import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rhBack.settings')
django.setup()

from user_app.models import User, Group, UserGroup
from user_app.modules.user_group.serializers import I_UserGroupSerializers

# Create test data
admin_user = User.objects.filter(email='admin@example.com').first()
if not admin_user:
    admin_user = User.objects.create_user(
        email='admin@example.com',
        password='testpass123',
        nom='Admin',
        prenom='User'
    )

regular_user = User.objects.filter(email='user@example.com').first()
if not regular_user:
    regular_user = User.objects.create_user(
        email='user@example.com',
        password='testpass123',
        nom='Regular',
        prenom='User'
    )

rrh_group = Group.objects.filter(code='RRH').first()
if not rrh_group:
    rrh_group = Group.objects.create(
        code='RRH',
        name='Responsable Ressources Humaines',
        description='Responsable des ressources humaines'
    )

# Test serializer
data = {
    'user': regular_user.id,
    'group': rrh_group.id,
    'assigned_by': admin_user.id
}

print(f"Input data: {data}")
print(f"User ID: {regular_user.id}, Group ID: {rrh_group.id}, Admin ID: {admin_user.id}")

serializer = I_UserGroupSerializers(data=data)
print(f"Is valid: {serializer.is_valid()}")
if not serializer.is_valid():
    print(f"Errors: {serializer.errors}")
else:
    print(f"Validated data: {serializer.validated_data}")
    instance = serializer.save()
    print(f"Created instance: {instance}")
    print(f"Instance user: {instance.user}, group: {instance.group}, assigned_by: {instance.assigned_by}")
