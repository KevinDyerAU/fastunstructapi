# from typing import Optional
import os

from unstructured_ingest.v2.pipeline.pipeline import Pipeline
from unstructured_ingest.v2.interfaces import ProcessorConfig
from unstructured_ingest.v2.processes.connectors.fsspec.s3 import (
    S3IndexerConfig,
    S3DownloaderConfig,
    S3ConnectionConfig,
    S3AccessConfig
)
from unstructured_ingest.v2.processes.partitioner import PartitionerConfig
from unstructured_ingest.v2.processes.chunker import ChunkerConfig
# from unstructured_ingest.v2.processes.embedder import EmbedderConfig
from unstructured_ingest.v2.processes.connectors.fsspec.s3 import (
    S3ConnectionConfig,
    S3AccessConfig,
    S3UploaderConfig
)

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


# async def read_item(folder: str):
#     background_tasks.add_task(process_files, folder)
#     background_tasks.add_task(startPipeline, folder)
#     return {"message": "File processing started"}

# def process_files(folder: str):
#     # Simulate image processing
#     time.sleep(2)
#     # Actual file processing would go here
#     print(f"Processed files "+folder)

# @app.post("/process-async")
# async def process_async(folder: str, background_tasks: BackgroundTasks):
#     background_tasks.add_task(process_files, folder)
#     background_tasks.add_task(startPipeline, folder)
#     return {"message": "File processing started"}

# Chunking and embedding are optional.
@app.get("/folder/{folder}")
def startPipeline(folder: str):
    Pipeline.from_configs(
        context=ProcessorConfig(),
        indexer_config=S3IndexerConfig(remote_url='s3://smartrtobucket/'+folder),
        downloader_config=S3DownloaderConfig(download_dir="/work"),
        source_connection_config=S3ConnectionConfig(
            access_config=S3AccessConfig(
                key=os.getenv('AWS_S3_KEY'),
                secret=os.getenv('AWS_S3_SECRET')
            )
        ),
        partitioner_config=PartitionerConfig(
            partition_by_api=True,
            api_key=os.getenv('UNSTRUCT_API_KEY'),
            partition_endpoint='https://api.unstructuredapp.io/general/v0/general',
            strategy="hi_res",
            additional_partition_args={
                "split_pdf_page": True,
                "split_pdf_allow_failed": True,
                "split_pdf_concurrency_level": 15
            }
        ),

        chunker_config=ChunkerConfig(chunking_strategy="by_title"),
        destination_connection_config=S3ConnectionConfig(
            access_config=S3AccessConfig(
                key=os.getenv('AWS_S3_KEY'),
                secret=os.getenv('AWS_S3_SECRET')
            )
        ),
        uploader_config=S3UploaderConfig(remote_url='s3://smartrtobucket/'+folder)
    ).run()
    return {"message": "File processing started"}