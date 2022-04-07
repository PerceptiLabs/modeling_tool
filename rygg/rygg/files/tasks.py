from contextlib import contextmanager
import glob
import os
import pandas as pd

from rygg.files.utils.download_data import download
from rygg.files.utils.subprocesses import CanceledError
from rygg.files.utils.zip import unzipped_files
from rygg.tasks import run_async

# TODO: get this behind the tasks api
from celery import Celery
from rygg.tasks.celery import work_in_celery


app = Celery()


######################
# Utils
class DatasetOperationException(Exception):
    pass


@contextmanager
def dataset_operation(dataset_id):
    from rygg.api.models import Dataset

    dataset = Dataset.get_by_id(dataset_id)
    dataset.status = "processing"
    dataset.save()

    try:
        yield dataset
        dataset.status = "uploaded"
    except DatasetOperationException as e:
        dataset.status = f"failed: {e}"
        raise e
    except Exception as e:
        dataset.status = "failed"
        raise e
    finally:
        dataset.save()


def find_csv(root_dir):
    glob_pattern = os.path.join(root_dir, "**", "*.csv")
    matches = glob.glob(glob_pattern, recursive=True)

    if not matches:
        raise DatasetOperationException("no data found")

    return matches[0]


def rm_f(file):
    if os.path.exists(file):
        os.remove(file)


######################
# Unzip
def is_zip(file):
    return open(file, "rb").read(4) == b"PK\x03\x04"


def is_csv(file):
    content = open(file, "r").read(100)
    # very rudimentary check that it's csv
    return len(content) > 0 and "," in content


def unzip(cancel_token, status_callback, dataset_id):
    with dataset_operation(dataset_id) as dataset:
        filepath = dataset.upload_path

        # if the filepath is a zip, then unzip
        if is_zip(filepath):
            unzipped = unzipped_files(
                filepath, dest=dataset.root_dir, cancel_token=cancel_token
            )
            for unzipped_ix, _ in enumerate(unzipped):
                status_callback(1, 0, "Unzipping", len(unzipped), unzipped_ix)

            # remove the zip
            rm_f(filepath)

            # point the dataset at the csv
            dataset.location = find_csv(dataset.root_dir)

        elif is_csv(filepath):
            os.makedirs(dataset.root_dir, exist_ok=True)
            dest = os.path.join(dataset.root_dir, "data.csv")
            os.rename(filepath, dest)
            dataset.location = dest


# Worker-side interface with celery
@app.task(
    name="unzip",  # must be in list in rygg/celery.py
    bind=True,
)
def unzip_task(self, dataset_id):
    work_in_celery(self, unzip, dataset_id)


# Caller-side interface with Celery and/or threading
def unzip_async(dataset_id):
    return run_async("unzip", unzip, dataset_id)


######################
# Download/Unzip
@app.task(
    name="download",  # must be in list in rygg/celery.py
    bind=True,
)
def download_task(self, dataset_id):
    work_in_celery(self, download_unzip, dataset_id)


def download_unzip(cancel_token, status_callback, dataset_id):
    from rygg.api.models import Dataset

    try:
        dataset = Dataset.objects.get(dataset_id=dataset_id)
        dataset.status = "uploading"
        dataset.save()
        file_path, chunk_count, chunks = download(
            dataset.source_url, dataset.root_dir, cancel_token
        )
        for chunk_ix, _ in enumerate(chunks):
            status_callback(2, 0, "Downloading", chunk_count, chunk_ix)

        if not os.path.isfile(file_path):
            raise Exception("Internal Error: downloading didn't generate a file")

        # re-fetch the dataset just in case it's been deleted
        dataset = Dataset.objects.get(dataset_id=dataset_id)

        unzipped = unzipped_files(
            file_path, dest=dataset.root_dir, cancel_token=cancel_token
        )
        for unzipped_ix, _ in enumerate(unzipped):
            status_callback(2, 1, "Unzipping", len(unzipped), unzipped_ix)

        glob_pattern = os.path.join(dataset.root_dir, "**", "*.csv")
        matches = glob.glob(glob_pattern, recursive=True)
        if matches:
            dataset.status = "uploaded"
            dataset.location = matches[0]
        else:
            dataset.status = "failed: no data found"
        dataset.save()
    except Dataset.DoesNotExist:
        # if the dataset is missing, then we're done
        pass
    except CanceledError:

        # if we got here from an error or cancellation, then clean up
        if dataset:
            dataset.delete()

    except Exception as e:

        # if we got here from an error or cancellation, then clean up
        if dataset:
            dataset.delete()

        raise e

    finally:

        # remove the zip
        if os.path.exists(file_path):
            os.remove(file_path)


def download_async(dataset_id):
    return run_async("download", download_unzip, dataset_id)


######################
# Create classification CSV
@app.task(
    name="create_classification_csv",
    bind=True,
)
def create_classification_csv_task(self, dataset_id):
    work_in_celery(self, create_classification_csv, dataset_id)


def _create_classification_csv(dataset, dataset_path):
    csv_path = dataset.location

    def get_files_in_category(path, category):
        files_list = os.listdir(path)
        if ".DS_Store" in files_list:
            files_list.remove(".DS_Store")
        files = [os.path.join(category, file) for file in files_list]
        categories = [category for file in files]
        return files, categories

    expected_count = 0  # TODO: count the files in the dataset's directories
    files = []

    categories = []
    # read all folders in the directory
    for folder in os.listdir(dataset_path):
        folder_path = os.path.join(dataset_path, folder)
        if os.path.isdir(folder_path):
            files_in_folder, categories_in_folder = get_files_in_category(
                folder_path, folder
            )
            files += files_in_folder
            categories += categories_in_folder
            expected_count = len(files)

    # create dataframe and save as csv
    df = pd.DataFrame({"images": files, "category": categories})
    df = df.sample(frac=1)
    df.to_csv(csv_path, encoding="utf-8", index=False)
    return expected_count, files


def create_classification_csv(cancel_token, status_callback, dataset, dataset_path):
    from rygg.api.models import Dataset

    if dataset.exists_on_disk:
        dataset.status = "uploaded"
        dataset.save()
        return

    def clean_up():
        if csv_path and os.path.isfile(csv_path):
            os.remove(csv_path)

    try:
        csv_path = dataset.location
        dataset.status = "building csv"
        dataset.save()

        expected_count, scanned_files = _create_classification_csv(
            dataset, dataset_path
        )
        for file_ix, _ in enumerate(scanned_files):
            status_callback(1, 0, "Building CSV", expected_count, file_ix)

        dataset.status = "uploaded"
        dataset.save()

    except Dataset.DoesNotExist:
        # noop if no dataset
        pass

    except CanceledError:
        clean_up()

    except Exception as e:
        clean_up()
        raise e


def create_classification_csv_async(dataset, dataset_path):
    return run_async(
        "create_classification_csv", create_classification_csv, dataset, dataset_path
    )


######################
# Create segmentation CSV
@app.task(
    name="create_segmentation_csv",
    bind=True,
)
def create_segmentation_csv_task(self, dataset_id):
    work_in_celery(self, create_segmentation_csv, dataset_id)


def _create_segmentation_csv(dataset, image_path, mask_path):
    csv_path = dataset.location

    def get_files_in_category(path):
        files_list = os.listdir(path)
        if ".DS_Store" in files_list:
            files_list.remove(".DS_Store")
        files = [os.path.join(path, file) for file in files_list]
        return files

    expected_count = 0  # TODO: count the files in the dataset's directories
    image_files = []
    mask_files = []

    # read all folders in the directory
    image_files = sorted(get_files_in_category(image_path))
    mask_files = sorted(get_files_in_category(mask_path))

    assert len(mask_files) == len(image_files)

    files = image_files + mask_files
    expected_count = len(files)

    # create dataframe and save as csv
    df = pd.DataFrame({"images": image_files, "mask": mask_files})
    df.to_csv(csv_path, encoding="utf-8", index=False)

    return expected_count, files


def create_segmentation_csv(
    cancel_token, status_callback, dataset, image_path, mask_path
):
    from rygg.api.models import Dataset

    if dataset.exists_on_disk:
        dataset.status = "uploaded"
        dataset.save()
        return

    def clean_up():
        if csv_path and os.path.isfile(csv_path):
            os.remove(csv_path)

    try:
        csv_path = dataset.location
        dataset.status = "building csv"
        dataset.save()

        expected_count, scanned_files = _create_segmentation_csv(
            dataset, image_path, mask_path
        )
        for file_ix, _ in enumerate(scanned_files):
            status_callback(1, 0, "Building CSV", expected_count, file_ix)

        dataset.status = "uploaded"
        dataset.save()

    except Dataset.DoesNotExist:
        # noop if no dataset
        pass

    except CanceledError:
        clean_up()

    except Exception as e:
        clean_up()
        raise e


def create_segmentation_csv_async(dataset, image_path, mask_path):
    return run_async(
        "create_segmentation_csv",
        create_segmentation_csv,
        dataset,
        image_path,
        mask_path,
    )


######################
# Create classification CSV from upload
@app.task(
    name="classification_from_upload",
    bind=True,
)
def classification_from_upload_task(self, dataset_id):
    work_in_celery(self, create_classification_csv_from_upload, dataset_id)


def create_classification_csv_from_upload(cancel_token, status_callback, dataset_id):
    from rygg.api.models import Dataset

    with dataset_operation(dataset_id) as dataset:
        filepath = dataset.upload_path
        dataset_dir = os.path.splitext(filepath)[0]
        # if the filepath is a zip, then unzip
        if is_zip(filepath):
            unzipped = unzipped_files(
                filepath, dest=dataset.root_dir, cancel_token=cancel_token
            )
            for unzipped_ix, _ in enumerate(unzipped):
                status_callback(1, 0, "Unzipping", len(unzipped), unzipped_ix)

            # point the dataset at the csv
            dataset_path = os.path.splitext(filepath)[0]
            dataset.location = os.path.join(dataset_path, "pl_data.csv")
            dataset.save()

            # remove the zip
            rm_f(filepath)

        create_classification_csv(cancel_token, status_callback, dataset, dataset_path)


def classification_from_upload_async(dataset_id):
    return run_async(
        "classification_from_upload", create_classification_csv_from_upload, dataset_id
    )


######################
# Create segmentation CSV from upload
@app.task(
    name="segmentation_from_upload",
    bind=True,
)
def segmentation_from_upload_task(
    self, dataset_id, images_upload_path, masks_upload_path
):
    work_in_celery(
        self,
        create_segmentation_csv_from_upload,
        dataset_id,
        images_upload_path,
        masks_upload_path,
    )


def create_segmentation_csv_from_upload(
    cancel_token, status_callback, dataset_id, images_upload_path, masks_upload_path
):
    from rygg.api.models import Dataset

    with dataset_operation(dataset_id) as dataset:
        # if the filepath is a zip, then unzip
        for filepath in [images_upload_path, masks_upload_path]:
            # filepath = os.path.join(dataset_path, file_path)
            if is_zip(filepath):
                unzipped = unzipped_files(
                    filepath, dest=dataset.root_dir, cancel_token=cancel_token
                )
                i = 0
                for unzipped_ix, _ in enumerate(unzipped):
                    status_callback(2, i, "Unzipping", len(unzipped), unzipped_ix)
                i += 1
                # remove the zip
                rm_f(filepath)

        dataset.save()

        image_folder = os.path.splitext(images_upload_path)[0]
        mask_folder = os.path.splitext(masks_upload_path)[0]
        create_segmentation_csv(
            cancel_token, status_callback, dataset, image_folder, mask_folder
        )


def segmentation_from_upload_async(dataset_id, images_upload_path, masks_upload_path):
    return run_async(
        "segmentation_from_upload",
        create_segmentation_csv_from_upload,
        dataset_id,
        images_upload_path,
        masks_upload_path,
    )
