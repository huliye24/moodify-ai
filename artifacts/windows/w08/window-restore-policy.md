# Window Restore Policy

Existing `LocalState.window` persists x/y/width/height/maximized. On creation, dimensions are finite, minimum 400×600 and capped to the primary work area. A saved rectangle must visibly intersect a current display; otherwise it is centered on primary. Valid coordinates are clamped fully inside the target work area. Maximized state is reapplied after safe base bounds.
