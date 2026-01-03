//! AI Tagger Module
//!
//! Implements AutotaggerSource trait to integrate with OneTagger

use anyhow::{Error, Result};
use onetagger_tagger::{
    AutotaggerSource, TaggerConfig, Track, TrackMatch, AudioFileInfo,
    PlatformInfo, SupportedTag, supported_tags,
    PlatformCustomOptions, PlatformCustomOptionValue
};
use crate::config::AIConfig;
use crate::analyze_track;

/// AI Tagger - implements OneTagger's AutotaggerSource trait
pub struct AITagger {
    ai_config: AIConfig,
}

impl AITagger {
    /// Create new AI tagger with config
    pub fn new_with_config(ai_config: AIConfig) -> Self {
        Self { ai_config }
    }

    /// Get platform info for UI display
    pub fn get_info() -> PlatformInfo {
        PlatformInfo {
            id: "ai".to_string(),
            name: "AI Tagger (Gemini)".to_string(),
            description: r#"
                <b>AI-Powered Tagging using FREE Gemini API</b><br>
                Automatically tag your tracks with:
                <ul>
                    <li>Custom genres and styles (your own taxonomy!)</li>
                    <li>Mood detection (dark, uplifting, hypnotic, etc.)</li>
                    <li>Energy level analysis (0-100)</li>
                    <li>Smart tag suggestions using Google Gemini</li>
                </ul>
                <br>
                <b>Setup:</b> Get your FREE API key at <a href="https://aistudio.google.com/app/apikey">Google AI Studio</a>
            "#.to_string(),
            version: env!("CARGO_PKG_VERSION").to_string(),
            icon: &[],  // TODO: Add icon
            max_threads: 8,
            custom_options: Self::custom_options(),
            supported_tags: supported_tags!(
                Genre, Style, Mood, BPM, Key, OtherTags
            ),
            requires_auth: true,  // Requires API key
        }
    }

    /// Custom configuration options for UI
    fn custom_options() -> PlatformCustomOptions {
        PlatformCustomOptions::new()
            .add("apiKey", "Gemini API Key",
                PlatformCustomOptionValue::String {
                    value: String::new(),
                    hidden: Some(true)  // Hide API key input
                })
            .add_tooltip("apiProvider", "API Provider",
                "Which AI provider to use (Gemini is recommended)",
                PlatformCustomOptionValue::Option {
                    values: vec![
                        "Gemini (Google)".to_string(),
                        "OpenRouter".to_string(),
                        "Groq".to_string(),
                        "Together AI".to_string(),
                    ],
                    value: "Gemini (Google)".to_string(),
                })
            .add("enableGenreClassification", "Genre Classification",
                PlatformCustomOptionValue::Boolean { value: true })
            .add("enableMoodDetection", "Mood Detection",
                PlatformCustomOptionValue::Boolean { value: true })
            .add("enableEnergyAnalysis", "Energy Analysis",
                PlatformCustomOptionValue::Boolean { value: true })
            .add_tooltip("confidenceThreshold", "Confidence Threshold (%)",
                "Minimum confidence to accept AI suggestions",
                PlatformCustomOptionValue::Number {
                    min: 50,
                    max: 100,
                    step: 5,
                    value: 70,
                })
    }
}

impl AutotaggerSource for AITagger {
    fn match_track(
        &mut self,
        info: &AudioFileInfo,
        _config: &TaggerConfig,
    ) -> Result<Vec<TrackMatch>> {
        // Get artist and title using methods
        let artist = info.artist().unwrap_or("Unknown");
        let title = info.title().unwrap_or("Unknown");

        info!("AI analyzing: {} - {}", artist, title);

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
            artists: if !info.artists.is_empty() {
                info.artists.clone()
            } else {
                vec!["Unknown".to_string()]
            },
            genres: analysis.genres.iter().map(|g| g.tag.clone()).collect(),
            styles: Vec::new(),
            bpm: analysis.audio_features.as_ref().and_then(|f| f.bpm).map(|b| b as i64),
            key: analysis.audio_features.as_ref().and_then(|f| f.key.clone()),
            mood: analysis.moods.first().map(|m| m.tag.clone()),
            duration: info.duration.unwrap_or_default(),
            url: String::new(),
            ..Default::default()
        };

        // Add AI-specific tags to "other" field
        if let Some(energy) = analysis.energy_level {
            track.other.push((
                onetagger_tag::FrameName::same("AI_ENERGY"),
                vec![format!("{:.0}", energy)]
            ));
        }

        if let Some(danceability) = analysis.danceability {
            track.other.push((
                onetagger_tag::FrameName::same("AI_DANCEABILITY"),
                vec![format!("{:.0}", danceability)]
            ));
        }

        // Add custom tags as styles
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

    fn extend_track(&mut self, _track: &mut Track, _config: &TaggerConfig) -> Result<(), Error> {
        // AI tagger doesn't need extended metadata fetching
        // All metadata is gathered in match_track
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ai_tagger_info() {
        let info = AITagger::get_info();
        assert_eq!(info.id, "ai");
        assert!(info.name.contains("AI"));
        assert!(info.requires_auth);  // Requires API key
    }

    #[test]
    fn test_custom_options() {
        let options = AITagger::custom_options();
        assert!(!options.options.is_empty());
        // Should have API key option
        assert!(options.options.iter().any(|o| o.id == "apiKey"));
    }
}
