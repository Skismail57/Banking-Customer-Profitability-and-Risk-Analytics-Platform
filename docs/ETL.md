# ETL Framework Documentation

## Overview

The ETL (Extract, Transform, Load) framework provides a configurable, reproducible pipeline for ingesting data from various sources into the banking analytics warehouse. The framework follows a staged architecture: RAW → STAGING → CLEAN → WAREHOUSE.

---

## Architecture

### Pipeline Stages

```
┌─────────────┐
│   SOURCE    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  EXTRACT    │ → RAW Storage (immutable)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ TRANSFORM   │ → STAGING (validated)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   CLEAN     │ → Cleaned data
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   LOAD      │ → WAREHOUSE (database)
└─────────────┘
```

### Storage Layers

- **RAW**: Immutable raw data as ingested from sources
- **STAGING**: Validated and transformed data ready for cleaning
- **WAREHOUSE**: Final data loaded into PostgreSQL database

---

## Components

### 1. Base Framework (`src/ingestion/base.py`)

#### IngestionMetadata
Dataclass that tracks all metadata for ingestion operations:

**Fields**:
- `source_name`: Name of the data source
- `source_type`: Type (csv, parquet, etc.)
- `source_path`: Path to source file
- `ingestion_timestamp`: When ingestion occurred
- `ingestion_id`: Unique ingestion identifier
- `row_count`: Number of rows ingested
- `column_count`: Number of columns
- `file_size_bytes`: Source file size
- `null_count`: Total null values
- `duplicate_count`: Number of duplicate rows
- `error_count`: Number of errors encountered
- `schema_hash`: Hash of DataFrame schema
- `data_hash`: Hash of DataFrame content
- `status`: success, partial_success, or failed
- `target_path`: Where data was loaded
- `target_table`: Target database table
- `metadata`: Additional custom metadata

**Methods**:
- `to_dict()`: Convert to dictionary
- `to_json()`: Convert to JSON string
- `from_dict()`: Create from dictionary
- `generate_ingestion_id()`: Generate unique ID
- `compute_schema_hash()`: Hash schema for change detection
- `compute_data_hash()`: Hash data for change detection

#### BaseExtractor
Abstract base class for data extractors.

**Methods**:
- `extract()`: Extract data from source (abstract)
- `get_file_size()`: Get source file size
- `validate_source()`: Validate source exists and is accessible

#### BaseLoader
Abstract base class for data loaders.

**Methods**:
- `load()`: Load data to storage (abstract)
- `ensure_directory()`: Ensure output directory exists
- `get_output_path()`: Generate output file path

#### Exceptions
- `IngestionError`: Base exception for ingestion errors
- `SourceValidationError`: Source validation failed
- `DataQualityError`: Data quality checks failed
- `LoadError`: Loading operation failed

---

### 2. Extractors (`src/ingestion/extractors.py`)

#### CSVExtractor
Extracts data from CSV files.

**Configuration**:
```yaml
type: csv
path: /path/to/file.csv
delimiter: ","
encoding: utf-8
has_header: true
```

**Features**:
- Custom delimiter support
- Encoding support
- Header/no-header support
- Automatic metadata generation

#### ParquetExtractor
Extracts data from Parquet files.

**Configuration**:
```yaml
type: parquet
path: /path/to/file.parquet
engine: pyarrow  # or fastparquet
```

**Features**:
- Efficient columnar format
- Preserves data types
- Automatic metadata generation

#### ExtractorFactory
Factory pattern for creating extractors based on source type.

**Usage**:
```python
from src.ingestion.extractors import ExtractorFactory

extractor = ExtractorFactory.create_extractor(source_config)
df = extractor.extract()
```

---

### 3. Schema Detection (`src/ingestion/schema.py`)

#### SchemaDetector
Analyzes DataFrame schema and structure.

**Methods**:
- `detect_schema()`: Detect complete schema (columns, types, nulls, uniques)
- `infer_column_type()`: Infer semantic type (numeric, datetime, categorical, etc.)
- `detect_key_candidates()`: Detect potential primary and foreign keys

**Output Example**:
```python
{
    "columns": ["col1", "col2", "col3"],
    "dtypes": {"col1": "int64", "col2": "object"},
    "null_counts": {"col1": 0, "col2": 5},
    "null_percentages": {"col1": 0.0, "col2": 0.1},
    "unique_counts": {"col1": 100, "col2": 50},
    "sample_values": {"col1": [1, 2, 3], "col2": ["a", "b", "c"]}
}
```

#### SchemaValidator
Validates DataFrame against expected schema.

**Configuration**:
```python
{
    "required_columns": ["col1", "col2"],
    "column_types": {"col1": "int64"},
    "nullable": {"col1": False}
}
```

**Methods**:
- `validate()`: Validate DataFrame, returns (is_valid, errors)

#### DataQualityChecker
Performs data quality checks.

**Configuration**:
```yaml
data_quality:
  min_row_count: 1
  max_null_percentage: 0.95
  handle_duplicates: true
```

**Checks**:
- Minimum row count
- Maximum null percentage per column
- Duplicate detection
- Returns detailed quality report

---

### 4. Loaders (`src/ingestion/loaders.py`)

#### RawLoader
Loads data to RAW storage (immutable).

**Features**:
- Compresses output (gzip)
- Organizes by date hierarchy: `raw/source/YYYY/MM/DD/source_HHMMSS.csv.gz`
- Saves metadata alongside data
- Immutable - never overwrites

#### StagingLoader
Loads data to STAGING storage.

**Features**:
- Saves as Parquet for efficiency
- Organized by date hierarchy
- Ready for transformation and cleaning

#### WarehouseLoader
Loads data to warehouse database.

**Features**:
- Loads to PostgreSQL via SQLAlchemy
- Batch loading with chunking
- Transaction support
- Error handling and rollback

---

### 5. Cleaners (`src/ingestion/cleaners.py`)

#### DataCleaner
Cleans and standardizes data.

**Configuration**:
```yaml
handle_duplicates: true
duplicate_strategy: keep_first  # keep_first, keep_last, drop_all
trim_strings: true
standardize_dates: true
fill_numeric: 0
fill_string: "unknown"
```

**Operations**:
- **Duplicate handling**: Remove or keep duplicates based on strategy
- **String trimming**: Remove leading/trailing whitespace
- **Date standardization**: Convert date-like columns to datetime
- **Null filling**: Fill null values with specified defaults
- **Empty row removal**: Remove rows with all null values

#### DataTransformer
Transforms data to match target schema.

**Configuration**:
```python
{
    "column_mappings": {"old_name": "new_name"},
    "target_columns": ["col1", "col2"],
    "column_types": {"col1": "int"},
    "derived_columns": {"total": lambda df: df["a"] + df["b"]}
}
```

**Operations**:
- **Column renaming**: Map source columns to target names
- **Column selection**: Keep only target columns
- **Type conversion**: Convert columns to target types
- **Derived columns**: Add computed columns

---

### 6. Orchestrator (`src/ingestion/orchestrator.py`)

#### IngestionOrchestrator
Manages end-to-end ingestion pipeline.

**Usage**:
```python
from src.ingestion.orchestrator import IngestionOrchestrator

orchestrator = IngestionOrchestrator("config/ingestion.yaml")

# Ingest single source
result = orchestrator.run_source_ingestion("customers")

# Ingest all sources
result = orchestrator.run_all_sources()

# Get pipeline summary
summary = orchestrator.get_pipeline_summary()
```

**Pipeline Stages**:
1. **Extract**: Load from source to RAW storage
2. **Transform**: Validate and load to STAGING
3. **Clean**: Apply cleaning operations
4. **Warehouse**: Load to database (optional)

**Result Structure**:
```python
{
    "source": "customers",
    "start_time": "2024-01-15T10:00:00",
    "end_time": "2024-01-15T10:05:00",
    "status": "success",
    "stages": {
        "raw": {"status": "success", "row_count": 1000, "output_path": "..."},
        "staging": {"status": "success", "quality_report": {...}},
        "clean": {"status": "success", "rows_removed": 5},
        "warehouse": {"status": "success", "table_name": "dim_customer"}
    },
    "final_row_count": 995
}
```

---

## Configuration

### Ingestion Configuration (`config/ingestion.yaml`)

```yaml
# Source configurations
sources:
  customers:
    type: csv
    path: data/input/customers.csv
    delimiter: ","
    encoding: utf-8
    has_header: true
    target_table: dim_customer
    natural_key: customer_id
    load_to_warehouse: true

# Data quality rules
data_quality:
  min_row_count: 1
  max_null_percentage: 0.95
  handle_duplicates: true
  duplicate_strategy: keep_first
  validate_schema: true

# Pipeline settings
pipeline:
  batch_size: 10000
  parallel_workers: 4
  max_retries: 3
  retry_delay_seconds: 5
  compress_raw: true
  compression_type: gzip

# Storage paths
storage:
  raw: data/raw
  staging: data/staging
  warehouse: data/warehouse
  metadata: data/metadata
```

---

## Metadata Tracking

### Metadata File Format
Each ingestion creates a metadata JSON file alongside the data:

```json
{
  "source_name": "customers",
  "source_type": "csv",
  "source_path": "data/input/customers.csv",
  "ingestion_timestamp": "2024-01-15T10:00:00",
  "ingestion_id": "ing_20240115100000_abc123",
  "row_count": 1000,
  "column_count": 15,
  "file_size_bytes": 512000,
  "null_count": 50,
  "duplicate_count": 5,
  "schema_hash": "abc123...",
  "data_hash": "def456...",
  "status": "success",
  "target_path": "data/raw/customers/2024/01/15/customers_100000.csv.gz"
}
```

### Metadata Storage
- **RAW**: Metadata stored alongside data files
- **STAGING**: Metadata tracked in orchestrator results
- **WAREHOUSE**: Metadata logged to database

---

## Error Handling

### Retry Logic
Configurable retry for transient failures:

```yaml
pipeline:
  max_retries: 3
  retry_delay_seconds: 5
```

### Error Propagation
- **Source validation errors**: Fail fast, don't proceed
- **Data quality errors**: Log warning, continue with partial success
- **Load errors**: Rollback transaction, log error

### Error Reporting
All errors include:
- Error message
- Stage where error occurred
- Timestamp
- Context (source, row count, etc.)

---

## Logging

### Log Levels
- **DEBUG**: Detailed diagnostic information
- **INFO**: Normal pipeline progress
- **WARNING**: Data quality issues, non-critical errors
- **ERROR**: Failures that stop pipeline
- **CRITICAL**: Critical system errors

### Log Format
Structured logging with context:
```json
{
  "event": "Data extraction completed",
  "level": "info",
  "timestamp": "2024-01-15T10:00:00Z",
  "source": "customers",
  "row_count": 1000,
  "duration_seconds": 5.2
}
```

### Log Locations
- **File**: `logs/ingestion.log`
- **Console**: Configurable
- **Database**: Optional for production

---

## Reproducibility

### Deterministic Behavior
- Same input produces same output
- No random operations in pipeline
- Configuration-driven behavior

### Version Control
- All configuration in version control
- Migration scripts versioned
- Data lineage tracked via metadata

### Audit Trail
- Every ingestion has unique ID
- All operations logged
- Metadata preserved for audit

---

## Performance Considerations

### Batch Processing
```yaml
pipeline:
  batch_size: 10000
```
Process data in batches for memory efficiency.

### Parallel Processing
```yaml
pipeline:
  parallel_workers: 4
```
Use multiple workers for independent sources.

### Compression
```yaml
pipeline:
  compress_raw: true
  compression_type: gzip
```
Compress raw data to save storage.

### Efficient Formats
- **RAW**: CSV with gzip compression
- **STAGING**: Parquet (columnar, efficient)
- **WAREHOUSE**: Database with proper indexing

---

## Testing

### Unit Tests
Located in `tests/unit/ingestion/`:

- `test_base.py`: Base classes and metadata
- `test_extractors.py`: CSV and Parquet extractors
- `test_cleaners.py`: Data cleaning and transformation
- `test_schema.py`: Schema detection and validation

### Running Tests
```bash
pytest tests/unit/ingestion/
pytest tests/unit/ingestion/test_extractors.py -v
```

### Test Coverage
- Extractor: Source validation, data extraction
- Cleaners: Duplicate handling, type conversion
- Schema: Detection, validation, quality checks
- Metadata: Serialization, hash computation

---

## Best Practices

### 1. Configuration
- Keep all configuration in YAML files
- Use environment variables for secrets
- Document configuration options

### 2. Data Quality
- Always validate before loading
- Set appropriate quality thresholds
- Review quality reports regularly

### 3. Error Handling
- Implement retry for transient failures
- Log all errors with context
- Don't silently ignore errors

### 4. Metadata
- Always generate metadata
- Preserve metadata for audit
- Use hashes for change detection

### 5. Testing
- Write unit tests for all components
- Test error conditions
- Use fixtures for test data

### 6. Performance
- Use appropriate batch sizes
- Compress large datasets
- Monitor pipeline execution time

---

## Example Usage

### Simple Ingestion
```python
from src.ingestion.orchestrator import IngestionOrchestrator

# Initialize orchestrator
orchestrator = IngestionOrchestrator("config/ingestion.yaml")

# Ingest single source
result = orchestrator.run_source_ingestion("customers")

print(f"Status: {result['status']}")
print(f"Rows: {result['final_row_count']}")
```

### Batch Ingestion
```python
# Ingest all configured sources
result = orchestrator.run_all_sources()

print(f"Total: {result['summary']['total']}")
print(f"Successful: {result['summary']['successful']}")
print(f"Failed: {result['summary']['failed']}")
```

### Custom Cleaning
```python
from src.ingestion.cleaners import DataCleaner

config = {
    "handle_duplicates": True,
    "duplicate_strategy": "keep_first",
    "trim_strings": True,
    "fill_numeric": 0
}

cleaner = DataCleaner(config)
df_cleaned = cleaner.clean(df)
```

### Schema Validation
```python
from src.ingestion.schema import SchemaValidator

schema = {
    "required_columns": ["customer_id", "name"],
    "column_types": {"customer_id": "int64"},
    "nullable": {"customer_id": False}
}

validator = SchemaValidator(schema)
is_valid, errors = validator.validate(df)
```

---

## Troubleshooting

### Common Issues

**Issue**: Source file not found
- **Solution**: Check path in configuration, verify file exists

**Issue**: Data quality checks failing
- **Solution**: Review quality report, adjust thresholds or fix source data

**Issue**: Type conversion errors
- **Solution**: Check column types in source, update schema configuration

**Issue**: Database connection errors
- **Solution**: Verify database credentials, check connection string

**Issue**: Out of memory errors
- **Solution**: Reduce batch size, process in smaller chunks

---

## Future Enhancements

- **Additional formats**: JSON, Excel, database sources
- **Incremental loading**: Load only new/changed data
- **Parallel processing**: Multi-threaded extraction
- **Data profiling**: Advanced data quality metrics
- **Lineage tracking**: Full data lineage graph
- **Monitoring**: Real-time pipeline monitoring
- **Alerting**: Automated alerts on failures
