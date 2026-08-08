# Moodify Asset Model

## Principle

A functioning feature is useful.

A traceable, reusable body of evidence is an asset.

Moodify should therefore distinguish software capability from accumulated knowledge.

## Canonical Asset Loop

```text
Production Case
  -> Measurement Record
  -> Evidence Artifact
  -> Theory Update
  -> Moodify Rule Update
  -> Next Production Case
```

## 1. Production Case

A Production Case is a bounded execution unit with:

- case identity;
- source identity;
- requested objective;
- configuration;
- state history;
- authority decisions;
- outputs;
- verification result;
- closure state.

## 2. Measurement Record

A Measurement Record contains structured measurements produced under a known method/version.

Examples:

- loudness;
- spectral balance;
- transient density;
- phase correlation;
- channel differences;
- residual measurements;
- structural/MIDI measurements.

A chart alone is not enough. The underlying values and measurement method should be preserved.

## 3. Evidence Artifact

Evidence connects a claim to reproducible observations.

Examples:

- before/after metric bundles;
- plots tied to a case;
- test results;
- comparison reports;
- human listening decisions;
- failure traces.

## 4. Theory Update

A Theory Update is a research interpretation of repeated evidence.

It is not automatically a production rule.

## 5. Moodify Rule

A Rule is a versioned, testable operational rule derived from evidence and accepted into production authority.

Rules need:

- identity;
- version;
- provenance;
- scope;
- conditions;
- confidence/limitations;
- tests;
- deprecation path.

## 6. Benchmarks

Benchmarks are durable evaluation sets and procedures.

They should separate:

- synthetic fixtures;
- real audio;
- edge cases;
- human-scored cases;
- regression cases.

## 7. What Is Not Automatically an Asset

The following are not automatically assets:

- one successful run;
- one preset;
- one plot;
- one prompt;
- one unverified metric;
- one generated report;
- a duplicate implementation.

They become assets only through traceability, validation and reuse.
