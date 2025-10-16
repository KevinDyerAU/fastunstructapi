# Unstructured Workflow Endpoint Migration Guide

## Overview

This application has been migrated from the deprecated **Partition Endpoint** (`unstructured_ingest`) to the modern **Workflow Endpoint** (`unstructured-client` SDK).

## Key Changes

### 1. Dependencies Updated

**Before:**
```
unstructured-ingest[remote,s3,pdf,docx]>=0.7.0
unstructured-ingest[postgres]
```

**After:**
```
unstructured-client>=0.30.6
```

### 2. Architecture Change

**Old Approach (Partition Endpoint):**
- Used `Pipeline.from_configs()` from `unstructured_ingest`
- Direct partition endpoint: `https://api.unstructuredapp.io/general/v0/general`
- Synchronous pipeline execution

**New Approach (Workflow Endpoint):**
- Uses `UnstructuredClient` SDK
- Base URL: `https://platform.unstructuredapp.io/api/v1`
- Creates: Source Connector → Destination Connector → Workflow → Job
- Asynchronous job-based execution

### 3. Workflow Components

The new implementation creates:

1. **S3 Source Connector**: Ingests files from S3
2. **PostgreSQL Destination Connector**: Sends processed data to Supabase
3. **Workflow with Nodes**:
   - **Partitioner Node**: Uses `hi_res` strategy with table inference
   - **Chunker Node**: Uses `chunk_by_title` strategy
4. **Job**: Executes the workflow

## Benefits

- ✅ **Production-ready**: Optimized for enterprise use
- ✅ **Better performance**: Latest vision transformer models
- ✅ **Batch processing**: Process multiple files efficiently
- ✅ **Cost optimization**: Built-in logic for best quality/cost ratio
- ✅ **Advanced features**: Access to embeddings, enrichments
- ✅ **SOC2 compliant**: Security and compliance standards

## API Usage

### Request Format

**POST** `/process`

```json
{
  "fileName": "s3://bucket-name/path/to/folder/",
  "awsK": "your-aws-access-key",
  "awsS": "your-aws-secret-key",
  "unstrK": "your-unstructured-api-key",
  "supaK": "your-supabase-password"
}
```

### Response

```json
{
  "status": "success",
  "message": "File s3://bucket-name/path/ processed successfully"
}
```

## Environment Setup

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Environment Variables

Set your Unstructured API key:
```bash
export UNSTRUCTURED_API_KEY="your-key-here"
```

Or pass it in the API request as `unstrK`.

## Workflow Execution Details

When you call the `/process` endpoint, the following happens:

1. **Creates S3 Source Connector** with your AWS credentials
2. **Creates PostgreSQL Destination Connector** for Supabase
3. **Creates Workflow** with:
   - Hi-res partitioning (with table inference)
   - By-title chunking (with multipage sections)
4. **Runs Job** to execute the workflow
5. **Returns** job ID and status

## Monitoring Jobs

The workflow runs asynchronously. To monitor:

- Job ID is printed in console logs
- Check Unstructured platform: https://platform.unstructured.io
- Use the SDK to query job status

## Configuration Options

### Partitioner Settings

Current settings:
- `strategy`: `hi_res` - High resolution partitioning
- `pdf_infer_table_structure`: `True` - Detect tables in PDFs
- `include_page_breaks`: `True` - Preserve page boundaries

### Chunker Settings

Current settings:
- `subtype`: `chunk_by_title` - Chunk by document titles/headings
- `include_orig_elements`: `False` - Don't include original elements
- `multipage_sections`: `True` - Allow chunks across pages

## Troubleshooting

### Common Issues

**Issue**: Authentication errors
- **Solution**: Verify your Unstructured API key is valid at https://platform.unstructured.io

**Issue**: S3 access denied
- **Solution**: Check AWS credentials have S3 read permissions

**Issue**: PostgreSQL connection fails
- **Solution**: Verify Supabase password and connection settings

## API Documentation

Full documentation: https://docs.unstructured.io/api-reference/workflow/overview

## Migration Notes

⚠️ **Breaking Changes:**
- The old `partition_endpoint` parameter is removed
- Workflow execution is now asynchronous (job-based)
- Connectors are created dynamically per request

✅ **Implemented Features:**
- ✅ Job status polling with configurable timeout (default: 1 hour, polls every 10 seconds)
- ✅ Webhook notifications for job completion (success, failure, or timeout)
- ✅ Optional synchronous mode (`waitForCompletion: true`) or async mode (`waitForCompletion: false`)

💡 **Future Enhancements:**
- Consider reusing connectors instead of creating new ones for better performance
- Add configurable polling intervals via API parameters
- Implement retry logic for failed webhook deliveries

