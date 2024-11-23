from unstructured_ingest.v2.pipeline.pipeline import Pipeline
from unstructured_ingest.v2.interfaces import ProcessorConfig

from unstructured_ingest.v2.processes.connectors.sql.postgres import (
    PostgresConnectionConfig,
    PostgresAccessConfig,
    PostgresUploaderConfig,
    PostgresUploadStagerConfig
)
from unstructured_ingest.v2.processes.connectors.local import (
    LocalIndexerConfig,
    LocalDownloaderConfig,
    LocalConnectionConfig
)
from unstructured_ingest.v2.processes.partitioner import PartitionerConfig
from unstructured_ingest.v2.processes.chunker import ChunkerConfig
from unstructured_ingest.v2.processes.embedder import EmbedderConfig

# Chunking and embedding are optional.

if __name__ == "__main__":
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
        indexer_config=LocalIndexerConfig(input_path='/mnt/c/temp/in'),
        downloader_config=LocalDownloaderConfig(),
        source_connection_config=LocalConnectionConfig(),
        partitioner_config=PartitionerConfig(
            partition_by_api=True,
            api_key='xQfdQBotLsruN9fFLB9sOdcez5wNIZ',
            partition_endpoint='https://api.unstructuredapp.io/general/v0/general',
            strategy="auto",
            additional_partition_args={
                "split_pdf_page": True,
                "split_pdf_allow_failed": True,
                "split_pdf_concurrency_level": 15
            }
        ),

        chunker_config=ChunkerConfig(chunking_strategy="by_title"),
        # embedder_config=EmbedderConfig(
        #     embedding_provider="openai",

        #     embedding_model="text-embedding-ada-002",
        # ),
        destination_connection_config=PostgresConnectionConfig(
            access_config=PostgresAccessConfig(password='xxx'),
            host='aws-0-ap-southeast-2.pooler.supabase.com',
            port='6543',
            username='postgres.nwwqkubrlvmrycubylso',
            database='postgres'
        ),
        stager_config=PostgresUploadStagerConfig(),
        uploader_config=PostgresUploaderConfig()
    ).run()