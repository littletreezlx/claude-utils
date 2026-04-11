---
name: SmbDataSource prefetch rationale
description: Why SmbDataSource has an internal 256KB prefetch buffer — non-obvious Media3 interaction
type: project
originSessionId: a8a448ae-f135-4fb0-b0db-65a5a1750cee
---
SmbDataSource holds an internal 256KB prefetch buffer because Media3's `DefaultExtractorInput.peek()` / `peekFully()` forward the caller's `length` argument **verbatim** to `dataReader.read()` without any batching.

**Why:** MatroskaExtractor parses EBML VINTs one byte at a time via `input.peek(buf, 0, 1)`. On a DataSource backed by `smbj.File.read()` (no kernel/socket buffering underneath, unlike HTTP/FileDataSource), each 1-byte peek becomes a full SMB2_READ round-trip (~10 ms). Early playback stalled at ~5KB into the MKV header — death by a thousand network calls. `HttpDataSource` / `FileDataSource` don't hit this because OS-level buffering absorbs the small reads; smbj is direct, so we buffer ourselves.

**How to apply:**
- Never remove the prefetch buffer without replacing it with an equivalent read-ahead layer.
- When touching SmbDataSource, remember ExoPlayer **will** call `read()` with `length=1` — the loop/single-read paths must handle that efficiently, not just "large chunks that happen to work".
- If you ever add another custom DataSource that talks directly to a network API (no socket-level read-ahead), it needs the same treatment.
- The `streamFromZero` branch (>2GB file workaround) skips prefetch — acceptable only because such files blow past headers into bulk streaming almost immediately and the extractor's tiny peeks occur before they matter. If you encounter a >2GB MKV header that fails to parse, that path needs the prefetch too.

Evidence trail: `100 Meters 2025 1080p ... BONE.mkv` (1.6GB) reproduced `toRead=1` per call, stuck at `readPosition≈5052`. After adding the 256KB prefetch, playback reached `STATE_READY` with `positionMs` advancing smoothly; refill logs show clean 262144-byte chunks stepping through the file.
