# Moodify Data Architecture

## Overview

This document describes the future data architecture for Moodify.

**Status**: Design Phase - Implementation Planned

## Data Architecture Vision

```
┌─────────────────────────────────────────────────────────────┐
│                    Data Ingestion Layer                      │
│              (Upload, Import, Integration)                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Audio Storage Layer                      │
│              (Raw Audio, Processed Audio)                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Feature Database                         │
│         (Extracted Features, Embeddings)                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Evaluation Database                      │
│              (MRS Scores, Analysis Results)                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Preference Dataset                       │
│           (Human Ratings, Preference Data)                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              Auditory Intelligence Data Layer                │
│         (Aggregated Insights, Model Training)              │
└─────────────────────────────────────────────────────────────┘
```

## Data Layers

### 1. Audio Storage Layer

**Purpose**: Store audio files

**Data Types**:
| Type | Format | Retention | Size |
|------|--------|-----------|------|
| Raw Upload | Original format | 7 days | ~50MB/file |
| Processed | WAV/FLAC | 30 days | ~100MB/file |
| Reference | Lossless | Permanent | Varies |
| Cache | Compressed | 24 hours | ~10MB/file |

**Storage Structure**:
```
audio-storage/
├── uploads/
│   └── {date}/
│       └── {user_id}/
│           └── {file_id}.ext
├── processed/
│   └── {case_id}/
│       ├── source.wav
│       └── processed.wav
├── reference/
│   └── {dataset}/
│       └── {file_id}.flac
└── cache/
    └── {hash}.tmp
```

**Technology Options**:
- AWS S3
- Alibaba Cloud OSS
- Tencent Cloud COS
- MinIO (self-hosted)

### 2. Feature Database

**Purpose**: Store extracted audio features

**Schema**:
```sql
CREATE TABLE audio_features (
    id UUID PRIMARY KEY,
    audio_id UUID REFERENCES audio_files(id),
    extracted_at TIMESTAMP,
    
    -- Temporal features
    duration FLOAT,
    sample_rate INTEGER,
    
    -- Spectral features
    spectral_centroid FLOAT[],
    spectral_rolloff FLOAT[],
    spectral_bandwidth FLOAT[],
    
    -- Temporal texture
    zero_crossing_rate FLOAT[],
    rms_energy FLOAT[],
    
    -- Embeddings
    embedding VECTOR(512),  -- Future: pgvector
    
    -- Metadata
    version VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Technology**: PostgreSQL with pgvector extension (future)

**Retention**: Permanent (aggregated, anonymized)

### 3. Evaluation Database

**Purpose**: Store MRS scores and analysis results

**Schema**:
```sql
CREATE TABLE evaluations (
    id UUID PRIMARY KEY,
    case_id UUID REFERENCES cases(id),
    
    -- MRS Scores
    mrs_overall FLOAT,
    mrs_fidelity FLOAT,
    mrs_balance FLOAT,
    mrs_clarity FLOAT,
    
    -- Technical metrics
    loudness_lufs FLOAT,
    true_peak_db FLOAT,
    dynamic_range_db FLOAT,
    
    -- Analysis metadata
    algorithm_version VARCHAR(20),
    processing_time_ms INTEGER,
    
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Technology**: PostgreSQL

**Retention**: 90 days (user data), permanent (aggregated)

### 4. Preference Dataset

**Purpose**: Store human ratings and preferences

**Schema**:
```sql
CREATE TABLE preferences (
    id UUID PRIMARY KEY,
    
    -- Reference
    audio_a_id UUID,
    audio_b_id UUID,
    
    -- Rating
    user_id UUID,  -- Anonymized
    preference INTEGER,  -- -1, 0, 1
    confidence INTEGER,  -- 1-5
    
    -- Context
    listening_environment VARCHAR(50),
    device_type VARCHAR(50),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    anonymized BOOLEAN DEFAULT FALSE
);
```

**Technology**: PostgreSQL

**Retention**: Anonymized after 90 days

### 5. Auditory Intelligence Data Layer

**Purpose**: Aggregated insights for model training

**Data Products**:

| Product | Description | Update Frequency |
|---------|-------------|------------------|
| Quality Benchmarks | Aggregated quality scores | Daily |
| Genre Profiles | Per-genre feature distributions | Weekly |
| User Preferences | Anonymized preference patterns | Monthly |
| Model Training Sets | Curated datasets for training | Quarterly |

**Structure**:
```
intelligence-layer/
├── benchmarks/
│   └── {date}_benchmark.parquet
├── profiles/
│   └── {genre}_profile.json
├── preferences/
│   └── {month}_preferences.parquet
└── training/
    └── {quarter}_dataset/
        ├── metadata.json
        └── features.parquet
```

## Data Flow

### Ingestion Flow

```
User Upload
    ↓
API Gateway
    ↓
Validation
    ↓
Audio Storage (Raw)
    ↓
Processing Queue
    ↓
Feature Extraction
    ↓
Feature Database
    ↓
Evaluation Engine
    ↓
Evaluation Database
    ↓
Result Cache
    ↓
User Access
```

### Analysis Flow

```
Audio File
    ↓
Preprocessing
    ↓
┌─────────────────┐
│ Feature Extract │
│ - Spectral      │
│ - Temporal      │
│ - Embeddings    │
└─────────────────┘
    ↓
Feature Database
    ↓
┌─────────────────┐
│ MRS Engine      │
│ - Scoring       │
│ - Assessment    │
└─────────────────┘
    ↓
Evaluation Database
    ↓
Result Aggregation
    ↓
User Response
```

## Data Governance

### Data Quality

| Dimension | Metric | Target |
|-----------|--------|--------|
| Completeness | % fields populated | > 95% |
| Accuracy | Error rate | < 1% |
| Consistency | Cross-system match | > 99% |
| Timeliness | Processing latency | < 5s |
| Validity | Schema compliance | 100% |

### Data Lineage

**Tracking**:
- Source system
- Transformation steps
- Destination
- Timestamp
- Version

**Example**:
```json
{
  "lineage_id": "uuid",
  "source": "user_upload",
  "transformations": [
    {"step": "validation", "timestamp": "..."},
    {"step": "feature_extraction", "timestamp": "..."},
    {"step": "scoring", "timestamp": "..."}
  ],
  "destination": "evaluation_db",
  "version": "1.0.0"
}
```

### Data Retention

| Data Type | Retention | Archive | Delete |
|-----------|-----------|---------|--------|
| Raw Audio | 7 days | No | Auto |
| Features | 90 days | Yes | User request |
| Evaluations | 90 days | Yes | User request |
| Preferences | 90 days | Anonymized | Auto |
| Audit Logs | 1 year | Yes | Auto |
| Aggregated | Permanent | N/A | N/A |

### Data Access

| Role | Read | Write | Delete |
|------|------|-------|--------|
| User | Own data | Own data | Own data |
| Admin | All | Config | No |
| Analyst | Anonymized | No | No |
| Service | API only | API only | No |

## Data Security

### Encryption

| Layer | Method | Status |
|-------|--------|--------|
| In Transit | TLS 1.3 | Planned |
| At Rest | AES-256 | Planned |
| Database | TDE | Planned |
| Backups | AES-256 | Planned |

### Access Control

- Role-based access
- Row-level security
- Column-level encryption (sensitive)
- Audit logging

### Data Masking

| Data Type | Masking | Purpose |
|-----------|---------|---------|
| User ID | Hash | Analytics |
| Audio Content | N/A | Never logged |
| File Names | Hash | Analytics |
| IP Addresses | Anonymize | Analytics |

## Data Integration

### External Sources

| Source | Type | Purpose | Status |
|--------|------|---------|--------|
| User Uploads | Audio | Analysis | Current |
| Public Datasets | Audio | Benchmarking | Planned |
| Partner APIs | Metadata | Enrichment | Future |
| Streaming Services | Reference | Comparison | Future |

### Export Formats

| Format | Use Case | Status |
|--------|----------|--------|
| JSON | API responses | Current |
| CSV | Bulk export | Planned |
| Parquet | Analytics | Planned |
| ONNX | Model export | Future |

## Scalability

### Volume Projections

| Metric | Year 1 | Year 2 | Year 3 |
|--------|--------|--------|--------|
| Audio Files | 1M | 10M | 50M |
| Feature Records | 10M | 100M | 500M |
| Evaluation Records | 5M | 50M | 250M |
| Storage (TB) | 10 | 100 | 500 |

### Scaling Strategy

| Layer | Strategy |
|-------|----------|
| Audio Storage | Horizontal (sharding by date) |
| Features | Partitioning by time |
| Evaluations | Partitioning by user |
| Preferences | Aggregation and archival |

## Technology Stack

| Component | Primary | Alternative |
|-----------|---------|-------------|
| Object Storage | S3 | OSS, COS, MinIO |
| Database | PostgreSQL | MySQL, RDS |
| Vector DB | pgvector | Pinecone, Milvus |
| Cache | Redis | Memcached |
| Data Lake | S3 + Athena | OSS + MaxCompute |
| ETL | Airflow | Dagster |
| Analytics | Metabase | Superset |

## Future Enhancements

### Phase 1: Foundation
- [ ] Core database schema
- [ ] Object storage integration
- [ ] Basic data pipeline

### Phase 2: Scale
- [ ] Partitioning strategy
- [ ] Data warehouse
- [ ] Analytics platform

### Phase 3: Intelligence
- [ ] Feature store
- [ ] Model registry
- [ ] A/B testing framework

### Phase 4: Enterprise
- [ ] Data marketplace
- [ ] Federated learning
- [ ] Privacy-preserving analytics

## Data Assets

### Core Assets

| Asset | Description | Value |
|-------|-------------|-------|
| Audio Collection | Processed audio corpus | Training data |
| Feature Library | Extracted features | Analysis input |
| Quality Benchmarks | MRS score distributions | Quality reference |
| Preference Data | Human ratings | Model validation |

### Derived Assets

| Asset | Description | Use |
|-------|-------------|-----|
| Genre Profiles | Per-genre characteristics | Classification |
| Quality Models | Trained MRS models | Scoring |
| Recommendation Engine | Preference patterns | Suggestions |

## References

- [Data Mesh Principles](https://martinfowler.com/articles/data-mesh-principles.html)
- [Lakehouse Architecture](https://databricks.com/blog/2020/01/30/what-is-a-data-lakehouse.html)
- [PostgreSQL Partitioning](https://www.postgresql.org/docs/current/ddl-partitioning.html)

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-08-23 | Initial data architecture |
