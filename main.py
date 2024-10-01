
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

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel

app = FastAPI()

class FileCreate(BaseModel):
    fileName: str

@app.get("/")
async def root():
    return {"message": "Hello World"}


# Chunking and embedding are optional.
@app.get("/folder/{folder}")
async def start_processing(folder: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(startPipeline, folder)
    return {"message": "File processing started"}


@app.post("/process_file/")
async def process_file(file_data: FileCreate, background_tasks: BackgroundTasks):
    fileName = file_data.fileName
    background_tasks.add_task(startPipeline, fileName)
    return {"message": "File processing started"}



def startPipeline(folder: str):
    Pipeline.from_configs(
        context=ProcessorConfig(),
        #indexer_config=S3IndexerConfig(remote_url='s3://smartrtobucket/SmartRTO/'+folder+"/"),
        indexer_config=S3IndexerConfig(remote_url=folder),
        downloader_config=S3DownloaderConfig(),
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
        #uploader_config=S3UploaderConfig(remote_url='s3://smartrtobucket/'+folder)
        uploader_config=S3UploaderConfig(remote_url=folder)
    ).run()
    