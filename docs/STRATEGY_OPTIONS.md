# Partitioning Strategy Options

This document provides detailed information about the 5 available partitioning strategies in the Unstructured Workflow Endpoint.

## 📋 Overview

The API supports 5 strategies for document partitioning, each optimized for different document types and use cases:

1. `hi_res` (default)
2. `fast`
3. `auto`
4. `ocr_only`
5. `vlm`

## 🎯 Strategy Details

### 1. hi_res (Default)
**High-Resolution Model-Based Partitioning**

```json
{
  "strategy": "hi_res"
}
```

**Description:**
- Uses advanced layout detection models to identify document structure
- Analyzes document layout to gain additional information about elements
- Provides the most accurate element classification

**Best For:**
- Complex documents with tables
- Forms and structured layouts
- Multi-column documents
- Documents requiring high accuracy

**Characteristics:**
- Processing time: Slower ⏱️
- Accuracy: Highest ⭐⭐⭐⭐⭐
- Cost: Higher 💰💰💰

**Use When:**
- Your use case is highly sensitive to correct classifications
- Processing tables and complex layouts
- Document structure matters for downstream tasks

---

### 2. fast
**Rule-Based Extraction**

```json
{
  "strategy": "fast"
}
```

**Description:**
- Uses traditional NLP extraction techniques
- Quickly pulls all text elements without layout analysis
- Rule-based approach (no AI models)

**Best For:**
- Simple text-heavy documents
- Plain text extraction
- High-volume processing where speed matters

**Characteristics:**
- Processing time: Fastest ⚡
- Accuracy: Lower ⭐⭐
- Cost: Lowest 💰

**⚠️ Warning:**
- Not recommended for image-based file types
- Will miss visual elements and layout information
- Limited table detection

**Use When:**
- Processing simple, text-only documents
- Speed is more important than accuracy
- Budget constraints require lowest cost option

---

### 3. auto
**Automatic Strategy Selection**

```json
{
  "strategy": "auto"
}
```

**Description:**
- Analyzes document characteristics automatically
- Chooses the best strategy based on document type
- Considers function parameters in decision

**Best For:**
- Mixed document types in same batch
- Unknown document formats
- General-purpose processing

**Characteristics:**
- Processing time: Variable (optimized per doc) ⏱️
- Accuracy: Variable (optimized) ⭐⭐⭐⭐
- Cost: Optimized 💰💰

**Use When:**
- Processing diverse document collections
- You want Unstructured to optimize for you
- Document types vary significantly

---

### 4. ocr_only
**Optical Character Recognition**

```json
{
  "strategy": "ocr_only"
}
```

**Description:**
- Uses OCR models to extract text from images
- Model-based approach specifically for image files
- Focuses on text extraction from visual sources

**Best For:**
- Scanned documents
- Images with text overlay
- PDFs that are images (not searchable text)
- Historical documents
- Screenshots

**Characteristics:**
- Processing time: Moderate ⏱️⏱️
- Accuracy: Good for images ⭐⭐⭐⭐
- Cost: Moderate 💰💰

**Use When:**
- Processing scanned documents
- Dealing with image-based PDFs
- Text is embedded in images

---

### 5. vlm (NEW!)
**Vision Language Model**

```json
{
  "strategy": "vlm"
}
```

**Description:**
- Uses advanced AI vision language models
- Understands visual context and relationships
- Can interpret charts, diagrams, and infographics
- Leverages latest AI for document understanding

**Best For:**
- Infographics and visual presentations
- Documents with charts and diagrams
- Complex visual layouts
- Documents where visual context matters
- Marketing materials and brochures

**Supported File Types:**
- `.bmp`, `.gif`, `.heic`, `.jpeg`, `.jpg`
- `.pdf`, `.png`, `.tiff`, `.webp`

**Characteristics:**
- Processing time: Slower (AI processing) ⏱️⏱️⏱️
- Accuracy: Highest for visual content ⭐⭐⭐⭐⭐
- Cost: Highest 💰💰💰💰

**Use When:**
- Visual understanding is critical
- Processing infographics or presentations
- Charts and diagrams need to be understood in context
- Maximum accuracy on image-based documents

---

## 📊 Quick Comparison Matrix

| Strategy | Speed | Accuracy | Cost | Best For |
|----------|-------|----------|------|----------|
| **hi_res** | ⏱️⏱️ | ⭐⭐⭐⭐⭐ | 💰💰💰 | Complex documents, tables |
| **fast** | ⚡ | ⭐⭐ | 💰 | Simple text documents |
| **auto** | ⏱️ | ⭐⭐⭐⭐ | 💰💰 | Mixed document types |
| **ocr_only** | ⏱️⏱️ | ⭐⭐⭐⭐ | 💰💰 | Scanned documents |
| **vlm** | ⏱️⏱️⏱️ | ⭐⭐⭐⭐⭐ | 💰💰💰💰 | Visual content, infographics |

## 🎨 Example Use Cases

### Scenario 1: Financial Reports
**Recommended: `hi_res`**
- Complex tables with financial data
- Multi-column layouts
- Structured forms

### Scenario 2: Email Archive
**Recommended: `fast`**
- Simple text content
- High volume
- No complex layouts

### Scenario 3: Document Management System
**Recommended: `auto`**
- Variety of document types
- Unknown formats
- Let Unstructured optimize

### Scenario 4: Historical Documents
**Recommended: `ocr_only`**
- Scanned from physical copies
- Image-based PDFs
- No native text layer

### Scenario 5: Marketing Materials
**Recommended: `vlm`**
- Infographics with charts
- Visual presentations
- Brand assets with text overlay

## 🔄 Changing Strategies

### Via API
```json
{
  "fileName": "s3://bucket/path/",
  "strategy": "vlm"
}
```

### Default Behavior
If no strategy is specified, the API uses `hi_res` as the default for best accuracy on complex documents.

## 💡 Best Practices

1. **Start with `auto`** if unsure - let Unstructured optimize
2. **Use `hi_res`** for production workloads requiring high accuracy
3. **Use `fast`** for dev/test environments or simple documents
4. **Use `ocr_only`** specifically for scanned documents
5. **Use `vlm`** when visual understanding is critical

## 📚 Additional Resources

- [Unstructured Partitioning Docs](https://docs.unstructured.io/api-reference/api-services/partitioning)
- [Workflow Endpoint Overview](https://docs.unstructured.io/api-reference/workflow/overview)
- [Main README](../README.md)
