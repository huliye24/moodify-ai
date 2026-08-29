# Package 03 Blockers

## EXTERNAL_DEPLOYMENT

The live Company Home source is not tracked in this repository. Package 03 establishes a new reviewable static source at `ops/web_origin/site/rongjingwenchuan/`, but original source provenance remains unknown.

## LOCAL_SOURCE_PUBLISH_PATH_REQUIRED

The existing `deploy_static_origins.sh` downloads the current production page into a release directory. It cannot publish the new local source. No production deployment or verification-marker update is performed until a reviewed upload/release procedure exists.

## LEGACY_ROUTE_DEPENDENCY_UNKNOWN

Traffic and customer dependencies for API/Developers/ACU and `/v1/*` are unavailable. They are removed only from the new Home navigation and narrative; no route or backend is deleted.

## LIMITED_COMPANY_FACTS

Founded year and location remain `UNVERIFIED` and are intentionally omitted. No financing, partnership, team biography or operating-scale claim is published.
