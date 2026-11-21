import datetime
from django.db import migrations, models
import mf.crud.models


class Migration(migrations.Migration):

    dependencies = [
        ('crud', '0336_sale_cancellation_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permisology',
            name='day',
            field=models.DateField(default=datetime.date.today, max_length=50, verbose_name='Fecha de pago'),
        ),
        migrations.AlterField(
            model_name='eventos',
            name='day',
            field=models.DateField(default=datetime.date.today, max_length=50, verbose_name='Fecha'),
        ),
        migrations.AlterField(
            model_name='sale',
            name='datejoined',
            field=models.DateField(default=datetime.date.today, max_length=10, verbose_name='Fecha'),
        ),
        migrations.AlterField(
            model_name='sale',
            name='datehour',
            field=models.CharField(default=mf.crud.models.today_str, max_length=30, verbose_name='Fecha'),
        ),
        migrations.AlterField(
            model_name='credit',
            name='last_credit_date',
            field=models.DateField(default=datetime.date.today, max_length=10, verbose_name='Fecha'),
        ),
        migrations.AlterField(
            model_name='credit',
            name='datehour',
            field=models.CharField(default=mf.crud.models.today_str, max_length=30, verbose_name='Fecha'),
        ),
        migrations.AlterField(
            model_name='detcredit',
            name='last_credit_date',
            field=models.DateField(default=datetime.date.today, max_length=10, verbose_name='Fecha'),
        ),
        migrations.AlterField(
            model_name='detcredit',
            name='datehour',
            field=models.CharField(default=mf.crud.models.today_str, max_length=30, verbose_name='Fecha y Hora'),
        ),
        migrations.AlterField(
            model_name='budget',
            name='datejoined',
            field=models.DateField(default=datetime.date.today, max_length=10, verbose_name='Fecha'),
        ),
        migrations.AlterField(
            model_name='debt',
            name='last_credit_date',
            field=models.DateField(default=datetime.date.today, max_length=10, verbose_name='Fecha'),
        ),
        migrations.AlterField(
            model_name='debt',
            name='datehour',
            field=models.CharField(default=mf.crud.models.today_str, max_length=30, verbose_name='Fecha'),
        ),
        migrations.AlterField(
            model_name='detdebt',
            name='last_debt_date',
            field=models.DateField(default=datetime.date.today, max_length=10, verbose_name='Fecha'),
        ),
        migrations.AlterField(
            model_name='detdebt',
            name='datehour',
            field=models.CharField(default=mf.crud.models.today_str, max_length=30, verbose_name='Fecha y Hora'),
        ),
    ]
