//! AI Configuration Module
//!
//! Defines all configuration structures for AI features using FREE Cloud APIs

use serde::{Serialize, Deserialize};
use std::path::PathBuf;
use std::collections::HashMap;

/// Main AI configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AIConfig {
    /// Enable AI features globally
    pub enabled: bool,

    /// Custom tag configuration
    pub custom_tags: CustomTagConfig,

    /// API configuration (Gemini, OpenRouter, etc.)
    pub api_config: APIConfig,

    /// Feature toggles
    pub enable_genre_classification: bool,
    pub enable_mood_detection: bool,
    pub enable_energy_analysis: bool,
    pub enable_duplicate_detection: bool,
    pub enable_quality_control: bool,
    pub enable_smart_playlists: bool,

    /// Confidence threshold for accepting AI predictions (0.0-1.0)
    pub confidence_threshold: f32,

    /// Duplicate detection similarity threshold (0.0-1.0)
    pub duplicate_threshold: f32,

    /// Quality control strictness (0.0-1.0)
    pub quality_strictness: f32,

    /// Advanced options
    pub multi_label_classification: bool,
    pub max_tags_per_track: usize,
    pub prefer_ai_over_platform: bool,

    /// Performance options
    pub batch_size: usize,
    pub max_threads: usize,

    /// Cache directory
    pub cache_dir: Option<PathBuf>,
}

impl Default for AIConfig {
    fn default() -> Self {
        let base_path = onetagger_shared::Settings::get_folder()
            .unwrap_or_else(|_| PathBuf::from("."));

        Self {
            enabled: true,
            custom_tags: CustomTagConfig::default(),
            api_config: APIConfig::default(),
            enable_genre_classification: true,
            enable_mood_detection: true,
            enable_energy_analysis: true,
            enable_duplicate_detection: false,
            enable_quality_control: true,
            enable_smart_playlists: false,
            confidence_threshold: 0.7,
            duplicate_threshold: 0.85,
            quality_strictness: 0.6,
            multi_label_classification: true,
            max_tags_per_track: 5,
            prefer_ai_over_platform: false,
            batch_size: 32,
            max_threads: num_cpus::get(),
            cache_dir: Some(base_path.join("cache")),
        }
    }
}

/// Custom tag collections defined by the user
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CustomTagConfig {
    /// Custom genre taxonomy
    pub genres: Vec<String>,

    /// Custom mood tags
    pub moods: Vec<String>,

    /// Custom vibe tags
    pub vibes: Vec<String>,

    /// Additional custom collections (name -> tags)
    pub custom_collections: HashMap<String, Vec<String>>,
}

impl Default for CustomTagConfig {
    fn default() -> Self {
        Self {
            // Example custom genres for DJs
            genres: vec![
                "deep-techno".to_string(),
                "melodic-techno".to_string(),
                "peak-time-techno".to_string(),
                "minimal-techno".to_string(),
                "progressive-house".to_string(),
                "deep-house".to_string(),
                "tech-house".to_string(),
                "melodic-house".to_string(),
            ],
            // Example mood tags
            moods: vec![
                "dark".to_string(),
                "uplifting".to_string(),
                "melancholic".to_string(),
                "euphoric".to_string(),
                "hypnotic".to_string(),
                "groovy".to_string(),
            ],
            // Example vibe tags
            vibes: vec![
                "warehouse".to_string(),
                "beach-sunset".to_string(),
                "peak-time".to_string(),
                "warm-up".to_string(),
                "after-hours".to_string(),
            ],
            custom_collections: HashMap::new(),
        }
    }
}

/// API Configuration - which FREE cloud API to use
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct APIConfig {
    /// Which API provider to use
    pub provider: APIProvider,

    /// API key (free tier)
    pub api_key: Option<String>,

    /// API endpoint (optional custom endpoint)
    pub endpoint: Option<String>,

    /// Enable caching of API responses
    pub enable_cache: bool,

    /// Cache TTL in seconds (default: 7 days)
    pub cache_ttl: u64,

    /// Rate limiting (requests per minute)
    pub rate_limit: u32,
}

impl Default for APIConfig {
    fn default() -> Self {
        Self {
            provider: APIProvider::Gemini,  // Best free option!
            api_key: None,
            endpoint: None,
            enable_cache: true,
            cache_ttl: 7 * 24 * 60 * 60,  // 7 days
            rate_limit: 15,  // Gemini free tier: 15 RPM
        }
    }
}

/// Available FREE API providers
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "kebab-case")]
pub enum APIProvider {
    /// Google Gemini (RECOMMENDED)
    Gemini,
    /// OpenRouter (multiple models, free tier)
    OpenRouter,
    /// Groq (ultra-fast inference, free)
    Groq,
    /// Together AI (free credits)
    TogetherAI,
    /// OpenAI (requires paid API key)
    OpenAI,
    /// Custom endpoint
    Custom,
}

impl APIProvider {
    /// Get default API endpoint
    pub fn default_endpoint(&self) -> &'static str {
        match self {
            Self::Gemini => "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent",
            Self::OpenRouter => "https://openrouter.ai/api/v1/chat/completions",
            Self::Groq => "https://api.groq.com/openai/v1/chat/completions",
            Self::TogetherAI => "https://api.together.xyz/v1/chat/completions",
            Self::OpenAI => "https://api.openai.com/v1/chat/completions",
            Self::Custom => "",
        }
    }

    /// Get display name
    pub fn display_name(&self) -> &'static str {
        match self {
            Self::Gemini => "Google Gemini 2.0 Flash (FREE)",
            Self::OpenRouter => "OpenRouter (Multiple Models, FREE)",
            Self::Groq => "Groq (Ultra-Fast, FREE)",
            Self::TogetherAI => "Together AI (FREE Credits)",
            Self::OpenAI => "OpenAI (Paid)",
            Self::Custom => "Custom Endpoint",
        }
    }

    /// Get free tier limits
    pub fn free_tier_info(&self) -> &'static str {
        match self {
            Self::Gemini => "15 RPM, 1M tokens/day, completely free",
            Self::OpenRouter => "20 RPM, free tier available",
            Self::Groq => "30 RPM, 14,400/day, free",
            Self::TogetherAI => "$25 free credits/month",
            Self::OpenAI => "Requires paid API key",
            Self::Custom => "Depends on provider",
        }
    }

    /// Is this provider recommended?
    pub fn is_recommended(&self) -> bool {
        matches!(self, Self::Gemini)
    }

    /// Does this provider require an API key?
    pub fn requires_api_key(&self) -> bool {
        !matches!(self, Self::Custom)
    }
}

/// Model configuration (simplified for API-based approach)
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ModelConfig {
    /// Specific model name (optional)
    pub model_name: Option<String>,

    /// Temperature (0.0-1.0) for creativity
    pub temperature: f32,

    /// Max tokens in response
    pub max_tokens: u32,
}

impl Default for ModelConfig {
    fn default() -> Self {
        Self {
            model_name: None,  // Use provider default
            temperature: 0.7,  // Balanced
            max_tokens: 256,   // Enough for tag suggestions
        }
    }
}

/// Playlist generation configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PlaylistConfig {
    /// Desired playlist duration in minutes
    pub duration_minutes: usize,

    /// Starting mood/energy
    pub start_mood: String,

    /// Peak mood/energy
    pub peak_mood: String,

    /// Ending mood/energy
    pub end_mood: String,

    /// Enable harmonic mixing (Camelot wheel)
    pub harmonic_mixing: bool,

    /// Energy curve type
    pub energy_curve: EnergyCurve,

    /// Genre consistency (0.0 = any mix, 1.0 = same genre only)
    pub genre_consistency: f32,

    /// Allow BPM changes
    pub allow_bpm_changes: bool,

    /// Max BPM difference between consecutive tracks
    pub max_bpm_difference: f32,
}

impl Default for PlaylistConfig {
    fn default() -> Self {
        Self {
            duration_minutes: 60,
            start_mood: "warm-up".to_string(),
            peak_mood: "peak-time".to_string(),
            end_mood: "cool-down".to_string(),
            harmonic_mixing: true,
            energy_curve: EnergyCurve::GradualBuild,
            genre_consistency: 0.7,
            allow_bpm_changes: true,
            max_bpm_difference: 10.0,
        }
    }
}

/// Energy curve types for playlist generation
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "kebab-case")]
pub enum EnergyCurve {
    /// Gradually build energy
    GradualBuild,
    /// Quick rise to peak, then maintain
    QuickPeak,
    /// Constant energy throughout
    Constant,
    /// Up and down waves
    Wave,
    /// Custom curve (defined by user)
    Custom,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_default_config() {
        let config = AIConfig::default();
        assert!(config.enabled);
        assert_eq!(config.confidence_threshold, 0.7);
        assert!(config.enable_genre_classification);
    }

    #[test]
    fn test_api_providers() {
        let gemini = APIProvider::Gemini;
        assert!(gemini.is_recommended());
        assert!(gemini.requires_api_key());
        assert!(gemini.default_endpoint().contains("googleapis.com"));
        assert_eq!(gemini.display_name(), "Google Gemini 2.0 Flash (FREE)");
    }

    #[test]
    fn test_custom_tags() {
        let custom = CustomTagConfig::default();
        assert!(!custom.genres.is_empty());
        assert!(!custom.moods.is_empty());
        assert!(custom.genres.contains(&"deep-techno".to_string()));
    }
}
