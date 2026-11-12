> **Document version:** film/voice/disk-log.md v1.0 | 7 Nov 2026 | Author: voice-audio (R10) | Status: draft (CP8)

# Disk log: R10 voice test (7 Nov 2026, AST)

Limits for this task: stop if free disk would fall under 10 GB; at most 6 GB of new downloads (models plus Python wheels). Free space is `df -k ~` (the Data volume), converted to GiB (÷ 1,048,576). Cache sizes are `du -sk`.

Free disk also moved for reasons outside this task. Between 15:06 and 15:13 it fell by about 3.1 GiB while this task's caches did not change, and later it rose again (other processes and APFS housekeeping). The download sizes below are therefore taken from cache growth, not from the change in free space.

| time (AST) | step | free before (GiB) | free after (GiB) | what this task added |
|---|---|---|---|---|
| 15:04 | start (`df -h ~`: 27 Gi free) | 26.7 | — | — |
| 15:05 | Arabic TTS venv `/tmp/r10-voice/venv-ar` (TrafficTwin's pinned `tts-ar-requirements.txt`: torch 2.6.0, chatterbox-tts 0.1.7, mlx-whisper 0.4.3; 104 wheels downloaded) | 26.65 | 25.34 | uv cache +1.27 GiB; venv 1.27 GiB apparent (APFS clones of the cache) |
| 15:06 | English TTS venv `/tmp/r10-voice/venv-en` (pinned `tts-requirements.txt`: torch 2.14.1, kokoro 0.9.4) | 25.34 | 23.66 | uv cache +0.70 GiB; venv 0.81 GiB apparent |
| 15:13-15:14 | model downloads: `NAMAA-Space/NAMAA-Saudi-TTS` (only `t3_mtl23ls_v2.safetensors` 2.14 GB, README, conds.pt), `oddadmix/Nabra-Saudi-82M` (`nabra_saudi_82m_v0.pth` 0.33 GB, voice, scripts, samples), `facebook/mms-tts-ara` (`model.safetensors` 0.145 GB, configs) | 20.59 | 17.13 | Hugging Face cache +2.44 GiB |
| 15:15 | Piper venv `/tmp/r10-voice/venv-piper` (piper-tts 1.8.0, onnxruntime 1.31.1) | 17.13 | 16.01 | uv cache +0.12 GiB; venv 0.14 GiB |
| 15:47 | deleted the `facebook/mms-tts-ara` cache (rejected: CC-BY-NC-4.0, test only); blob checked by SHA-256 77d29c97… | 20.17 | 20.31 | Hugging Face cache −0.14 GiB |
| 15:48 | end (`df -h ~`: 20 Gi free) | — | 20.3 | — |

## Totals

- **New downloads:** about 4.4 GiB (4.7 GB). Python wheels in the uv cache account for +2.10 GiB (9.36 → 11.56 M KB). Model weights in the Hugging Face cache account for +2.30 GiB net after the MMS deletion (12.29 → 14.71 M KB). This is inside the 6 GB cap.
- **Already cached and reused (no download):**
  - `ResembleAI/chatterbox` rev 5bb1f6ee: Multilingual V2 weights, s3gen, ve, conds.
  - `hexgrad/Kokoro-82M` rev f3ff3571: weights and the af_heart and am_michael voices.
  - `mlx-community/whisper-large-v3-turbo` rev a4aaeec0: weights.
  - Copied out of TrafficTwin (read-only): the ClArTTS reference clip and `ar_JO-kareem-medium.onnx`.
- **Not downloaded:**
  - Chatterbox Multilingual V3 (about 3.2 GB; it would breach the 6 GB cap).
  - Coqui XTTS-v2 (CPML, licence research only).
  - Fish Audio, F5-TTS and the other non-commercial Saudi fine-tunes (licence).
  - Fasee7-Najdi-Small with its VoxCPM2 base (about 5 GB), aszfezf/saudi-arabic-tts (4.2 GB) and AhmedEladl/saudi-tts (5.6 GB): disk cap.
- **Lowest free space seen:** 16.0 GiB at 15:15, above the 10 GB floor.

## Clean-up still available (Tariq's call at CP8)

- Throwaway venvs: `rm -rf /tmp/r10-voice`. This frees up to 2.4 GiB apparent, much of it shared clones of the uv cache.
- If NAMAA-Saudi-TTS is rejected, remove its 2.14 GB blob: `~/.cache/huggingface/hub/blobs/21/211deb34…` and the `models--NAMAA-Space--NAMAA-Saudi-TTS` folder.
- If Nabra-Saudi-82M is rejected, remove its 0.33 GB blob: `blobs/91/91b7e83f…` and the `models--oddadmix--Nabra-Saudi-82M` folder.
- The uv cache wheels (torch 2.6, torch 2.14 and others) are reusable for the final narration. Keep them until after CP8.
