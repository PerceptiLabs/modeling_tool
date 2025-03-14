# Generated by Django 3.2 on 2022-01-13 13:26

from django.db import migrations, models
import rygg.api.models.dataset


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0013_ensure_dataset_id_in_settings"),
    ]

    operations = [
        migrations.AddField(
            model_name="dataset",
            name="type",
            field=models.CharField(
                default=rygg.api.models.dataset.Dataset.Type.MULTI_MODAL[0],
                max_length=1,
            ),
        ),
        migrations.AlterField(
            model_name="dataset",
            name="root_dir",
            field=models.CharField(
                blank=True,
                max_length=1000,
                validators=[rygg.api.models.dataset.validate_path],
            ),
        ),
    ]
