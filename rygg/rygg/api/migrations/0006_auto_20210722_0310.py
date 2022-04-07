# Generated by Django 3.2 on 2021-07-22 03:10

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import os
import json
import logging
import rygg.api.models

logger = logging.getLogger(__name__)
# rygg.settings isn't obeyed. Make it obey
logger.setLevel(os.getenv("PL_RYGG_LOG_LEVEL", "WARNING"))


def all_string_values(d):
    # Likely, it would be more straightforward if we just looked for certain keys that
    # are known to contain filenames. This could theoretically get false positives
    q = list(d.values())
    while q:
        v = q.pop()
        if isinstance(v, str):
            yield v
        elif isinstance(v, dict):
            q.extend(v.values())
        elif isinstance(v, list):
            q.extend(v)


def json_file_to_dict(json_file):
    try:
        with open(json_file, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(
            f"Error while attempting to load json file {json_file}. It will not be usable in PerceptiLabs modeling"
        )
        raise e


def csv_strings_from_model_json(json_file):
    d = json_file_to_dict(json_file)
    csvs = [s for s in all_string_values(d) if s.endswith(".csv")]
    uniq = list(set(csvs))
    return uniq


def csv_files_from_model_json(json_file):
    strings = csv_strings_from_model_json(json_file)
    return [f for f in strings if os.path.exists(f)]


def populate_existing_datasets(app, schema_editor):
    Model = app.get_model("api", "Model")
    Dataset = app.get_model("api", "Dataset")
    db_alias = schema_editor.connection.alias

    for m in Model.objects.using(db_alias).all():
        json_file = os.path.join(m.location, "model.json")
        if not os.path.exists(json_file):
            logger.debug(f"Skipping model {m.model_id}. {json_file} doesn't exist")
            m.is_removed = True
            m.save()
            continue

        try:
            csv_files = csv_files_from_model_json(json_file)
        except Exception:
            continue

        logger.debug(f"Got csv files: {csv_files}")

        # upsert dataset records for the csv files in the model's project
        for dataset_file in csv_files:
            ds, created = Dataset.objects.using(db_alias).update_or_create(
                location=dataset_file,
                project_id=m.project_id,
                defaults={"name": dataset_file, "status": "uploaded"},
            )
            action = "Created" if created else "Found"
            logger.debug(f"{action} dataset {ds.dataset_id} for {dataset_file}")

            # if the dataset wasn't created, then it might not be in the uploaded state.
            # Since we just checked that it's preset, we need to set it to uploaded
            if ds.status != "uploaded":
                logger.debug(f"Updating dataset {ds.id}'s status to uploaded")
                ds.status = "uploaded"
                ds.save()

            if not ds.models.filter(model_id=m.model_id).exists():
                logger.debug(
                    f"Adding link between model {m.model_id} and dataset {ds.dataset_id}."
                )
                ds.models.add(m.model_id)
                ds.save()


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0005_filelink_notebook"),
    ]

    operations = [
        migrations.AddField(
            model_name="model",
            name="is_removed",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="notebook",
            name="is_removed",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="project",
            name="is_removed",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="Dataset",
            fields=[
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                (
                    "status",
                    model_utils.fields.StatusField(
                        choices=[
                            ("new", "new"),
                            ("uploading", "uploading"),
                            ("uploaded", "uploaded"),
                        ],
                        default="new",
                        max_length=100,
                        no_check_for_status=True,
                        verbose_name="status",
                    ),
                ),
                (
                    "status_changed",
                    model_utils.fields.MonitorField(
                        default=django.utils.timezone.now,
                        monitor="status",
                        verbose_name="status changed",
                    ),
                ),
                ("is_removed", models.BooleanField(default=False)),
                ("dataset_id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=1000)),
                (
                    "location",
                    models.CharField(
                        blank=True,
                        max_length=1000,
                        validators=[
                            rygg.api.models.dataset.validate_file_name,
                            rygg.api.models.dataset.validate_file_exists,
                        ],
                    ),
                ),
                (
                    "models",
                    models.ManyToManyField(
                        blank=True, related_name="datasets", to="api.Model"
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="datasets",
                        to="api.project",
                    ),
                ),
            ],
            options={
                "unique_together": {("project", "name"), ("project", "location")},
            },
        ),
        migrations.RunPython(
            populate_existing_datasets,
            # Unapply isn't needed since rollback will remove any datasets
            migrations.RunPython.noop,
        ),
    ]
