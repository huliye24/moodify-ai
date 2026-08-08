package com.moodify.app.ui.components

/** UI visibility of the global mini player. Audio playback state is independent. */
enum class MiniPlayerVisibility { VISIBLE, HIDDEN_PEEK }

/** Where a finished drag gesture should settle. */
enum class SnapDecision { VISIBLE, HIDDEN_PEEK }

fun SnapDecision.toVisibility(): MiniPlayerVisibility = when (this) {
    SnapDecision.VISIBLE -> MiniPlayerVisibility.VISIBLE
    SnapDecision.HIDDEN_PEEK -> MiniPlayerVisibility.HIDDEN_PEEK
}

object MiniPlayerGestureConstants {
    /** Downward drag past this fraction of the player height hides it. */
    const val HIDE_DISTANCE_FRACTION = 0.25f

    /** Upward drag past this fraction of the player height reveals it. */
    const val SHOW_DISTANCE_FRACTION = 0.20f

    /** Downward release velocity (px/s) that hides even below the distance threshold. */
    const val HIDE_FLING_VELOCITY_PX_S = 700f

    /** Upward release velocity (px/s) that reveals even below the distance threshold. */
    const val SHOW_FLING_VELOCITY_PX_S = 650f

    /** Touch area height of the hidden-state peek strip (dp). */
    const val PEEK_TOUCH_HEIGHT_DP = 36f

    /** Visible pill height of the peek strip (dp). */
    const val PEEK_VISUAL_HEIGHT_DP = 4f

    /** Snap animation duration (ms). */
    const val SNAP_DURATION_MS = 220
}

/**
 * Decides where the player should settle after a drag ends.
 *
 * [offsetPx] is the current drag offset (0 = fully visible, contentHeightPx = fully hidden),
 * [dragDeltaPx] the net signed drag distance (positive = downward),
 * [velocityYPxS] the signed release velocity (positive = downward).
 */
fun resolveSnapTarget(
    offsetPx: Float,
    contentHeightPx: Float,
    dragDeltaPx: Float,
    velocityYPxS: Float,
): SnapDecision {
    if (contentHeightPx <= 0f) return SnapDecision.VISIBLE
    if (velocityYPxS > MiniPlayerGestureConstants.HIDE_FLING_VELOCITY_PX_S) return SnapDecision.HIDDEN_PEEK
    if (velocityYPxS < -MiniPlayerGestureConstants.SHOW_FLING_VELOCITY_PX_S) return SnapDecision.VISIBLE
    if (dragDeltaPx >= contentHeightPx * MiniPlayerGestureConstants.HIDE_DISTANCE_FRACTION) return SnapDecision.HIDDEN_PEEK
    if (dragDeltaPx <= -contentHeightPx * MiniPlayerGestureConstants.SHOW_DISTANCE_FRACTION) return SnapDecision.VISIBLE
    // No threshold reached: settle to the nearer end so there is never a stuck half state.
    return if (offsetPx >= contentHeightPx / 2f) SnapDecision.HIDDEN_PEEK else SnapDecision.VISIBLE
}

/** Clamps a drag offset into [0, contentHeightPx] so the player can never fly past its bounds. */
fun clampedMiniPlayerOffset(currentPx: Float, deltaPx: Float, contentHeightPx: Float): Float =
    (currentPx + deltaPx).coerceIn(0f, contentHeightPx.coerceAtLeast(0f))
