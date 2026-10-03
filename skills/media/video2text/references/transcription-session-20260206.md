# Real-World Transcription Session — IMS Daily Meeting 2026-02-06

## Input
- File: `IMS Daily Meeting-20260206_001643UTC-Meeting Recording.mp4`
- Size: 54 MB, Duration: 23 min 38 sec
- Content: IT team daily standup, multi-speaker, English (Filipino accent)

## Command Used
```bash
mkdir -p ~/Desktop/v2t_input
ln -sf /path/to/video.mp4 ~/Desktop/v2t_input/
video2text -i ~/Desktop/v2t_input -o ~/Desktop/v2t_output -m small -l auto
rm -rf ~/Desktop/v2t_input
```

## Results
- **Model**: small (medium OOM'd — needs 5 GB, only 4 GB free)
- **Processing**: 191.2s for 1417.7s audio = 7.4x realtime
- **Confidence**: 56.5% (multi-speaker, background noise, accented English)
- **Output**: 4,512 chars, single-line .txt file

## Quality Issues
1. **Garbled prefix**: First ~1,800 chars was repeated "I am a smithing..." from audio noise/background music at start of recording
2. **Single-line output**: No line breaks — post-processed with `fold -w 80`
3. **MPS unsupported**: Auto-fell back to CPU (ctranslate2 limitation)

## Cleaned Output Pattern
```bash
# Remove garbled prefix by taking content after known junk string
sed 's/.*smithing//' original.txt | fold -w 80 > clean.txt
```
