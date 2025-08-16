# Generated manually for model_type field addition

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_hyperparameterpreset'),
    ]

    operations = [
        migrations.AddField(
            model_name='hyperparameterpreset',
            name='model_type',
            field=models.CharField(
                choices=[
                    ('RandomForestRegressor', 'Random Forest'),
                    ('GradientBoostingRegressor', 'Gradient Boosting'),
                    ('LinearRegression', 'Regresión Lineal')
                ],
                default='RandomForestRegressor',
                help_text='ML model type this preset is designed for',
                max_length=100
            ),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='hyperparameterpreset',
            unique_together={('name', 'user', 'model_type')},
        ),
    ]
