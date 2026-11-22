from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crud', '0334_auto_20260609_1822'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detsale',
            name='quantity',
            field=models.DecimalField(decimal_places=3, default=0.0, max_digits=30, verbose_name='Cantidad'),
        ),
    ]
