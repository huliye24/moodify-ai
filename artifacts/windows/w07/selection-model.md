# Selection Model

Selection is `{ selected_ids, anchor_id, focused_id }` in React component memory only. Click selects one; Ctrl-click toggles; Shift-click selects the stable visible ID range; Ctrl+A selects the current view; Escape clears. Sort preserves IDs. Search removes no-longer-visible IDs. View change clears selection. Queue duplicates remain keyed by QueueItem ID in Queue-specific interactions.
