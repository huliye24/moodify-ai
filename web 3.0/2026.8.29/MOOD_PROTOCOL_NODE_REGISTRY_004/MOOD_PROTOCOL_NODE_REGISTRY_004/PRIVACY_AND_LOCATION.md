# Privacy and Location Policy

## Principle

The public network map should reveal enough to understand geographic distribution without exposing unnecessary operator risk.

## Precision levels

Support:

```text
country
region
city
exact
hidden
```

Default public registry should prefer `country` or `region`.

Exact coordinates or street addresses should NOT be required.

## Never publish by default

- home address
- personal phone
- private IP
- internal VPC topology
- SSH endpoint
- cloud account ID
- billing account
- credential
- customer location
- precise machine coordinates

## Region data

Recommended:

```json
{
  "countryCode": "SG",
  "regionCode": null,
  "city": null,
  "precision": "country"
}
```

## Developer nodes

A developer node may have:

```text
region.precision = hidden
```

if location is unnecessary.

## Public display

UI can render:

```text
Singapore
United States / West
China / Zhejiang
Europe
```

without exposing exact infrastructure addresses.
