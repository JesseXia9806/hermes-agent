---
name: video2text
description: Video/audio to text transcription using faster-whisper (Video2Text / MP4ToText). Batch process videos into TXT/SRT/VTT/JSON output.
---

# Video2Text Skill

Transcribe video/audio files to text using `faster-whisper` (2-8x faster than original OpenAI Whisper). Uses the **Video2Text** tool by sawyerbutton.

## Location

Installed at: **`~/.video2text/`** (cloned GitHub repo)
CLI wrappers: **`video2text`**, **`mp4-to-text`**, **`v2t`** — all available on PATH via `~/.local/bin/`

## ⚠️ Critical: `-i` expects a DIRECTORY, not a file

`-i` (input) **must be a directory**. If you pass a single file path, the tool errors with `"Input path is not a directory"`.

### Single-file workaround

```bash
mkdir -p ~/Desktop/v2t_input
ln -sf /path/to/your/video.mp4 ~/Desktop/v2t_input/
video2text -i ~/Desktop/v2t_input -o ~/Desktop/v2t_output -m small
rm -rf ~/Desktop/v2t_input   # clean up
```

### Normal batch usage (directory of videos)

```bash
# Process all videos in ./videos_dir -> output to ./output_dir
video2text -i /path/to/videos -o /path/to/output

# With specific model and language
video2text -i ./videos -o ./texts -m small -l zh

# Parallel processing (2 workers)
video2text -i ./videos -o ./texts -w 2

# Skip already-processed files
video2text -i ./videos -o ./texts -s
```

### System info / model list

```bash
video2text --system-info      # Hardware, device, memory status
video2text --list-models      # Available Whisper models
```

### Python API

```python
from video2text import transcribe_file, transcribe_url

# Transcribe local file
result = transcribe_file("/path/to/video.mp4", model_name="medium")
print(result["text"])          # Full transcription
print(result["segments"])      # List of {start, end, text}
print(result["language"])      # Detected language code
```

## Configuration

Default config at `~/.video2text/config/config.ini`. Key settings:

| Setting | Default | Options |
|---------|---------|---------|
| `model_name` | `medium` | tiny, base, small, medium, large, large-v2, large-v3 |
| `language` | `auto` | auto, zh, en, ja, ko, fr, de, es |
| `device` | `auto` | auto, cpu, cuda, mps |
| `compute_type` | `auto` | auto, float16, int8, int8_float16, float32 |
| `batch_size` | `1` | 1-16 (higher = faster on GPU) |
| `max_workers` | `1` | Parallel workers |
| `vad_filter` | `false` | Skip silence segments |

### Via CLI flags

```bash
video2text -i ./videos -o ./texts -m large-v3 -d mps -w 2
```

### Via custom config file

```bash
video2text -i ./videos -o ./texts -c ~/.video2text/config/config.ini
```

## Memory Constraints on This Mac

**Available: ~4 GB free**. The medium model (requires 5 GB) will fail with:
```
Insufficient memory for model 'medium'. Required: 5.0GB, Available: 4.0GB
```

**Use `small` (3 GB)** for reliable operation — still achieves ~7x realtime (23 min meeting processed in 3 min).

## ⚠️ Known Issue: MPS Not Supported

faster-whisper (via ctranslate2) does **not** support Apple Silicon MPS. The tool auto-falls back to CPU — still fast (8-10x realtime with tiny/base), but won't use the GPU. This is a ctranslate2 limitation, not a bug.

## Environment on This Mac

- **macOS 27.0 (ARM64)** with **Apple Silicon MPS** available
- **faster-whisper** v1.2.1 installed
- **FFmpeg** v8.1 (via Homebrew)
- **Model path**: ~/.cache/huggingface/hub/ (auto-downloaded on first use)
- **Python 3.13.5** with PyTorch 2.13.0
- Memory available: **~4 GB** (small model recommended; medium may OOM)

## Transcription Quality Notes

- **Detection confidence** varies by audio quality. Noisy recordings or multi-speaker meetings may score **~50-60%** confidence.
- **Garbled sections**: Audio with background noise, music, or silence at the start can produce repeated nonsense text ("I am a smithing..."). Strip these manually from the output.
- **Single-line output**: Default `.txt` format dumps everything on one line — no line breaks. Use `formats = txt,srt,vtt` in config.ini or post-process with `fold -w 80`.
- **Language detection**: Set `-l zh` / `-l en` explicitly when you know the language, rather than relying on auto-detect.
- **VAD filter**: For recordings with long silence, enable `vad_filter = true` in config.ini to skip silent segments and improve accuracy.

## Recommended Models by Memory

| Model | Size | Min RAM | Speed | Use Case |
|-------|------|---------|-------|----------|
| tiny | 39 MB | 1 GB | very fast | Quick test, low-res |
| base | 142 MB | 2 GB | fast | General purpose |
| small | 244 MB | 3 GB | medium | Balanced |
| medium | 769 MB | 5 GB | medium | **Recommended** |
| large-v3 | 1.55 GB | 10 GB | slow | Highest accuracy |

On this Mac (~2.9 GB free), use **small** or **base** for faster processing, **medium** for quality.

## Output Formats

Default is `.txt`. For timed output, configure `formats` in config.ini:

```
formats = txt,srt,vtt,json
```

## Further Reading

- Project README: `~/.video2text/README.md`
- Config: `~/.video2text/config/config.ini`
- Arch docs: `~/.video2text/ref/architecture.md`
- API ref: `~/.video2text/ref/api-reference.md`
- Workflows: `~/.video2text/ref/workflows.md`
- Real transcription session notes: `references/transcription-session-20260206.md`
