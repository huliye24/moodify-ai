#!/usr/bin/env node

/**
 * MOOD Protocol Mainnet Configuration Validator
 *
 * Validates protocol/mainnet.json against schema and business rules.
 * Usage: node scripts/validate-mainnet-config.mjs protocol/mainnet.json
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Get current file directory
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load schema
const schemaPath = path.join(__dirname, '..', 'protocol', 'mainnet.schema.json');
const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));

// Load config
const configPath = process.argv[2] || path.join(__dirname, '..', 'protocol', 'mainnet.json');
const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

// Simple JSON Schema Validator (lightweight implementation)
class SchemaValidator {
  constructor(schema) {
    this.schema = schema;
  }

  validate(data, schema = this.schema) {
    const errors = [];
    this.validateRecursive(data, schema, errors);
    return errors;
  }

  validateRecursive(data, schema, errors, path = '') {
    // Check required properties
    if (schema.required) {
      for (const required of schema.required) {
        if (!(required in data)) {
          errors.push(`${path}.${required}: Missing required property`);
        }
      }
    }

    // Check all properties
    for (const [key, value] of Object.entries(data)) {
      const propertyPath = path ? `${path}.${key}` : key;
      const propertySchema = schema.properties?.[key];

      if (!propertySchema) {
        if (!schema.additionalProperties) {
          errors.push(`${propertyPath}: Additional property not allowed`);
        }
        continue;
      }

      this.validateProperty(value, propertySchema, propertyPath, errors);
    }
  }

  validateProperty(value, schema, path, errors) {
    // Type validation
    if (schema.type) {
      const actualType = Array.isArray(schema.type) ?
        schema.type.find(t => this.isType(value, t)) :
        this.isType(value, schema.type);

      if (!actualType) {
        errors.push(`${path}: Expected type ${schema.type}, got ${typeof value}`);
      }
    }

    // Enum validation
    if (schema.enum && !schema.enum.includes(value)) {
      errors.push(`${path}: Value must be one of: ${schema.enum.join(', ')}`);
    }

    // Pattern validation
    if (schema.pattern && typeof value === 'string' && !new RegExp(schema.pattern).test(value)) {
      errors.push(`${path}: Value does not match pattern: ${schema.pattern}`);
    }

    // Minimum/Maximum validation
    if (typeof value === 'number') {
      if (schema.minimum !== undefined && value < schema.minimum) {
        errors.push(`${path}: Value ${value} is less than minimum ${schema.minimum}`);
      }
      if (schema.maximum !== undefined && value > schema.maximum) {
        errors.push(`${path}: Value ${value} is greater than maximum ${schema.maximum}`);
      }
    }

    // Array validation
    if (schema.type === 'array' && Array.isArray(value)) {
      if (schema.uniqueItems && new Set(value).size !== value.length) {
        errors.push(`${path}: Array contains duplicate items`);
      }

      if (schema.items) {
        value.forEach((item, index) => {
          this.validateProperty(item, schema.items, `${path}[${index}]`, errors);
        });
      }
    }

    // Object validation
    if (schema.type === 'object' && typeof value === 'object' && value !== null) {
      this.validateRecursive(value, schema, errors, path);
    }
  }

  isType(value, type) {
    switch (type) {
      case 'string': return typeof value === 'string';
      case 'number': return typeof value === 'number';
      case 'integer': return Number.isInteger(value);
      case 'boolean': return typeof value === 'boolean';
      case 'object': return typeof value === 'object' && value !== null && !Array.isArray(value);
      case 'array': return Array.isArray(value);
      case 'null': return value === null;
      default: return false;
    }
  }
}

// Business logic validators
const businessValidators = {
  validateChainFamily(chain) {
    const errors = [];
    if (chain.family === 'evm') {
      // Validate EVM-specific properties
      if (!chain.chainId || chain.chainId < 1) {
        errors.push('EVM chain must have valid chainId > 0');
      }
    }
    return errors;
  },

  validateTokenFormat(token) {
    const errors = [];

    // Validate address format for EVM
    if (token.identifier) {
      if (!/^0x[a-fA-F0-9]{40}$/.test(token.identifier)) {
        errors.push(`Token identifier must be valid EVM address: ${token.identifier}`);
      }
    }

    // Validate decimals
    if (typeof token.decimals !== 'number' || token.decimals < 0 || token.decimals > 36) {
      errors.push(`Token decimals must be between 0-36: ${token.decimals}`);
    }

    // Validate total supply format
    if (!/^\d+$/.test(token.totalSupplyAtomic)) {
      errors.push(`Total supply must be atomic integer string: ${token.totalSupplyAtomic}`);
    }

    return errors;
  },

  validateEndpoints(endpoints) {
    const errors = [];

    // Validate RPC URLs
    if (Array.isArray(endpoints.rpcUrls)) {
      const uniqueUrls = new Set();
      for (const url of endpoints.rpcUrls) {
        try {
          new URL(url);
          if (uniqueUrls.has(url)) {
            errors.push(`Duplicate RPC URL: ${url}`);
          }
          uniqueUrls.add(url);
        } catch {
          errors.push(`Invalid RPC URL: ${url}`);
        }
      }
    }

    // Validate explorer URL
    try {
      new URL(endpoints.explorerBaseUrl);
    } catch {
      errors.push(`Invalid explorer URL: ${endpoints.explorerBaseUrl}`);
    }

    return errors;
  },

  validateLaunchStatus(config) {
    const errors = [];
    const launch = config.launch;

    if (launch.status === 'locked') {
      if (!launch.lockedAt) {
        errors.push('Locked config must have lockedAt timestamp');
      }
      if (!launch.lockedBy) {
        errors.push('Locked config must have lockedBy identifier');
      }
      if (!config.evidence.sourceCommit) {
        errors.push('Locked config must have source commit in evidence');
      }
    }

    return errors;
  }
};

// Main validation function
function validateMainnetConfig() {
  console.log('🔍 Validating MOOD Protocol Mainnet Configuration...\n');

  // Basic schema validation
  const validator = new SchemaValidator(schema);
  const schemaErrors = validator.validate(config);

  // Business logic validation
  const businessErrors = [
    ...businessValidators.validateChainFamily(config.chain),
    ...businessValidators.validateTokenFormat(config.token),
    ...businessValidators.validateEndpoints(config.endpoints),
    ...businessValidators.validateLaunchStatus(config),
  ];

  // Combine all errors
  const allErrors = [...schemaErrors, ...businessErrors];

  // Validation result
  if (allErrors.length === 0) {
    console.log('✅ Configuration is valid!\n');

    // Print summary
    console.log('📋 Configuration Summary:');
    console.log(`   Protocol: ${config.protocol.name} (${config.protocol.ticker})`);
    console.log(`   Chain: ${config.chain.network} (ID: ${config.chain.chainId})`);
    console.log(`   Token: ${config.token.name} (${config.token.symbol})`);
    console.log(`   Total Supply: ${config.token.totalSupplyAtomic} atomic units`);
    console.log(`   Status: ${config.launch.status}`);

    if (config.launch.status === 'locked') {
      console.log(`   Locked At: ${config.launch.lockedAt}`);
      console.log(`   Locked By: ${config.launch.lockedBy}`);
    }

    console.log('\n🎉 All acceptance gates passed!');
    return true;
  } else {
    console.log('❌ Configuration validation failed!\n');

    console.log('📝 Validation Errors:');
    allErrors.forEach((error, index) => {
      console.log(`   ${index + 1}. ${error}`);
    });

    console.log(`\n💡 Total errors: ${allErrors.length}`);
    console.log('🔧 Please fix the errors above.');
    return false;
  }
}

// Run validation
const isValid = validateMainnetConfig();
process.exit(isValid ? 0 : 1);