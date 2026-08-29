# Moodify Deployment Architecture

This document describes the deployment architecture for Moodify AI Audio Infrastructure.

## System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        User[User/Application]
        Mobile[Mobile App]
        Web[Web Player]
    end

    subgraph "Gateway Layer"
        LB[Load Balancer<br/>Nginx/ALB/SLB]
        CDN[CDN<br/>CloudFront/AliCDN]
    end

    subgraph "API Layer"
        API1[API Service 1]
        API2[API Service 2]
        APIN[API Service N]
    end

    subgraph "Queue Layer"
        Queue[Task Queue<br/>Redis/RabbitMQ]
    end

    subgraph "Worker Layer"
        Worker1[Audio Worker 1]
        Worker2[Audio Worker 2]
        WorkerN[Audio Worker N]
        GPU[GPU Worker<br/>Optional]
    end

    subgraph "Engine Layer"
        MRS[MRS Engine<br/>Moodify Reconstruction]
        Ear[Ear Engine<br/>Auditory Analysis]
        DSP[DSP Engine<br/>Audio Processing]
    end

    subgraph "Storage Layer"
        S3[Object Storage<br/>S3/OSS/COS]
        DB[Database<br/>PostgreSQL]
        Cache[Cache<br/>Redis]
    end

    User --> LB
    Mobile --> CDN
    Web --> CDN
    CDN --> LB
    LB --> API1
    LB --> API2
    LB --> APIN

    API1 --> Queue
    API2 --> Queue
    APIN --> Queue

    Queue --> Worker1
    Queue --> Worker2
    Queue --> WorkerN
    Queue --> GPU

    Worker1 --> MRS
    Worker2 --> Ear
    WorkerN --> DSP
    GPU --> MRS

    MRS --> S3
    Ear --> DB
    DSP --> Cache

    API1 --> DB
    API1 --> Cache
```

## Data Flow

### Audio Analysis Flow

```mermaid
sequenceDiagram
    participant User
    participant API as API Service
    participant Queue as Task Queue
    participant Worker as Audio Worker
    participant Ear as Ear Engine
    participant DB as Database
    participant S3 as Object Storage

    User->>API: Upload Audio File
    API->>S3: Store File
    API->>DB: Create Case Record
    API->>Queue: Submit Analysis Job
    API->>User: Return Job ID

    Worker->>Queue: Poll for Job
    Queue->>Worker: Return Job
    Worker->>S3: Fetch Audio
    Worker->>Ear: Analyze Audio
    Ear->>Worker: Return Features
    Worker->>S3: Store Results
    Worker->>DB: Update Case Status
    Worker->>Queue: Acknowledge Job

    User->>API: Query Results (Job ID)
    API->>DB: Fetch Case
    API->>S3: Fetch Results
    API->>User: Return Analysis
```

### Audio Processing Flow

```mermaid
sequenceDiagram
    participant User
    participant API as API Service
    participant Queue as Task Queue
    participant Worker as Audio Worker
    participant MRS as MRS Engine
    participant DSP as DSP Engine
    participant S3 as Object Storage

    User->>API: Submit Processing Request
    API->>Queue: Submit Processing Job
    API->>User: Return Job ID

    Worker->>Queue: Poll for Job
    Queue->>Worker: Return Job
    Worker->>S3: Fetch Source Audio
    Worker->>MRS: Reconstruct Audio
    MRS->>Worker: Return Reconstructed
    Worker->>DSP: Apply Post-processing
    DSP->>Worker: Return Processed
    Worker->>S3: Store Output
    Worker->>Queue: Acknowledge Job

    User->>API: Download Result
    API->>S3: Fetch Processed Audio
    API->>User: Return Audio File
```

## Component Details

### API Service

**Responsibilities**:
- Receive HTTP requests
- Authenticate users
- Validate inputs
- Queue tasks
- Return results

**Scaling**: Horizontal (2-20 instances)

**Endpoints**:
- `/health` - Health check
- `/api/v1/analyze` - Audio analysis
- `/api/v1/process` - Audio processing
- `/api/v1/cases/{id}` - Case status

### Task Queue

**Responsibilities**:
- Decouple API from workers
- Ensure task durability
- Enable retry logic
- Support priorities

**Options**: Redis, RabbitMQ, SQS

**Queues**:
- `audio:analysis` - High priority
- `audio:processing` - Normal priority
- `audio:batch` - Low priority

### Audio Worker

**Responsibilities**:
- Poll queue for tasks
- Process audio files
- Call MRS/Ear/DSP engines
- Store results

**Scaling**: Horizontal (2-50 instances)

**Instance Types**:
- Standard: 4 CPU, 8GB RAM
- GPU: 8 CPU, 32GB RAM, NVIDIA T4

### MRS Engine

**Responsibilities**:
- Moodify Reconstruction Score
- Audio quality assessment
- Feature extraction

**Input**: Audio file
**Output**: MRS scores and features

### Ear Engine

**Responsibilities**:
- Auditory analysis
- Temporal texture analysis
- Multi-scale representation

**Input**: Audio file
**Output**: Auditory features

### DSP Engine

**Responsibilities**:
- Audio processing
- Effects application
- Format conversion

**Input**: Audio file + parameters
**Output**: Processed audio

## Network Architecture

```mermaid
graph TB
    subgraph "Internet"
        Users[Users]
    end

    subgraph "VPC / Virtual Network"
        subgraph "Public Subnet"
            LB[Load Balancer]
            NAT[NAT Gateway]
        end

        subgraph "Private Subnet - API"
            API1[API 1]
            API2[API 2]
        end

        subgraph "Private Subnet - Workers"
            W1[Worker 1]
            W2[Worker 2]
            WN[Worker N]
        end

        subgraph "Private Subnet - Data"
            DB[PostgreSQL]
            Cache[Redis]
        end
    end

    subgraph "Managed Services"
        S3[Object Storage]
    end

    Users --> LB
    LB --> API1
    LB --> API2

    API1 --> Cache
    API2 --> Cache
    API1 --> DB
    API2 --> DB

    API1 --> W1
    API2 --> W2

    W1 --> S3
    W2 --> S3
    WN --> S3

    W1 --> NAT
    W2 --> NAT
    WN --> NAT
```

## Deployment Patterns

### Single Region

```mermaid
graph TB
    subgraph "Region: us-east-1"
        LB[Load Balancer]
        API[API Service]
        Worker[Worker Pool]
        DB[(Database)]
        S3[(Object Storage)]
    end

    User --> LB
    LB --> API
    API --> Worker
    API --> DB
    Worker --> S3
```

### Multi-Region (Future)

```mermaid
graph TB
    subgraph "Region: US East"
        LB1[Load Balancer]
        API1[API Service]
        Worker1[Worker Pool]
        DB1[(Database)]
    end

    subgraph "Region: Asia Pacific"
        LB2[Load Balancer]
        API2[API Service]
        Worker2[Worker Pool]
        DB2[(Database)]
    end

    subgraph "Global"
        DNS[DNS / Geo-Routing]
        S3[(Object Storage<br/>Cross-Region)]
    end

    User --> DNS
    DNS --> LB1
    DNS --> LB2
    LB1 --> API1
    LB2 --> API2
    API1 --> Worker1
    API2 --> Worker2
    Worker1 --> S3
    Worker2 --> S3
```

## Scaling Strategy

### Horizontal Scaling

```mermaid
graph LR
    subgraph "Low Load"
        A1[API 1]
        W1[Worker 1]
    end

    subgraph "Medium Load"
        A1
        A2[API 2]
        W1
        W2[Worker 2]
        W3[Worker 3]
    end

    subgraph "High Load"
        A1
        A2
        A3[API 3]
        W1
        W2
        W3
        W4[Worker 4]
        W5[Worker 5]
    end

    Low --> Medium --> High
```

### Auto-scaling Triggers

| Metric | Scale Up | Scale Down |
|--------|----------|------------|
| API CPU | > 70% | < 30% |
| API Latency | > 500ms | < 200ms |
| Queue Depth | > 100 | < 10 |
| Worker Utilization | > 80% | < 40% |

## Security Architecture

```mermaid
graph TB
    subgraph "Security Layers"
        WAF[Web Application Firewall]
        Auth[Authentication]
        Encrypt[Encryption]
        Network[Network Security]
    end

    subgraph "Data Protection"
        TLS[TLS 1.3 in Transit]
        AES[AES-256 at Rest]
        KeyMgmt[Key Management]
    end

    subgraph "Access Control"
        IAM[IAM Roles]
        APIKey[API Keys]
        JWT[JWT Tokens]
    end

    User --> WAF
    WAF --> Auth
    Auth --> Encrypt
    Encrypt --> Network

    Network --> TLS
    TLS --> AES
    AES --> KeyMgmt

    Auth --> IAM
    Auth --> APIKey
    Auth --> JWT
```

## Monitoring Architecture

```mermaid
graph TB
    subgraph "Metrics Collection"
        Prom[Prometheus]
        Logs[Log Aggregator]
        Traces[Distributed Tracing]
    end

    subgraph "Visualization"
        Grafana[Grafana Dashboards]
        Alerts[Alert Manager]
    end

    subgraph "Notifications"
        Slack[Slack]
        Email[Email]
        PagerDuty[PagerDuty]
    end

    API[API Service] --> Prom
    Worker[Audio Worker] --> Prom
    Queue[Task Queue] --> Prom

    API --> Logs
    Worker --> Logs

    Prom --> Grafana
    Logs --> Grafana
    Traces --> Grafana

    Grafana --> Alerts
    Alerts --> Slack
    Alerts --> Email
    Alerts --> PagerDuty
```

## Technology Stack

| Layer | Technology | Alternatives |
|-------|------------|--------------|
| Container | Docker | containerd |
| Orchestration | Docker Compose | Kubernetes |
| API Framework | FastAPI | Flask, Django |
| Queue | Redis | RabbitMQ, SQS |
| Database | PostgreSQL | MySQL, RDS |
| Storage | MinIO | S3, OSS, COS |
| Monitoring | Prometheus | Datadog, CloudWatch |
| Visualization | Grafana | Kibana, CloudWatch |
| Load Balancer | Nginx | Traefik, ALB |

## References

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [AWS Well-Architected](https://aws.amazon.com/architecture/well-architected/)
