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
from unstructured_ingest.v2.processes.embedder import EmbedderConfig
from unstructured_ingest.v2.processes.connectors.fsspec.s3 import (
    S3ConnectionConfig,
    S3AccessConfig,
    S3UploaderConfig
)


from unstructured_ingest.v2.processes.connectors.pinecone import (
    PineconeConnectionConfig,
    PineconeAccessConfig,
    PineconeUploaderConfig,
    PineconeUploadStagerConfig
)


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
    awsK = data.get("awsK")
    awsS = data.get("awsS")
    unstrK = data.get("unstrK")


    await startPipeline(fileName, awsK, awsS, unstrK)

    message = f"Filename {fileName} received and processed"

    return jsonify({
        "Message": message
    })



async def startPipeline(folder: str, awsK: str, awsS: str, unstK: str):
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
        destination_connection_config=PineconeConnectionConfig(
            access_config=PineconeAccessConfig(
                api_key=''
            ),
            index_name='smarrto'
        ),
        stager_config=PineconeUploadStagerConfig(),
        uploader_config=PineconeUploaderConfig()
    ).run()
    

if __name__=="__main__":
    app.run(debug=True,host="0.0.0.0",port=8080)
# if __name__ == "__main__":
#     app.run(host='0.0.0.0',port=80)