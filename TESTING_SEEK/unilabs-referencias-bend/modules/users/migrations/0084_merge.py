# users/migrations/0084_merge.py
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0019_loggeduser_change_password'),
        ('users', '0020_alter_loggeduser_change_password'),
        ('users', '0021_auto_20220509_1703'),
        ('users', '0022_auto_20220509_1709'),
        ('users', '0023_auto_20220509_1710'),
        ('users', '0083_merge'),
    ]
    operations = []
