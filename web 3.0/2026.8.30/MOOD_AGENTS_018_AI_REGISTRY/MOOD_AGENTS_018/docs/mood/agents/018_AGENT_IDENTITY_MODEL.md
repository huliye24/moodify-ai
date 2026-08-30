# Agent Identity Model — MOOD AGENTS 018

## Core Principles

### 1. Identity Separation
- **Agent Identity**: Stable, persistent identifier independent of implementation
- **Runtime Implementation**: Can change without affecting identity
- **Operator Link**: Clear human accountability chain

### 2. Decoupling Requirements
- **Provider Decoupled**: Identity doesn't depend on model provider
- **Key Decoupled**: Not tied to specific API keys
- **Version Independent**: Can track version history

## Canonical Agent Identity Types

### Recommended Format: `type_slug_version`
```text
agent_listener_001      # First audio listener agent
agent_curator_001       # First content curator agent
agent_auditor_001       # First proof verification agent
```

### Alternative: UUID + Slug
```typescript
{
  id: "550e8400-e29b-41d4-a716-446655440000",
  slug: "audio-analyzer",
}
```

## Identity Components

### AgentIdentity (Core)
```typescript
type AgentIdentity = {
  // Stable identifiers
  id: string;                    // Unique immutable ID
  slug: string;                   // Human-readable identifier
  name: string;                   // Public display name
  
  // Accountability
  operatorResidentId?: string;    // Human operator (if applicable)
  operatorOrganizationId?: string; // Organization operator
  
  // Status tracking
  status: AgentStatus;
  public: boolean;               // Whether identity is public
  
  // Audit trail
  createdAt: string;
  updatedAt: string;
};
```

### AgentRuntime (Implementation)
```typescript
type AgentRuntime = {
  runtimeType: string;           // "openai", "claude", "local", "hybrid"
  modelProvider?: string;       // "openai", "anthropic", "custom"
  modelName?: string;           // "gpt-4", "claude-3", "custom-v1"
  version?: string;             // Implementation version
  endpoint?: string;            // Runtime-specific endpoint
  config?: Record<string, any>;  // Runtime configuration
};
```

## Identity Lifecycle

### 1. Agent Registration
```typescript
// Create new agent identity
const agentId = await registry.registerAgent({
  slug: "audio-analyzer",
  name: "Audio Analysis Agent",
  operatorResidentId: "resident_123", // Optional human operator
  public: true,
});
```

### 2. Runtime Assignment
```typescript
// Assign runtime to existing identity
await registry.assignRuntime(agentId, {
  runtimeType: "openai",
  modelProvider: "openai",
  modelName: "gpt-4-turbo",
  version: "1.0.0",
});
```

### 3. Version Management
```typescript
// Create new version of same agent
const agentIdV2 = await registry.createVersion(agentId, {
  name: "Audio Analysis Agent v2",
  runtime: { /* new runtime config */ },
});
```

## Identity Constraints

### Forbidden Patterns
```text
// Never use:
auto-generated-12345          # Non-human-meaningful
wallet_0xabc...               # Tied to financial addresses
model_gpt_4                   # Tied to specific model
random_uuid                   # No semantic meaning
```

### Required Properties
1. **Human-meaningful slug**
2. **Stable ID** (never changes for same agent)
3. **Clear operator** (human or organization)
4. **Privacy boundary** (public/private status)

## Agent Identity Registry

### Registry Contract
```typescript
interface AgentRegistry {
  // Identity management
  registerAgent(data: AgentRegistration): Promise<AgentIdentity>;
  getAgent(id: string): Promise<AgentIdentity>;
  updateAgent(id: string, data: AgentUpdate): Promise<AgentIdentity>;
  
  // Runtime management
  assignRuntime(agentId: string, runtime: AgentRuntime): Promise<void>;
  updateRuntime(agentId: string, runtime: AgentRuntime): Promise<void>;
  
  // Versioning
  createVersion(agentId: string, data: AgentVersion): Promise<AgentIdentity>;
  getVersionHistory(agentId: string): Promise<AgentIdentity[]>;
}
```

### Registration Validation
```typescript
function validateAgentRegistration(data: AgentRegistration): boolean {
  // Required fields
  if (!data.slug || !data.name) return false;
  
  // Slug format: letters, numbers, hyphens only
  if (!/^[a-z][a-z0-9-]*$/.test(data.slug)) return false;
  
  // Must have operator (human or org)
  if (!data.operatorResidentId && !data.operatorOrganizationId) return false;
  
  return true;
}
```

## Integration with Network Identity

### Operator Relationship
```typescript
// Agent operated by human resident
{
  agentId: "agent_listener_001",
  operator: {
    type: "resident",
    residentId: "resident_audio_expert_001",
    role: "Audio Engineering Lead"
  }
}

// Agent operated by organization
{
  agentId: "agent_curator_001",
  operator: {
    type: "organization",
    organizationId: "org_moodify_audio",
    role: "Content Curation Team"
  }
}
```

### Accountability Records
```typescript
interface AccountabilityLog {
  agentId: string;
  action: string;           // "runtime_update", "operator_change"
  operatorId: string;
  timestamp: string;
  reason?: string;          // Human-readable reason
  approval?: {              // If approval required
    approvedBy: string;
    approvedAt: string;
  }
}
```

## Security Model

### Identity Protection
1. **Immutable Base ID**: Once created, never changes
2. **Runtime Decoupling**: Can change implementations without affecting identity
3. **Operator Transparency**: Always clear who is responsible
4. **Audit Trail**: Complete history of all changes

### Privacy Controls
1. **Public/Private Identities**: Agent chooses visibility
2. **Selective Disclosure**: Can reveal only necessary information
3. **Consent-Based Sharing**: Operator controls what's shared

## Migration Strategy

### From Legacy Systems
1. **Legacy Agent Detection**: Scan for existing "agents"
2. **Identity Creation**: Generate proper canonical identities
3. **Operator Assignment**: Link to existing human operators
4. **Runtime Migration**: Move to new runtime system

### Future-Proofing
1. **Multiple Runtime Support**: Can switch providers
2. **Version Independence**: Identity persists across upgrades
3. **Scaling Support**: Handle increasing number of agents

---

*Generated: 2026-08-30*
*Status: DRAFT*