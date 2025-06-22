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
    S3AccessConfig
)

from unstructured_ingest.v2.processes.connectors.sql.postgres import (
    PostgresConnectionConfig,
    PostgresAccessConfig,
    PostgresUploaderConfig,
    PostgresUploadStagerConfig
)

import os
from flask import Flask,jsonify,request

app = Flask(__name__)



@app.route("/")
def root():
    return jsonify({
        "Message": "app up and running successfully"
    })


# Chunking and embedding are optional.
@app.route("/access",methods=["POST"])
async def access():
    data = request.get_json()
    fileName = data.get("fileName")
    awsK = os.environ.get("AWS_ACCESS_KEY_ID1")
    awsS = os.environ.get("AWS_SECRET_ACCESS_KEY1")
    unstrK = os.environ.get("UNSTRUCTURED_API_KEY")
    supaK = os.environ.get("SUPABASE_PASSWORD")


    await startPipeline(fileName, awsK, awsS, unstrK, supaK)

    message = f"Filename {fileName} received and processed"

    return jsonify({
        "Message": message
    })



async def startPipeline(folder: str, awsK: str, awsS: str, unstK: str, supaK: str):
    # Specify which fields to output in the processed data. This can help prevent
    # database record insert issues, where a particular field in the processed data
    # does not match a column in the database table on insert.
    metadata_includes = [
        "id", "element_id", "text", "embeddings", "type", "system", "layout_width",
        "layout_height", "points", "url", "version", "date_created", "date_modified",
        "date_processed", "permissions_data", "record_locator", "category_depth",
        "parent_id", "attached_filename", "filetype", "last_modified", "file_directory",
        "filename", "languages", "page_number", "links", "page_name", "link_urls",
        "link_texts", "sent_from", "sent_to", "subject", "section", "header_footer_type",
        "emphasized_text_contents", "emphasized_text_tags", "text_as_html", "regex_metadata",
        "detection_class_prob"
    ]

    Pipeline.from_configs(
        context=ProcessorConfig(),
        indexer_config=S3IndexerConfig(remote_url=folder),
        downloader_config=S3DownloaderConfig(),
        source_connection_config=S3ConnectionConfig(
            access_config=S3AccessConfig(
                key=awsK,
                secret=awsS
            )
        ),
        partitioner_config=PartitionerConfig(
            partition_by_api=True,
            api_key=unstK,
            partition_endpoint='https://api.unstructuredapp.io/general/v0/general',
            strategy="hi_res",
            additional_partition_args={
                "split_pdf_page": True,
                "split_pdf_allow_failed": True,
                "split_pdf_concurrency_level": 15
            }
        ),

        chunker_config=ChunkerConfig(chunking_strategy="by_title"),
        destination_connection_config=PostgresConnectionConfig(
            access_config=PostgresAccessConfig(password=supaK),
            host='aws-0-ap-southeast-2.pooler.supabase.com',
            port='6543',
            username='postgres.nwwqkubrlvmrycubylso',
            database='postgres'
        ),
        stager_config=PostgresUploadStagerConfig(),
        uploader_config=PostgresUploaderConfig()
    ).run()
    

# if __name__=="__main__":
#     app.run(debug=True,host="0.0.0.0",port=8080)
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=80)