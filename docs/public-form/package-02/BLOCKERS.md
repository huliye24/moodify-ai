# Package 02 Blockers

## AUDIO_PUBLIC_RIGHTS_REQUIRED

No same-source Original/Moodify pair currently satisfies all required public-demo conditions: explicit public rights, traceable lineage, comparable formats/timeline, and documented loudness fairness. The repository rights matrix explicitly records public demo as NO for current test material.

Safe result: the Product Home renders the Sound Proof section as `Listening proof in preparation.` without audio sources or simulated controls. A synchronized A/B control must only be enabled after an approved `AUDIO_DEMO_MANIFEST` exists.

## ANDROID_3_1_DEPLOYMENT_REQUIRED

The repository contains Moodify Music 3.1.0 (`60acfcfa...4337`) but `https://rongjingmusic.com/downloads/Moodify_Music_3.1.0_Android_20260816.apk` returned 404 on 2026-08-19. The verified 2.0 APK and release ZIP remain live and are retained on the Product Home.

## LOCAL_SOURCE_PUBLISH_PATH_REQUIRED

`deploy_static_origins.sh` downloads the current live site into a server release directory; it does not upload the local repository source. Package 02 implements and verifies the repository source but does not deploy or change DNS/Cloudflare. A reviewed publish procedure is required before production cutover.
