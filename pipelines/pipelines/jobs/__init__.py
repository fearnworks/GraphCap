from .basic import basic_caption_pipeline
from .dataset_import_job import dataset_import_job
from .omi import omi_perspective_pipeline_job

JOBS = [omi_perspective_pipeline_job, basic_caption_pipeline, dataset_import_job]
