# OneTagger AI Enhancement Implementation Plan

## Overview
This document outlines the comprehensive AI enhancement features being added to OneTagger. These features will provide intelligent, automated tagging capabilities with custom tag collections, quality control, and advanced music library management.

## Architecture

### New Components

```
onetagger-ai/
├── Core AI Engine
│   ├── Model management (ONNX Runtime)
│   ├── Audio feature extraction
│   └── Inference pipeline
├── Custom Tag System
│   ├── User-defined taxonomies
│   ├── Training data management
│   └── Model fine-tuning
├── Classification System
│   ├── Genre/style multi-label classifier
│   ├── Mood detection
│   └── Energy level analysis
├── Matching Enhancement
│   ├── Semantic embeddings
│   ├── Cross-language support
│   └── Version/remix detection
├── Duplicate Detection
│   ├── Audio fingerprinting
│   ├── Neural embeddings
│   └── Quality comparison
├── Quality Control
│   ├── Tag validation
│   ├── Completeness scoring
│   └── Auto-fix suggestions
└── Smart Playlists
    ├── Energy curve generation
    ├── Harmonic mixing
    └── Context-aware selection
```

## Features

### 1. Custom AI Tagging

**What it does:**
- Analyzes audio files to automatically assign custom tags
- Supports user-defined tag collections (genres, moods, vibes)
- Machine learning models that learn from your library

**Configuration:**
```json
{
  "ai": {
    "enabled": true,
    "customTags": {
      "genres": ["Deep Techno", "Melodic House", "Progressive Breaks"],
      "moods": ["dark", "uplifting", "melancholic", "euphoric"],
      "vibes": ["warehouse", "beach-sunset", "peak-time"]
    },
    "confidenceThreshold": 0.7,
    "multiLabel": true
  }
}
```

**Use Cases:**
- Tag your library with your personal genre definitions
- Consistent tagging across all tracks
- Works offline (local models)

### 2. Intelligent Energy Detection

**What it does:**
- Analyzes audio to detect energy level (0-100)
- Detects mood characteristics
- Validates/enhances MixedInKey data

**Features:**
- Energy curve analysis (intro, build, peak, outro)
- Danceability scoring
- Aggression/intensity detection
- Tempo stability analysis

**Integration with MixedInKey:**
- Cross-validation of BPM and key
- Enhanced mood detection
- Quality control for existing tags

### 3. Custom Tag Suggestions via AI

**What it does:**
- Uses LLM to suggest custom tags based on audio analysis
- Combines audio features with existing metadata
- Natural language descriptions

**Example:**
```
Audio Analysis: Dark pads, driving bassline, 128 BPM, A minor
Existing Tags: Techno, Peak Time
→ AI Suggests: ["warehouse-vibe", "hypnotic", "dark-progressive"]
```

### 4. Enhanced Matching Intelligence

**What it does:**
- Replaces Levenshtein distance with semantic embeddings
- Better handling of remixes, edits, and versions
- Cross-language track matching

**Improvements:**
- "Original Mix" ≈ "Radio Edit" ≈ "Club Version"
- Artist name variations (DJ Snake vs. Dj Snake)
- Non-English titles

### 5. Smart Duplicate Detection

**What it does:**
- Finds duplicate tracks in your library
- Detects different quality versions
- Identifies similar tracks

**Detection Methods:**
1. **Exact Duplicates**: Same audio, different files
2. **Quality Variants**: 320kbps MP3 vs FLAC
3. **Different Masters**: Original vs remaster
4. **Similar Tracks**: Same melody, different arrangement

**Actions:**
- Keep highest quality version
- Merge tags from duplicates
- Create consolidated view

### 6. Intelligent Quality Control

**What it does:**
- Validates tag consistency
- Detects metadata errors
- Suggests corrections

**Validations:**
- Genre vs BPM consistency (Classical at 174 BPM = suspicious)
- Key detection vs tagged key
- Duration mismatches
- Missing critical tags
- Low-quality album art

**Auto-Fix Capabilities:**
- Capitalize genre names
- Standardize artist names
- Fill missing BPM/key from audio analysis
- Download higher quality artwork

### 7. Context-Aware Playlist Generation

**What it does:**
- Generates DJ-ready playlists with smooth transitions
- Energy curve management
- Harmonic mixing support

**Parameters:**
```json
{
  "playlistGen": {
    "duration": 60,  // minutes
    "startMood": "chill",
    "peakMood": "energetic",
    "endMood": "cool-down",
    "harmonicMixing": true,
    "energyCurve": "gradual-build",
    "genreConsistency": 0.8
  }
}
```

**Features:**
- BPM transitions (gradual or stepped)
- Key compatibility (Camelot wheel)
- Energy progression
- Genre coherence
- Mood journey

### 8. Smart Renaming & Organization

**What it does:**
- AI-powered folder structure suggestions
- Intelligent file naming
- Library organization

**Example:**
```
Your library has:
- 60% Techno (20% Peak Time, 15% Minimal, 25% Melodic)
- 25% House (15% Deep, 10% Tech)
- 15% Breaks

Suggested Structure:
/Music Library/
  /Techno/
    /Peak Time - 128+ BPM/
    /Minimal - Dark/
    /Melodic - Emotional/
  /House/
    /Deep House - Groovy/
    /Tech House - Underground/
  /Breaks/
```

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
- [x] Analyze existing codebase
- [ ] Create `onetagger-ai` crate
- [ ] Set up ONNX Runtime integration
- [ ] Implement audio feature extraction
- [ ] Create AI configuration system

### Phase 2: Custom Tagging (Week 3-4)
- [ ] Custom tag collection UI
- [ ] Genre/style classifier
- [ ] Mood detection system
- [ ] Energy level analysis
- [ ] Training data management

### Phase 3: Advanced Features (Week 5-6)
- [ ] Duplicate detection
- [ ] Quality control system
- [ ] Enhanced matching (embeddings)
- [ ] Smart playlist generation

### Phase 4: Integration & UI (Week 7-8)
- [ ] Integrate AI as platform/module
- [ ] Add UI components
- [ ] Settings panel
- [ ] Visualization (confidence scores, energy curves)

### Phase 5: Testing & Refinement (Week 9-10)
- [ ] End-to-end testing
- [ ] Model optimization
- [ ] Performance tuning
- [ ] Documentation

## Technical Stack

### Rust Dependencies
```toml
[dependencies]
# ML Inference
ort = "2.0"  # ONNX Runtime
tract = "0.21"  # Alternative lightweight inference

# Audio Analysis
aubio = "0.2"  # Pitch, tempo, onset detection
rusty-chromaprint = "0.1"  # Audio fingerprinting
hound = "3.5"  # WAV reading

# Embeddings & NLP
rust-bert = "0.21"  # Sentence embeddings (optional)
tokenizers = "0.15"

# Utilities
ndarray = "0.15"
nalgebra = "0.32"
```

### Optional Cloud Integration
- OpenAI API for LLM-based tag suggestions
- Custom model hosting (optional)

### Models
1. **Audio Classification**: MusicNN, VGGish, or custom
2. **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
3. **Audio Features**: Librosa-equivalent in Rust (aubio)

## Data Flow

```
Audio File
    ↓
[Feature Extraction]
    ├─ Spectral features (MFCCs, chroma)
    ├─ Temporal features (BPM, beats)
    ├─ Harmonic features (key, pitch)
    └─ Loudness/energy
    ↓
[AI Models]
    ├─ Genre Classifier → [Techno, House, ...]
    ├─ Mood Detector → [dark, uplifting, ...]
    ├─ Energy Analyzer → [85/100]
    └─ Embedding Generator → [vector]
    ↓
[Post-Processing]
    ├─ Confidence filtering
    ├─ Multi-label aggregation
    └─ Custom tag mapping
    ↓
[Write to Track]
    ├─ track.custom["ai_genre"] = "Deep Techno"
    ├─ track.custom["ai_mood"] = "dark,hypnotic"
    ├─ track.custom["ai_energy"] = "85"
    └─ track.custom["ai_confidence"] = "0.92"
```

## Configuration Schema

### TaggerConfig Extension
```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AIConfig {
    pub enabled: bool,

    // Custom Tags
    pub custom_tags: CustomTagConfig,

    // Feature Toggles
    pub enable_genre_classification: bool,
    pub enable_mood_detection: bool,
    pub enable_energy_analysis: bool,
    pub enable_duplicate_detection: bool,
    pub enable_quality_control: bool,

    // Thresholds
    pub confidence_threshold: f32,
    pub duplicate_threshold: f32,

    // Models
    pub model_path: Option<PathBuf>,
    pub use_cloud_api: bool,
    pub api_key: Option<String>,

    // Advanced
    pub multi_label_classification: bool,
    pub max_tags_per_track: usize,
    pub prefer_ai_over_platform: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CustomTagConfig {
    pub genres: Vec<String>,
    pub moods: Vec<String>,
    pub vibes: Vec<String>,
    pub custom_collections: HashMap<String, Vec<String>>,
}
```

## UI Components

### New Screens
1. **AI Tagging Tab** (client/src/views/AITagger.vue)
   - Custom tag manager
   - Model selection
   - Batch AI tagging interface

2. **Duplicate Manager** (client/src/views/Duplicates.vue)
   - Duplicate track list
   - Quality comparison
   - Merge/delete actions

3. **Quality Control** (client/src/views/QualityControl.vue)
   - Validation results
   - Auto-fix suggestions
   - Batch corrections

4. **Smart Playlists** (client/src/views/SmartPlaylists.vue)
   - Playlist generator
   - Energy curve editor
   - Preview & export

### Settings Integration
- AI Settings panel in Settings.vue
- Custom tag editor
- Model management
- API key configuration

## Database/Storage

### AI Model Storage
```
~/.config/OneTagger/
├── settings.json (extended with AI config)
├── models/
│   ├── genre_classifier.onnx
│   ├── mood_detector.onnx
│   ├── embeddings.onnx
│   └── metadata.json
├── custom_tags/
│   ├── training_data.json
│   └── user_taxonomies.json
└── cache/
    ├── embeddings_cache.db
    └── fingerprints.db
```

## API Extensions

### New Endpoints
```rust
// Axum routes in onetagger-ui
POST /api/ai/tag
    → Analyze and tag files with AI

GET /api/ai/duplicates
    → Find duplicates in library

POST /api/ai/quality-check
    → Validate track metadata

POST /api/ai/generate-playlist
    → Create smart playlist

GET /api/ai/models
    → List available models

POST /api/ai/train
    → Fine-tune models (future)
```

## Performance Considerations

### Optimization Strategies
1. **Batch Processing**: Process multiple tracks in parallel
2. **Caching**: Store embeddings and fingerprints
3. **Lazy Loading**: Load models on-demand
4. **GPU Acceleration**: ONNX Runtime CUDA support (optional)
5. **Model Quantization**: Use INT8 models for speed

### Resource Requirements
- **Memory**: 500MB-2GB (depending on models)
- **Storage**: 100-500MB (models)
- **CPU**: Multi-core recommended
- **GPU**: Optional, improves speed 5-10x

## Future Enhancements

### Phase 2+ Features
1. **Cloud Model Sync**: Download community-trained models
2. **Collaborative Filtering**: Learn from similar users
3. **Lyrics Analysis**: Sentiment and theme detection
4. **Cover Art Generation**: AI-generated artwork
5. **Audio Enhancement**: Stem separation, mastering detection
6. **Vinyl Detection**: Identify vinyl rips vs digital
7. **Live Performance Mode**: Real-time next-track suggestions
8. **Genre Evolution Tracking**: Detect emerging sub-genres

## Success Metrics

### KPIs
- **Tagging Accuracy**: >85% match with user expectations
- **Duplicate Detection Rate**: >95% true positives
- **Performance**: <500ms per track (local inference)
- **User Satisfaction**: Measured via feedback
- **Library Quality Score**: Average metadata completeness

## Risks & Mitigation

### Technical Risks
1. **Model Size**: Large models may be slow
   - **Mitigation**: Use quantized models, offer cloud option
2. **Accuracy**: AI may make mistakes
   - **Mitigation**: Confidence scores, user review
3. **Platform Compatibility**: ONNX Runtime on all OSes
   - **Mitigation**: Fallback to cloud API

### UX Risks
1. **Complexity**: Too many options
   - **Mitigation**: Smart defaults, progressive disclosure
2. **Trust**: Users may not trust AI tags
   - **Mitigation**: Transparency (show confidence), easy override

## Success Criteria

### MVP (Minimum Viable Product)
- [ ] Custom genre/style tagging works offline
- [ ] Energy/mood detection provides useful insights
- [ ] Duplicate detection finds exact duplicates
- [ ] Quality control catches obvious errors
- [ ] UI is intuitive and responsive

### Full Release
- [ ] All features implemented and tested
- [ ] Documentation complete
- [ ] Community models available
- [ ] Performance optimized
- [ ] User feedback integrated

---

## Getting Started

Once implemented, users will:

1. **Install OneTagger** with AI support
2. **Configure Custom Tags** in AI Settings
3. **Run AI Analysis** on their library
4. **Review & Refine** AI suggestions
5. **Enjoy** a perfectly tagged, organized library

---

**This is a living document and will be updated as implementation progresses.**
