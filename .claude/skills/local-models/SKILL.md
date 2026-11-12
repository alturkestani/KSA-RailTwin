---
name: local-models
description: Running open-weights LLMs, Whisper and open TTS locally on the Apple-silicon Mac (MLX first, llama.cpp second; Ollama was removed from this Mac on 31 Oct 2026; vLLM not on Mac), memory and disk limits, the disk gate, where models live, registering every model in the licence register, and when to ask Tariq for GPU. Use before downloading or running any model inside the pipeline (extraction, OCR, translation drafts, embeddings, classification, transcription, speech).
---
> **Document version:** skills/local-models/SKILL.md v1.2 | 31 Oct 2026 | Author: coordinator | Status: active

# Local open-weights models on the Mac

Rule 12: open-weights models run locally come first for pipeline tasks. Claude (`claude-fable-5-1`, `claude-opus-5-5`, `claude-haiku-5-5`) remains the orchestrator and coder; it is not a pipeline model.

## Model policy (Tariq, 31 Oct 2026): when a paid model or API is allowed
Open/local models stay the default for bulk, low-stakes work. Paid state-of-the-art models and APIs are allowed where they **materially improve quality**, especially: Saudi-dialect Arabic script and narration (R10), Arabic–English translation of final deliverables (R8), and extraction or verification of hard Arabic sources. Ollama is not needed.

1. **Before first use of any paid model or API**, write a one-paragraph request in `docs/STATUS.md` (what step, which model/vendor, why open isn't good enough, estimated USD, licence/terms for commercial and public release) and **stop that step until Tariq approves**. Other tracks continue.
2. Prefer **one A/B test** (open vs paid, the same 2-minute sample) and show Tariq both before committing.
3. **Log every paid call** in the cost log (`docs/cost-log.md`/`.csv`) with vendor and model; **alert Tariq at 80 %** of any approved amount.
4. **Never send personal data, credentials or unpublished partner material** to any API.
5. **Never store API keys in the repo**; ask Tariq to set them as environment variables (named in the request), read them from the environment only, and keep `.env*` gitignored.

How to file the request: append to `docs/STATUS.md` under "Model policy" a block `#### Paid-model request <n> — <step> — pending` with the paragraph above, write `<LABEL>: blocked - awaiting paid-model approval (request <n>)` only if the whole label cannot proceed, otherwise continue the open-model path and leave the paid step as a TODO in the status file. For the A/B test, keep both samples (open and paid) under `runs/ab/<step>/` with the prompt, the input text, the model/vendor, timestamps and the cost row id, and point Tariq to both. Paid calls are logged with `uv run python -m common.cost_log add-paid --vendor <v> --model <m> --usd <x> --step <s> --approved-usd <cap>`; the command warns at 80 % of the approved amount (the R1 integration run adds `add-paid` if it does not exist yet).

## Machine limits
- Apple M3 Pro, 18 GB unified memory, no CUDA. Use Metal (MLX, llama.cpp) or CPU. **Ollama is not available**: Tariq removed it and its 25 GB of models on 31 Oct 2026 (D13 follow-up, `docs/STATUS.md`); no track may assume `ollama`. `vllm` does not target macOS; do not install it here.
- Memory rule of thumb: a Q4-quantised model needs about 0.6 GB per billion parameters plus context KV cache (budget 1–3 GB). Stay under about 10 GB of model memory in total so the OS, the builders and a browser still fit. Practical ceiling: 7–14B at Q4 for LLMs; Whisper large-v3-turbo or medium; TTS models of a few GB.
- Run one model at a time; never alongside an OSRM extract or a SUMO run.

## Disk gate (binding)
- No model download until `docs/STATUS.md` says the disk is confirmed for the phase (R1a skims ≥ 15 GiB free, R3 ≥ 40 GiB, R10 ≥ 50 GiB). 52 GiB were free on 31 Oct 2026 after the Ollama removal.
- Before any download: `df -h ~ | tail -1`, the model's size from its model card, and a line in `docs/status/<track>.md`: `download planned: <model> <size GB>, free before <GB>`. After: free after.
- Models live in the Hugging Face cache (`~/.cache/huggingface/hub`, the default for `mlx-lm`, `mlx-whisper` and `huggingface-cli`) or in `~/models/<name>/` for GGUF files, never under the repo or under `data/`. **Already cached on 31 Oct 2026 (reuse, do not re-download):** `mlx-community/Qwen2.5-7B-Instruct-4bit` (4.0 GB), `mlx-community/Qwen2.5-1.5B-Instruct-4bit` (0.8 GB), `intfloat/multilingual-e5-large` (2.1 GB, embeddings), `ResembleAI/chatterbox` (configs; weights fetched on first use). `hexgrad/Kokoro-82M` and `mlx-community/whisper-large-v3-turbo` hold config files only; their weights (about 0.3 GB and 1.6 GB) are re-downloaded on first use under the disk gate.

## Toolchain
| need | first choice | notes |
|---|---|---|
| LLM inference | `mlx-lm` (`uv run --with mlx-lm python -m mlx_lm.generate --model mlx-community/Qwen2.5-7B-Instruct-4bit ...`; `mlx_lm.server` gives an OpenAI-compatible endpoint) | first choice on Apple silicon; the 7B 4-bit Qwen is cached. Fallback `llama.cpp` (brew `llama.cpp`, Metal) with a GGUF under `~/models/`; pin the repo and revision/sha in the licence register |
| Python inference on Apple silicon | `mlx-lm`, `mlx-whisper` | fastest on M-series; TrafficTwin used MLX Whisper |
| Transcription / alignment | `mlx-whisper` or `faster-whisper` (CPU) or `whisper.cpp` | used for subtitle alignment and TTS read-back (`voiceover-tts`, `subtitles-srt`) |
| TTS | see `voiceover-tts` | Kokoro-82M (English), Chatterbox, F5-TTS, Piper, MMS-TTS, Fish-Speech, OpenVoice; XTTS-v2 only for tests (CPML) |
| Arabic LLMs | ALLaM-family, Jais, Qwen (multilingual) where the licence permits | read the licence; many have use restrictions |

Candidate check before use: `uv run python -m common.licences add ...` with the exact licence name read from the model card, then `huggingface-cli download <repo> --revision <sha>` with the revision recorded (or `llama.cpp`'s `-hf <repo>` for a GGUF). Arabic at R10: prefer an MLX conversion of `ALLaM-7B-Instruct-preview` or a Jais release **if the licence permits**, else the cached multilingual Qwen2.5-7B; download at most one Arabic model (≤ 5 GB) under the R10 gate.

## Procedure for a pipeline task
1. State the task, the input size and the acceptable error (e.g. OCR of a GASTAT PDF table; translation draft of a dossier; classification of 2,000 OSM places).
2. Pick the smallest model that meets it; test on 20 items; record precision/recall or error rate in the status file.
3. Any output that becomes a number in a register is checked by a human-readable trace (source id) — a model's output is never itself a source.
4. Record model, revision, quantisation, prompt file and seed in `runs/<id>/meta.json`.

## When to ask Tariq for GPU (rule 7)
Fine-tuning a TTS or LLM, 4K renders, or any model above the memory ceiling: write the estimate (model, GB, hours, expected gain) in the status file and stop at the next checkpoint. Never sign up to, pay for or send data to a cloud or sovereign GPU service on your own.
