# Previous Recovery Reality

| Area before W08 | Status |
|---|---|
| Library/Playlist/Favorite/History persistence | WORKING |
| playback volume field | PARTIAL; stored but renderer authority did not restore session |
| current Track/position | MISSING operational restore |
| Queue persistence | MISSING |
| active view/Playlist | MISSING |
| window writes | PARTIAL; bounds saved but createWindow ignored them |
| graceful flush | WORKING for LocalState |
| atomic temp/rename | WORKING |
| LKG fallback | MISSING |
| malformed canonical recovery | BROKEN for durable data: default reset |
| schema migrations | WORKING through v4 |
| recovery logs | MISSING |
