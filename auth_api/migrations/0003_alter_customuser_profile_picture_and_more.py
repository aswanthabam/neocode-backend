# Generated by Django 5.2.4 on 2025-07-19 22:13

import common.fields
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_api', '0002_alter_customuser_managers_customuser_address_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='profile_picture',
            field=common.fields.ProfileImageField(blank=True, null=True, upload_to='profile-images/'),
        ),
        migrations.CreateModel(
            name='UserSecuritySettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('secret_pin', models.CharField(blank=True, help_text='Hashed secret PIN', max_length=255, null=True)),
                ('pin_created_at', models.DateTimeField(blank=True, null=True)),
                ('pin_last_used', models.DateTimeField(blank=True, null=True)),
                ('biometric_enabled', models.BooleanField(default=False, help_text='Whether biometric authentication is enabled')),
                ('biometric_type', models.CharField(blank=True, choices=[('fingerprint', 'Fingerprint'), ('face', 'Face Recognition'), ('touch', 'Touch ID'), ('face_id', 'Face ID')], max_length=20, null=True)),
                ('require_pin_for_downloads', models.BooleanField(default=True, help_text='Require PIN for document downloads')),
                ('require_pin_for_sharing', models.BooleanField(default=True, help_text='Require PIN for document sharing')),
                ('require_pin_for_deletion', models.BooleanField(default=True, help_text='Require PIN for document deletion')),
                ('auto_lock_timeout', models.IntegerField(default=300, help_text='Auto-lock timeout in seconds (0 = disabled)')),
                ('max_login_attempts', models.IntegerField(default=5, help_text='Maximum failed login attempts')),
                ('lockout_duration', models.IntegerField(default=900, help_text='Lockout duration in seconds')),
                ('two_factor_enabled', models.BooleanField(default=False, help_text='Whether 2FA is enabled')),
                ('backup_codes', models.JSONField(blank=True, default=list, help_text='Backup codes for 2FA')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='security_settings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Security Settings',
                'verbose_name_plural': 'User Security Settings',
            },
        ),
    ]
