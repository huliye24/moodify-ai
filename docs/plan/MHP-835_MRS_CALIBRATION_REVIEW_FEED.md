# MHP-835: MRS Calibration Review Feed

**Status**: done
**Implementation**: `moodify_runtime/product_integration.py::write_calibration_review_feed()`

Converts scoring calibration recommendations into MRS calibration lab proposals. Each proposal links to the originating task, includes both pseudo and MRS Open delta values, and carries severity + human review flags. Status is set to "open" for the calibration review workflow.
