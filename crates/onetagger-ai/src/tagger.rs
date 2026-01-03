//! AI Tagger Module
//!
//! Implements AutotaggerSource trait to integrate with OneTagger

use anyhow::{Error, Result};
use onetagger_tagger::{
    AutotaggerSource, TaggerConfig, Track, TrackMatch, AudioFileInfo,
    PlatformInfo, SupportedTag, supported_tags, MatchingUtils,
    PlatformCustomOptions
};
use std::collections::HashMap;
use crate::config::AIConfig;
use crate::analyze_track;

/// AI Tagger - implements OneTagger's AutotaggerSource trait
pub struct AITagger {
    ai_config: AIConfig,
}

impl AITagger {
    pub fn new(ai_config: AIConfig) -> Self {
        Self { ai_config }
    }

    /// Get platform info for UI display
    pub fn info() -> PlatformInfo {
        PlatformInfo {
            id: "ai".to_string(),
            name: "AI Tagger".to_string(),
            description: r#"
                <b>AI-Powered Tagging</b><br>
                Uses machine learning to automatically tag your tracks with:
                <ul>
                    <li>Custom genres and styles</li>
                    <li>Mood detection (dark, uplifting, etc.)</li>
                    <li>Energy level analysis</li>
                    <li>Smart tag suggestions using Llama 3.2</li>
                </ul>
                Works completely offline with free, open-source models.
            "#.to_string(),
            version: env!("CARGO_PKG_VERSION").to_string(),
            icon: include_bytes!("../../assets/ai-icon.png"),  // Will add later
            max_threads: 8,  // AI inference can be parallelized
            custom_options: Self::custom_options(),
            supported_tags: supported_tags!(
                Genre, Style, Mood, BPM, Key, OtherTags
            ),
            requires_auth: false,  // No authentication needed!
        }
    }

    /// Custom configuration options for UI
    fn custom_options() -> PlatformCustomOptions {
        let mut options = PlatformCustomOptions::new();

        // Enable/disable features
        options.push_opt("enableGenreClassification", "Genre Classification",
            onetagger_tagger::PlatformCustomOptionValue::Boolean { value: true });

        options.push_opt("enableMoodDetection", "Mood Detection",
            onetagger_tagger::PlatformCustomOptionValue::Boolean { value: true });

        options.push_opt("enableEnergyAnalysis", "Energy Analysis",
            onetagger_tagger::PlatformCustomOptionValue::Boolean { value: true });

        // LLM model selection
        options.push_opt("llmModel", "LLM Model",
            onetagger_tagger::PlatformCustomOptionValue::Option {
                values: vec![
                    "Llama 3.2 1B (Fastest)".to_string(),
                    "Llama 3.2 3B (Balanced)".to_string(),
                    "Phi-3.5 Mini (Smart)".to_string(),
                    "Qwen 2.5 1.5B (Multilingual)".to_string(),
                ],
                value: "Llama 3.2 1B (Fastest)".to_string(),
            });

        // Confidence threshold
        options.push_opt("confidenceThreshold", "Confidence Threshold",
            onetagger_tagger::PlatformCustomOptionValue::Number {
                min: 50,
                max: 100,
                step: 5,
                value: 70,
            });

        options
    }
}

impl AutotaggerSource for AITagger {
    fn new(_config: &TaggerConfig) -> Result<Self>
    where
        Self: Sized
    {
        // Load AI config from tagger config custom options
        let ai_config = AIConfig::default();
        Ok(Self::new(ai_config))
    }

    fn info(&mut self) -> PlatformInfo {
        Self::info()
    }

    fn match_track(
        &mut self,
        info: &AudioFileInfo,
        config: &TaggerConfig,
    ) -> Result<Vec<TrackMatch>> {
        info!("AI analyzing: {} - {}", info.artist.as_ref().unwrap_or(&"Unknown".to_string()),
            info.title.as_ref().unwrap_or(&"Unknown".to_string()));

        // Analyze track using AI
        let analysis = match tokio::runtime::Runtime::new()?.block_on(
            analyze_track(&info.path, &self.ai_config)
        ) {
            Ok(a) => a,
            Err(e) => {
                warn!("AI analysis failed: {}", e);
                return Ok(Vec::new());
            }
        };

        // Convert AI result to Track
        let mut track = Track {
            platform: "ai".to_string(),
            title: info.title.clone().unwrap_or_default(),
            artists: vec![info.artist.clone().unwrap_or_default()],
            genres: analysis.genres.iter().map(|g| g.tag.clone()).collect(),
            styles: Vec::new(),
            bpm: analysis.audio_features.as_ref().and_then(|f| f.bpm).map(|b| b as i64),
            key: analysis.audio_features.as_ref().and_then(|f| f.key.clone()),
            mood: analysis.moods.first().map(|m| m.tag.clone()),
            ..Default::default()
        };

        // Add AI-specific tags to "other" field
        if let Some(energy) = analysis.energy_level {
            track.other.push((
                onetagger_tag::FrameName::same("AI_ENERGY"),
                vec![format!("{:.0}", energy)]
            ));
        }

        // Add custom tags
        for tag in analysis.custom_tags {
            track.styles.push(tag.tag);
        }

        // Add LLM suggestions as custom tags
        if !analysis.llm_suggestions.is_empty() {
            track.other.push((
                onetagger_tag::FrameName::same("AI_TAGS"),
                analysis.llm_suggestions.clone()
            ));
        }

        // Create track match with confidence
        let track_match = TrackMatch::new(analysis.confidence as f64, track);

        Ok(vec![track_match])
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ai_tagger_info() {
        let info = AITagger::info();
        assert_eq!(info.id, "ai");
        assert_eq!(info.name, "AI Tagger");
        assert!(!info.requires_auth);
    }
}
