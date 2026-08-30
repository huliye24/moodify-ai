# Moodify QA Desktop

**Electron desktop application for Moodify QA API**

A beautiful desktop interface for the Moodify QA audio quality analysis service.

![Moodify QA Desktop](assets/screenshot.png)

---

## Features

- **Single File Analysis**: Drag & drop or select audio files for instant quality analysis
- **Batch Analysis**: Process multiple files simultaneously
- **Visual Score Display**: See QA scores with color-coded ratings
- **Issue Detection**: View detected issues with severity levels
- **Recommendations**: Get actionable improvement suggestions
- **Real-time Status**: Monitor API connection status
- **Dark Theme**: Modern dark UI design

---

## Quick Start

### Prerequisites

1. **Moodify QA API** must be running on `localhost:8000`
   ```bash
   cd moodify-qa
   pip install -r requirements.txt
   uvicorn api.main:app
   ```

2. **Node.js** (v18 or higher)

### Installation

```bash
cd moodify-qa-desktop

# Install dependencies
npm install

# Start the app
npm start

# Or run in development mode
npm run dev
```

---

## Usage

### Single Analysis

1. Launch the app
2. Drag & drop an audio file, or click "Select File"
3. Click "Analyze"
4. View the QA report with scores, issues, and recommendations

### Batch Analysis

1. Switch to "Batch Analysis" tab
2. Select multiple audio files
3. Click "Analyze All"
4. View batch summary and individual reports

---

## Building

### Build for Current Platform

```bash
npm run build
```

### Build for Specific Platforms

```bash
# Windows
npm run build:win

# macOS
npm run build:mac

# Linux
npm run build:linux
```

Built files will be in `dist/` directory.

---

## Project Structure

```
moodify-qa-desktop/
├── src/
│   ├── main/
│   │   └── main.js          # Electron main process
│   ├── preload/
│   │   └── preload.js       # Preload script
│   └── renderer/
│       ├── index.html       # Main UI
│       ├── styles.css       # Styles
│       └── app.js           # Renderer logic
├── assets/
│   └── screenshot.png
├── package.json
└── README.md
```

---

## Tech Stack

- **Electron** - Desktop app framework
- **Node.js** - Runtime
- **HTML/CSS/JS** - Frontend (no framework, vanilla JS)

---

## API Integration

The desktop app communicates with Moodify QA API via IPC:

| Feature | IPC Channel | Description |
|---------|-------------|-------------|
| Select File | `select-audio-file` | Open file dialog |
| Analyze | `analyze-audio` | Send file to API |
| Get Report | `get-report` | Fetch analysis results |
| Batch | `analyze-batch` | Batch file analysis |

---

## Screenshots

### Main Interface
- Drag & drop upload area
- File info display
- Analyze button

### Results View
- QA Score (large display)
- Technical & Musical scores
- Score breakdown
- Issues list
- Recommendations

### Batch Analysis
- Multi-file selection
- Progress tracking
- Batch summary
- Individual reports

---

## Development

### Run in Dev Mode

```bash
npm run dev
```

This enables:
- DevTools opening automatically
- Hot reload
- Verbose logging

### Debug

Press `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Option+I` (macOS) to open DevTools.

---

## Packaging

### Package without Building

```bash
npm run pack
```

Creates unpacked app in `dist/` for testing.

### Create Installer

```bash
npm run dist
```

Creates:
- Windows: `.exe` installer
- macOS: `.dmg` disk image
- Linux: `.AppImage` file

---

## Configuration

### API URL

Edit `src/main/main.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000/api/v1';
```

### File Size Limit

Default: 100MB per file

Edit in `src/main/main.js`:

```javascript
const maxSize = 100 * 1024 * 1024; // 100MB
```

---

## Troubleshooting

### API Not Connected

- Check that Moodify QA API is running on port 8000
- Check firewall settings
- Verify API health: `curl http://localhost:8000/health`

### Analysis Fails

- Check file format (WAV, MP3, FLAC, AIFF, OGG, M4A)
- Check file size (< 100MB)
- Check API logs for errors

### Build Fails

```bash
# Clean and reinstall
rm -rf node_modules
npm install
npm run build
```

---

## Roadmap

- [ ] Export reports as PDF/JSON
- [ ] History persistence
- [ ] Settings panel
- [ ] Custom scoring profiles
- [ ] Multi-language support

---

## License

GPL-3.0-only

Copyright (c) 2024-2026 荣景文川

---

## Related Projects

- [Moodify QA API](../moodify-qa/) - The backend API service
- [Moodify Engine](../moodify-core-package/) - Core analysis modules

---

**Moodify QA Desktop** - *Professional audio quality analysis, now on your desktop.*
