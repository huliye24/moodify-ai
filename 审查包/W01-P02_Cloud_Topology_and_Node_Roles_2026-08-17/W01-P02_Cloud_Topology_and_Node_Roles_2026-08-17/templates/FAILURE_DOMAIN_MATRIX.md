# Failure Domain Matrix

| Failure | Current Behavior | Desired Behavior | Data Loss Risk | Job State Risk | Recovery Authority | Manual Action | Implementation Package |
|---|---|---|---|---|---|---|---|
| Control/API down | | | | | | | P04/P06 |
| Worker down | | | | | | | P04/P05 |
| DB unavailable | | | | | | | P03/P04 |
| OSS unavailable | | | | | | | P03/P05 |
| External API unavailable | | | | | | | P05 |
| Network partition | | | | | | | P04 |
| Disk full | | | | | | | P05 |
| Job crash | | | | | | | P04/P05 |
| Playback fetch failure | | | | | | | P06 |
