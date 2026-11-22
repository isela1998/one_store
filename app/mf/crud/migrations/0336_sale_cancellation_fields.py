from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crud', '0335_alter_detsale_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='cancelled_by',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Anulada por'),
        ),
        migrations.AddField(
            model_name='sale',
            name='cancelled_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fecha de anulación'),
        ),
        migrations.AddField(
            model_name='sale',
            name='cancel_reason',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Motivo de anulación'),
        ),
    ]
