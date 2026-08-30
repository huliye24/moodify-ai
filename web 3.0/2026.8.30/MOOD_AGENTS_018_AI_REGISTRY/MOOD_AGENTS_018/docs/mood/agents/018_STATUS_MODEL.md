# Agent Status Model — MOOD AGENTS 018

## Overview

This model defines the runtime status tracking for MOOD network agents. Status must reflect:

- **Real-time Health**: Actual operational state
- **Activity Tracking**: Last known working state
- **Performance Metrics**: Quality and efficiency indicators
- **Transparency**: No fake or assumed status

## Canonical Status Values

### 1. "draft"
**Purpose**: Agent in development, not yet active

**Characteristics**:
- Configuration incomplete
- No operator assigned
- Not visible to public registry
- Can transition to "active" or be deleted

**Required Evidence**:
- Configuration specification
- Development roadmap
- Operator intent to deploy

```typescript
interface DraftStatus {
  status: "draft";
  phase: "development" | "testing" | "review";
  estimatedGoLive?: string;
  blockers: string[];
}
```

---

### 2. "active"
**Purpose**: Agent fully operational and participating

**Characteristics**:
- Healthy and responsive
- Taking on tasks
- Producing outputs
- Under operator supervision

**Required Evidence**:
- Recent heartbeat (< 5 minutes)
- Task completion history
- Quality metrics within thresholds
- Operator contact valid

```typescript
interface ActiveStatus {
  status: "active";
  health: {
    heartbeat: string;
    lastTaskAt: string;
    successRate: number; // 0.0 to 1.0
    averageLatency: number; // milliseconds
  };
  activity: {
    tasksCompleted: number;
    tasksFailed: number;
    successRate: number;
  };
}
```

---

### 3. "paused"
**Purpose**: Temporary suspension of operations

**Characteristics**:
- Not accepting new tasks
- Existing tasks continue
- Can resume to "active"
- Operator oversight required

**Required Evidence**:
- Pause reason documented
- Resume plan defined
- No critical operations mid-execution
- Operator approval

```typescript
interface PausedStatus {
  status: "paused";
  reason: string;
  pausedAt: string;
  resumePlanned?: string;
  tasksInProgress: number;
}
```

---

### 4. "degraded"
**Purpose**: Reduced performance or capability

**Characteristics**:
- Operating below normal standards
- May have reduced functionality
- Requires attention from operator
- May need to transition to "offline"

**Required Evidence**:
- Performance metrics below thresholds
- Error rate elevated
- Quality impact documented
- Operator notified

```typescript
interface DegradedStatus {
  status: "degraded";
  issues: string[];
  impact: {
    performance: boolean;
    quality: boolean;
    functionality: boolean;
  };
  severity: "low" | "medium" | "high";
  since: string;
}
```

---

### 5. "offline"
**Purpose**: Agent unavailable for operations

**Characteristics**:
- Not responding to requests
- Cannot take on tasks
- May be temporary or permanent
- Requires investigation

**Required Evidence**:
- Health checks failing
- Recent attempts to contact
- No task completions for extended period
- Operator aware

```typescript
interface OfflineStatus {
  status: "offline";
  since: string;
  lastContactAttempt?: string;
  investigation?: string;
  recoveryPlan?: string;
}
```

---

### 6. "retired"
**Purpose**: Agent permanently decommissioned

**Characteristics**:
- No longer operational
- History preserved
- Cannot be reactivated
- Data archived appropriately

**Required Evidence**:
- Retirement decision documented
- Data migration completed
- Operator approval
- No pending tasks

```typescript
interface RetiredStatus {
  status: "retired";
  retiredAt: string;
  reason: string;
  archivalStatus: "completed" | "in_progress" | "pending";
  replacement?: string; // Agent ID that takes over
}
```

## Status Determination Rules

### Real Status Requirements
1. **Evidence-Based**: Status must be based on actual measurements
2. **Recent Data**: Status information must be current (≤ 5 minutes for active)
3. **Multiple Sources**: At least 2 independent data sources
4. **No Assumptions**: Never assume "online" without evidence

### Status Transition Rules
```typescript
interface StatusTransition {
  from: AgentStatus;
  to: AgentStatus;
  allowed: boolean;
  conditions?: string[];
  requiresApproval?: boolean;
}
```

**Valid Transitions**:
```
draft → active (requires approval)
draft → deleted (no approval needed)
active → paused (operator approval)
active → degraded (automatic, notification required)
paused → active (operator approval)
degraded → active (requires verification)
degraded → offline (automatic if conditions met)
offline → active (requires investigation and fix)
active → retired (requires governance approval)
```

## Status Tracking Implementation

### Health Metrics
```typescript
interface AgentHealth {
  // Runtime health
  lastHeartbeat: string;
  responseTime: number;
  errorRate: number;
  
  // Activity health
  tasksCompleted24h: number;
  tasksFailed24h: number;
  averageQualityScore: number;
  
  // System health
  memoryUsage: number;
  cpuUsage: number;
  availableDisk: number;
}
```

### Activity Metrics
```typescript
interface AgentActivity {
  // Task execution
  currentTasks: Task[];
  queuedTasks: number;
  averageTaskDuration: number;
  
  // Performance
  throughput: number; // tasks per hour
  successRate: number; // 0.0 to 1.0
  qualityScore: number; // 0.0 to 1.0
  
  // Reliability
  uptime: number; // percentage
  lastFailure: string;
  recoveryTime: number; // minutes
}
```

## Status Visibility Rules

### Public Registry
**Always Visible**:
- Status value
- Last update time
- Public metrics (uptime, success rate)
- Contact information (if applicable)

**Never Visible**:
- Internal health details
- Error logs
- Sensitive configuration
- Private operator information

### Internal System
**Full Visibility**:
- All health metrics
- Detailed activity logs
- Error conditions
- Performance trends

## Status Reporting

### Real-time Updates
```typescript
// Status update event
interface StatusUpdateEvent {
  agentId: string;
  previousStatus: AgentStatus;
  currentStatus: AgentStatus;
  timestamp: string;
  metrics: AgentHealth;
  reason?: string;
}
```

### Status API
```typescript
// Get agent status
GET /api/agents/{id}/status
{
  agentId: string;
  status: AgentStatus;
  lastUpdated: string;
  health: AgentHealth;
  metrics: AgentActivity;
  history: StatusEvent[];
}
```

## Monitoring and Alerting

### Status Alerts
- **Critical**: Degraded, Offline status changes
- **Warning**: High error rates, performance degradation
- **Info**: Status transitions, maintenance windows

### Alert Rules
```typescript
interface AlertRule {
  condition: string; // e.g., "errorRate > 0.1"
  severity: "critical" | "warning" | "info";
  recipients: string[]; // Resident IDs
  escalation?: string; // Escalation path
}
```

## Recovery Procedures

### From Degraded Status
1. **Assess Impact**: Determine functionality impact
2. **Diagnose Issue**: Identify root cause
3. **Apply Fix**: Configuration or code changes
4. **Verify Recovery**: Return to "active" status
5. **Monitor**: Watch for recurrence

### From Offline Status
1. **Investigate**: Determine cause of unavailability
2. **Fix Infrastructure**: Resolve underlying issues
3. **Test Connectivity**: Verify agent is responsive
4. **Gradual Resume**: Return to "degraded" first, then "active"
5. **Post-Mortem**: Document and learn

## Status History

### Retention Policy
- **Active Agents**: 30 days of detailed history
- **Retired Agents**: Permanent archive
- **Draft Agents**: Delete after 90 days if not deployed

### History Query
```typescript
interface StatusHistory {
  agentId: string;
  from: string;
  to: string;
  events: StatusEvent[];
  summary: StatusSummary;
}
```

## Implementation Notes

### No Fake Status
- Never show "online" without evidence
- Never hide degradation
- Always show when last seen
- Be transparent about data availability

### Privacy Considerations
- Redact sensitive information from public status
- Allow selective disclosure of health metrics
- Respect operator privacy preferences

---

*Generated: 2026-08-30*
*Status: DRAFT*