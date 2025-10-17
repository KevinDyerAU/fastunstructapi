# Metadata Capture Guide

This document explains all metadata captured by the Unstructured Workflow Endpoint and how to ensure accurate tracking of document information.

## 📋 Overview

The workflow automatically captures comprehensive metadata for every document element, including **filename**, **page numbers**, **coordinates**, and much more. This metadata is preserved through the entire processing pipeline and stored in your Supabase database.

## ✅ Metadata Captured by Default

### 🔑 Core Identification Metadata

| Field | Type | Description | Always Present |
|-------|------|-------------|----------------|
| **`filename`** | string | **Original document filename** (e.g., "report.pdf") | ✅ Yes |
| **`file_directory`** | string | Source directory path | ✅ Yes |
| **`page_number`** | integer | **Page number where element appears** | ✅ Yes (PDF, DOCX) |
| **`element_id`** | string | Unique identifier for the element | ✅ Yes |
| **`filetype`** | string | File extension (pdf, docx, etc.) | ✅ Yes |

### 📍 Position & Structure Metadata

| Field | Type | Description | When Present |
|-------|------|-------------|--------------|
| **`coordinates`** | object | Bounding box coordinates on page | When `coordinates: true` |
| `coordinates.points` | array | Corner points of element bounding box | With coordinates |
| `coordinates.system` | object | Coordinate system (PixelSpace, etc.) | With coordinates |
| **`parent_id`** | string | ID of parent element (for hierarchy) | For nested elements |
| **`category_depth`** | integer | Depth in document hierarchy | For structured docs |

### 📄 Content Metadata

| Field | Type | Description | When Present |
|-------|------|-------------|--------------|
| `text` | string | Extracted text content | Always |
| `type` | string | Element type (Title, NarrativeText, etc.) | Always |
| **`section`** | string | Section heading or title | When applicable |
| `languages` | array | Detected languages in element | Always |
| `is_continuation` | boolean | If element continues from previous page | For chunked content |

### 🖼️ Visual & Formatting Metadata

| Field | Type | Description | When Present |
|-------|------|-------------|--------------|
| `image_base64` | string | Base64 encoded image data | When extracting images |
| `image_mime_type` | string | Image format (image/png, etc.) | With images |
| `text_as_html` | string | HTML formatted text | When available |
| `emphasized_text_contents` | array | Bold, italic text | When detected |
| `emphasized_text_tags` | array | Formatting tags | When detected |

### 🔗 Document Structure Metadata

| Field | Type | Description | When Present |
|-------|------|-------------|--------------|
| `link_texts` | array | Hyperlink anchor text | When links present |
| `link_urls` | array | Hyperlink URLs | When links present |
| `header_footer_type` | string | Header/footer classification | Word documents |
| `page_name` | string | Sheet name | Excel files |

## 🎯 Enhanced Metadata Configuration

Our implementation uses **enhanced settings** to ensure comprehensive metadata capture:

### Partitioner Node Settings

```python
{
    # Strategy - determines extraction method
    "strategy": "hi_res",  # or "fast", "auto", "ocr_only", "vlm"
    
    # Structure Detection
    "pdf_infer_table_structure": True,  # Detect table structures
    "include_page_breaks": True,        # Mark page boundaries
    
    # Metadata Capture
    "coordinates": True,                # ✅ Capture element positions
    "extract_image_block_types": ["Image", "Table"],  # Extract visual elements
    
    # Language Detection
    "languages": ["eng"],               # Primary language (auto-detects others)
    
    # Element Tracking
    "unique_element_ids": True,         # Ensure globally unique IDs
}
```

### Chunker Node Settings

```python
{
    # Metadata Preservation
    "include_orig_elements": True,      # ✅ Preserve original element metadata
    "multipage_sections": True,         # Allow chunks across pages
    
    # Chunk Size Configuration
    "max_characters": 1500,             # Maximum chunk size
    "new_after_n_chars": 1000,          # Start new chunk threshold
    "overlap": 100,                     # Character overlap for context
}
```

## 📊 Supabase Table Schema

Your `elements` table stores all captured metadata:

```sql
CREATE TABLE elements (
    -- Core identification
    id UUID PRIMARY KEY,              -- Unique element ID
    element_id VARCHAR,               -- Element identifier
    record_id VARCHAR,                -- Record tracking ID
    
    -- Content
    text TEXT,                        -- Extracted text
    
    -- Metadata (CRITICAL FIELDS)
    filename VARCHAR,                 -- ⭐ Document filename
    page_number INTEGER,              -- ⭐ Page number
    filetype VARCHAR,                 -- File type
    
    -- Structure & Relationships  
    parent_id VARCHAR,                -- Parent element ID
    is_continuation BOOLEAN,          -- Continuation flag
    
    -- Additional metadata
    embeddings DECIMAL[],             -- Vector embeddings (if enabled)
    orig_elements TEXT,               -- Original element metadata (JSON)
    partitioner_type VARCHAR          -- Strategy used for partitioning
);
```

## 🔍 Metadata in Action

### Example: Processed PDF Element

When a PDF page is processed, you'll get metadata like:

```json
{
  "element_id": "abc123def456",
  "type": "Title",
  "text": "Quarterly Financial Report",
  "metadata": {
    "filename": "Q4-2024-Report.pdf",       // ⭐ Document name
    "page_number": 3,                       // ⭐ Page number
    "filetype": "application/pdf",
    "file_directory": "s3://my-bucket/reports/",
    "coordinates": {
      "points": [
        [100, 50], [100, 80], [500, 80], [500, 50]
      ],
      "system": "PixelSpace",
      "layout_width": 612,
      "layout_height": 792
    },
    "languages": ["eng"],
    "detection_class_prob": 0.98
  }
}
```

### Example: After Chunking

Chunked elements preserve original metadata:

```json
{
  "chunk_id": "chunk_001",
  "text": "Q4 revenue increased by 25%...",
  "metadata": {
    "filename": "Q4-2024-Report.pdf",       // ⭐ Preserved
    "page_number": 3,                       // ⭐ Preserved
    "parent_id": "abc123def456",            // Link to original element
    "is_continuation": false,
    "orig_elements": [                      // Original element metadata
      {
        "element_id": "abc123def456",
        "type": "Title",
        "page_number": 3
      }
    ]
  }
}
```

## 🎯 Ensuring Accuracy

### 1. **Filename Tracking** ✅
- **Source**: Extracted from S3 object key automatically
- **Accuracy**: 100% - directly from S3 metadata
- **Location**: `metadata.filename`
- **Example**: `"annual-report-2024.pdf"`

### 2. **Page Number Tracking** ✅
- **Source**: Extracted during partitioning
- **Accuracy**: 100% for PDF, DOCX, PPTX
- **Location**: `metadata.page_number`
- **Example**: `1`, `2`, `3`, etc.
- **Note**: Not applicable for text files or emails

### 3. **Element Position** ✅
- **Source**: Bounding box coordinates
- **Enabled**: `"coordinates": True`
- **Accuracy**: Pixel-perfect for hi_res strategy
- **Location**: `metadata.coordinates`

### 4. **Document Hierarchy** ✅
- **Source**: Parent-child relationships
- **Preserved**: Through `parent_id` and `category_depth`
- **Use**: Reconstruct document structure

## 🔧 Configuration Tips

### For Maximum Metadata Accuracy

1. **Use `hi_res` or `vlm` strategy**
   - Better element detection
   - More accurate page numbers
   - Precise coordinate extraction

2. **Enable coordinates capture**
   ```python
   "coordinates": True
   ```

3. **Preserve original elements in chunks**
   ```python
   "include_orig_elements": True
   ```

4. **Use unique element IDs**
   ```python
   "unique_element_ids": True
   ```

### For Specific Document Types

**PDFs with Tables:**
```python
{
    "strategy": "hi_res",
    "pdf_infer_table_structure": True,
    "coordinates": True
}
```

**Scanned Documents:**
```python
{
    "strategy": "ocr_only",
    "coordinates": True,
    "languages": ["eng", "spa"]  # Multiple languages
}
```

**Visual Documents:**
```python
{
    "strategy": "vlm",
    "extract_image_block_types": ["Image", "Table"],
    "coordinates": True
}
```

## 📈 Querying Metadata in Supabase

### Find all elements from a specific document:
```sql
SELECT * FROM elements 
WHERE orig_elements::jsonb @> '[{"filename": "report.pdf"}]';
```

### Find elements from specific page:
```sql
SELECT * FROM elements 
WHERE page_number = 5 
  AND orig_elements::jsonb @> '[{"filename": "report.pdf"}]';
```

### Get document page count:
```sql
SELECT MAX(page_number) as total_pages 
FROM elements 
WHERE orig_elements::jsonb @> '[{"filename": "report.pdf"}]';
```

## ✅ Verification Checklist

After processing, verify metadata capture:

- [ ] `filename` is present in all records
- [ ] `page_number` is accurate (for PDF/DOCX)
- [ ] `coordinates` are captured (when enabled)
- [ ] `parent_id` links are maintained
- [ ] `orig_elements` preserves original metadata
- [ ] Text content matches source document
- [ ] Element types are correctly classified

## 🚀 Best Practices

1. **Always check logs** - Workflow IDs and job IDs are logged
2. **Monitor Supabase** - Verify data is flowing correctly
3. **Test with sample documents** - Validate metadata before production
4. **Use consistent naming** - S3 file naming helps with tracking
5. **Enable coordinates** - Useful for visual document reconstruction
6. **Preserve original elements** - Critical for traceability

## 📚 Related Documentation

- [Unstructured Document Elements](https://docs.unstructured.io/api-reference/partition/document-elements)
- [Strategy Options Guide](STRATEGY_OPTIONS.md)
- [Main README](../README.md)
- [Migration Summary](MIGRATION_SUMMARY.md)

---

**Summary**: The workflow captures **comprehensive metadata** including filename and page numbers by default. Enhanced configuration ensures maximum accuracy and preservation through the entire processing pipeline.
