import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crud', '0337_dynamic_date_defaults'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sale',
            name='datejoined',
            field=models.DateField(db_index=True, default=datetime.date.today, max_length=10, verbose_name='Fecha'),
        ),
        migrations.AlterField(
            model_name='sale',
            name='status',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AlterField(
            model_name='detcredit',
            name='last_credit_date',
            field=models.DateField(db_index=True, default=datetime.date.today, max_length=10, verbose_name='Fecha'),
        ),
        migrations.AlterField(
            model_name='credit',
            name='last_credit_date',
            field=models.DateField(db_index=True, default=datetime.date.today, max_length=10, verbose_name='Fecha'),
        ),
        migrations.AlterField(
            model_name='cashmovement',
            name='date_time',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='cashmovement',
            name='status',
            field=models.IntegerField(db_index=True, default=1),
        ),
        migrations.AlterField(
            model_name='product',
            name='status',
            field=models.IntegerField(db_index=True, default=1),
        ),
    ]
