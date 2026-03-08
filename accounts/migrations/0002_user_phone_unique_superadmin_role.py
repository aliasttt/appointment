# Generated manually for unique phone and SUPERADMIN role

from django.db import migrations, models


def empty_phone_to_null(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.filter(phone="").update(phone=None)


def null_to_empty_phone(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.filter(phone__isnull=True).update(phone="")


def set_superadmin_role(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.filter(is_superuser=True).update(role="SUPERADMIN")


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        # 1) Allow NULL so we can backfill empty string to null
        migrations.AlterField(
            model_name="user",
            name="phone",
            field=models.CharField(
                blank=True,
                max_length=20,
                null=True,
                verbose_name="Telefon",
            ),
        ),
        migrations.RunPython(empty_phone_to_null, null_to_empty_phone),
        # 2) Add unique and help_text
        migrations.AlterField(
            model_name="user",
            name="phone",
            field=models.CharField(
                blank=True,
                help_text="İşletme sahibi için benzersiz olmalıdır.",
                max_length=20,
                null=True,
                unique=True,
                verbose_name="Telefon",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[
                    ("SUPERADMIN", "Süper Admin"),
                    ("OWNER", "İşletme Sahibi"),
                    ("STAFF", "Personel"),
                ],
                default="OWNER",
                max_length=20,
                verbose_name="Rol",
            ),
        ),
        migrations.RunPython(set_superadmin_role, noop_reverse),
    ]
