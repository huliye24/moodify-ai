# Sort Contract

Keys: Title, Artist, Recently Added (`created_at`) and Duration. Defaults are Title ascending, except Recently Added uses newest first. `Intl.Collator` provides locale-aware primary comparison; title then stable Track ID are tie-breakers. Unknown duration sorts last ascending. Sort returns a copied array and never writes Playlist/Queue/Library order.
