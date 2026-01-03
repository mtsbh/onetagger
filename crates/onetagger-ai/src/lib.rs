//! OneTagger AI Module
//!
//! AI-powered features using FREE Cloud APIs (Gemini, OpenRouter, Groq, etc.)
//! - Custom genre/style/mood tagging
//! - Intelligent energy detection
//! - Smart duplicate detection
//! - Quality control and metadata validation
//! - Context-aware playlist generation
//! - Enhanced matching using semantic understanding

#[macro_use] extern crate log;
#[macro_use] extern crate anyhow;
#[macro_use] extern crate lazy_static;

use anyhow::Error;
use serde::{Serialize, Deserialize};
use std::path::PathBuf;
use std::collections::HashMap;

// Public modules
pub mod config;
pub mod api;
pub mod tagger;
pub mod features;
pub mod classifier;
pub mod embeddings;
pub mod duplicates;
pub mod quality;
pub mod playlist;

// Re-exports
pub use config::{AIConfig, CustomTagConfig, APIConfig, APIProvider};
pub use api::APIClient;
pub use tagger::{AITagger, AIBuilder};
pub use features::{AudioFeatures, FeatureExtractor};
pub use classifier::{GenreClassifier, MoodDetector, EnergyAnalyzer};
pub use embeddings::{EmbeddingGenerator, SemanticMatcher};
pub use duplicates::{DuplicateDetector, DuplicateMatch};
pub use quality::{QualityControl, ValidationResult};
pub use playlist::PlaylistGenerator;
pub use config::PlaylistConfig;

/// AI Module version
pub const VERSION: &str = env!("CARGO_PKG_VERSION");

/// AI Analysis Result for a single track
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AIAnalysisResult {
    /// Detected genres with confidence scores
    pub genres: Vec<TagWithConfidence>,

    /// Detected moods
    pub moods: Vec<TagWithConfidence>,

    /// Custom tags (user-defined)
    pub custom_tags: Vec<TagWithConfidence>,

    /// Energy level (0-100)
    pub energy_level: Option<f32>,

    /// Danceability score (0-100)
    pub danceability: Option<f32>,

    /// Aggression/intensity (0-100)
    pub aggression: Option<f32>,

    /// Overall confidence score (0-1)
    pub confidence: f32,

    /// Audio features extracted
    pub audio_features: Option<AudioFeatures>,

    /// LLM-generated description (optional)
    pub description: Option<String>,

    /// Suggested custom tags from LLM
    pub llm_suggestions: Vec<String>,
}

/// A tag with its confidence score
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TagWithConfidence {
    pub tag: String,
    pub confidence: f32,
}

impl TagWithConfidence {
    pub fn new(tag: impl Into<String>, confidence: f32) -> Self {
        Self {
            tag: tag.into(),
            confidence: confidence.clamp(0.0, 1.0),
        }
    }
}

/// Initialize the AI module
pub fn initialize(config: &AIConfig) -> Result<(), Error> {
    info!("Initializing OneTagger AI module v{} (Cloud API Edition)", VERSION);
    info!("Using provider: {}", config.api_config.provider.display_name());
    info!("Free tier: {}", config.api_config.provider.free_tier_info());

    if config.api_config.api_key.is_none() {
        warn!("No API key configured. Please set your {} API key in settings.",
              config.api_config.provider.display_name());
        warn!("Get a free API key at: {}", get_api_key_url(&config.api_config.provider));
    }

    // Create cache directory
    if let Some(ref cache_dir) = config.cache_dir {
        std::fs::create_dir_all(cache_dir)?;
        info!("Cache directory: {}", cache_dir.display());
    }

    Ok(())
}

/// Get URL for obtaining API key
fn get_api_key_url(provider: &APIProvider) -> &'static str {
    match provider {
        APIProvider::Gemini => "https://aistudio.google.com/app/apikey",
        APIProvider::OpenRouter => "https://openrouter.ai/keys",
        APIProvider::Groq => "https://console.groq.com/keys",
        APIProvider::TogetherAI => "https://api.together.xyz/settings/api-keys",
        APIProvider::OpenAI => "https://platform.openai.com/api-keys",
        APIProvider::Custom => "Contact your provider",
    }
}

/// Analyze a single audio file and return AI-generated tags
pub async fn analyze_track(path: &PathBuf, config: &AIConfig) -> Result<AIAnalysisResult, Error> {
    info!("Analyzing track: {}", path.display());

    // Extract audio features
    let extractor = FeatureExtractor::new();
    let audio_features = extractor.extract(path)?;
    debug!("Extracted audio features: BPM={:?}, Key={:?}", audio_features.bpm, audio_features.key);

    let mut result = AIAnalysisResult {
        genres: Vec::new(),
        moods: Vec::new(),
        custom_tags: Vec::new(),
        energy_level: None,
        danceability: None,
        aggression: None,
        confidence: 0.0,
        audio_features: Some(audio_features.clone()),
        description: None,
        llm_suggestions: Vec::new(),
    };

    // Genre classification (rule-based + API)
    if config.enable_genre_classification {
        let classifier = GenreClassifier::new(config)?;
        let genres = classifier.classify(&audio_features)?;
        result.genres = genres.into_iter()
            .filter(|g| g.confidence >= config.confidence_threshold)
            .collect();
        debug!("Detected {} genres", result.genres.len());
    }

    // Mood detection (rule-based + API)
    if config.enable_mood_detection {
        let detector = MoodDetector::new(config)?;
        let moods = detector.detect(&audio_features)?;
        result.moods = moods.into_iter()
            .filter(|m| m.confidence >= config.confidence_threshold)
            .collect();
        debug!("Detected {} moods", result.moods.len());
    }

    // Energy analysis
    if config.enable_energy_analysis {
        let analyzer = EnergyAnalyzer::new(config)?;
        let energy_result = analyzer.analyze(&audio_features)?;
        result.energy_level = Some(energy_result.energy_level);
        result.danceability = Some(energy_result.danceability);
        result.aggression = Some(energy_result.aggression);
        debug!("Energy: {}, Danceability: {}, Aggression: {}",
               energy_result.energy_level, energy_result.danceability, energy_result.aggression);
    }

    // LLM-based tag suggestions (using FREE Gemini API)
    if config.api_config.api_key.is_some() {
        match get_llm_suggestions(&audio_features, &result, config).await {
            Ok((description, suggestions)) => {
                result.description = Some(description);
                result.llm_suggestions = suggestions;
                debug!("LLM generated {} custom tag suggestions", result.llm_suggestions.len());
            }
            Err(e) => {
                warn!("LLM tag suggestions failed: {}. Continuing with rule-based tags.", e);
            }
        }
    }

    // Map to custom tags if user has defined collections
    if !config.custom_tags.genres.is_empty() {
        result.custom_tags = map_to_custom_tags(&result, &config.custom_tags)?;
    }

    // Calculate overall confidence
    result.confidence = calculate_overall_confidence(&result);

    info!("Analysis complete: {} genres, {} moods, {} custom tags, energy={:?}",
          result.genres.len(), result.moods.len(), result.custom_tags.len(), result.energy_level);

    Ok(result)
}

/// Get LLM tag suggestions using API
async fn get_llm_suggestions(
    features: &AudioFeatures,
    result: &AIAnalysisResult,
    config: &AIConfig,
) -> Result<(String, Vec<String>), Error> {
    let prompt = create_llm_prompt(features, result, config);

    let api_client = APIClient::new(config.api_config.clone())?;
    let response = api_client.generate(&prompt).await?;

    parse_llm_response(&response)
}

/// Create a prompt for the LLM to suggest custom tags
fn create_llm_prompt(features: &AudioFeatures, result: &AIAnalysisResult, config: &AIConfig) -> String {
    let mut prompt = String::from("You are a DJ assistant analyzing electronic music tracks. Based on the following audio characteristics, suggest 3-5 custom tags that a DJ would use for categorization.\n\n");

    prompt.push_str("Audio Features:\n");
    if let Some(bpm) = features.bpm {
        prompt.push_str(&format!("- BPM: {:.1}\n", bpm));
    }
    if let Some(ref key) = features.key {
        prompt.push_str(&format!("- Key: {}\n", key));
    }

    if !result.genres.is_empty() {
        prompt.push_str(&format!("\nDetected Genres: {}\n",
            result.genres.iter().take(3).map(|g| &g.tag).cloned().collect::<Vec<_>>().join(", ")));
    }

    if !result.moods.is_empty() {
        prompt.push_str(&format!("Detected Moods: {}\n",
            result.moods.iter().take(3).map(|m| &m.tag).cloned().collect::<Vec<_>>().join(", ")));
    }

    if let Some(energy) = result.energy_level {
        prompt.push_str(&format!("Energy Level: {:.0}/100\n", energy));
    }

    // Add user's custom tag collection for context
    if !config.custom_tags.genres.is_empty() {
        prompt.push_str(&format!("\nAvailable custom genres: {}\n",
            config.custom_tags.genres.join(", ")));
    }

    prompt.push_str("\nProvide 3-5 tags (comma-separated) that describe the vibe, context, or sub-genre. Focus on tags a DJ would use to find this track later (e.g., 'peak-time', 'warehouse-vibe', 'hypnotic', 'melodic-progressive').\n\n");
    prompt.push_str("Tags: ");

    prompt
}

/// Parse LLM response to extract description and tag suggestions
fn parse_llm_response(response: &str) -> Result<(String, Vec<String>), Error> {
    // Clean up response
    let cleaned = response.trim();

    // Extract tags (comma or newline separated)
    let tags: Vec<String> = cleaned
        .split(&[',', '\n', ';'][..])
        .map(|s| s.trim())
        .filter(|s| !s.is_empty())
        .filter(|s| s.len() < 50)  // Reasonable tag length
        .map(|s| s.to_lowercase().replace(" ", "-"))
        .take(10)  // Max 10 tags
        .collect();

    let description = cleaned.lines().next().unwrap_or("").to_string();

    Ok((description, tags))
}

/// Map AI results to user's custom tag collections
fn map_to_custom_tags(result: &AIAnalysisResult, custom_config: &CustomTagConfig) -> Result<Vec<TagWithConfidence>, Error> {
    let mut custom_tags = Vec::new();

    // Map genres to custom genre taxonomy
    for genre in &result.genres {
        if custom_config.genres.iter().any(|g| g.eq_ignore_ascii_case(&genre.tag)) {
            custom_tags.push(genre.clone());
        }
    }

    // Map moods to custom mood taxonomy
    for mood in &result.moods {
        if custom_config.moods.iter().any(|m| m.eq_ignore_ascii_case(&mood.tag)) {
            custom_tags.push(mood.clone());
        }
    }

    // Check LLM suggestions against custom collections
    for suggestion in &result.llm_suggestions {
        // Check all custom collections
        for (_name, tags) in &custom_config.custom_collections {
            if tags.iter().any(|t| t.eq_ignore_ascii_case(suggestion)) {
                custom_tags.push(TagWithConfidence::new(suggestion.clone(), 0.8));
                break;
            }
        }
    }

    Ok(custom_tags)
}

/// Calculate overall confidence score from all detections
fn calculate_overall_confidence(result: &AIAnalysisResult) -> f32 {
    let mut scores = Vec::new();

    scores.extend(result.genres.iter().map(|g| g.confidence));
    scores.extend(result.moods.iter().map(|m| m.confidence));
    scores.extend(result.custom_tags.iter().map(|c| c.confidence));

    if scores.is_empty() {
        return 0.5;
    }

    scores.iter().sum::<f32>() / scores.len() as f32
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_tag_with_confidence() {
        let tag = TagWithConfidence::new("techno", 0.95);
        assert_eq!(tag.tag, "techno");
        assert_eq!(tag.confidence, 0.95);
    }

    #[test]
    fn test_llm_prompt_generation() {
        let mut features = AudioFeatures::default();
        features.bpm = Some(128.0);
        features.key = Some("Am".to_string());

        let mut result = AIAnalysisResult {
            genres: vec![TagWithConfidence::new("techno", 0.9)],
            moods: vec![TagWithConfidence::new("dark", 0.85)],
            energy_level: Some(85.0),
            ..Default::default()
        };

        let config = AIConfig::default();
        let prompt = create_llm_prompt(&features, &result, &config);

        assert!(prompt.contains("128"));
        assert!(prompt.contains("Am"));
        assert!(prompt.contains("techno"));
    }

    #[test]
    fn test_api_key_urls() {
        assert!(get_api_key_url(&APIProvider::Gemini).contains("aistudio.google.com"));
        assert!(get_api_key_url(&APIProvider::Groq).contains("groq.com"));
    }
}

impl Default for AIAnalysisResult {
    fn default() -> Self {
        Self {
            genres: Vec::new(),
            moods: Vec::new(),
            custom_tags: Vec::new(),
            energy_level: None,
            danceability: None,
            aggression: None,
            confidence: 0.0,
            audio_features: None,
            description: None,
            llm_suggestions: Vec::new(),
        }
    }
}
