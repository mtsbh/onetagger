//! Classification Module
//!
//! AI-powered classifiers for:
//! - Genre/style detection
//! - Mood detection
//! - Energy analysis

use anyhow::{Error, Result};
use crate::config::AIConfig;
use crate::features::AudioFeatures;
use crate::TagWithConfidence;

/// Genre/Style classifier
pub struct GenreClassifier {
    confidence_threshold: f32,
}

impl GenreClassifier {
    pub fn new(config: &AIConfig) -> Result<Self> {
        Ok(Self {
            confidence_threshold: config.confidence_threshold,
        })
    }

    /// Classify genre from audio features
    pub fn classify(&self, features: &AudioFeatures) -> Result<Vec<TagWithConfidence>> {
        let mut genres = Vec::new();

        // Rule-based classification based on BPM and features
        // TODO: Replace with ONNX model inference

        if let Some(bpm) = features.bpm {
            // Techno range
            if (120.0..=135.0).contains(&bpm) && features.spectral_centroid > 1200.0 {
                genres.push(TagWithConfidence::new("techno", 0.85));

                // Sub-genres based on features
                if features.rms_energy > 0.75 {
                    genres.push(TagWithConfidence::new("peak-time-techno", 0.80));
                } else if features.rms_energy < 0.5 {
                    genres.push(TagWithConfidence::new("minimal-techno", 0.75));
                }
            }

            // House range
            if (118.0..=128.0).contains(&bpm) && features.zero_crossing_rate < 0.4 {
                genres.push(TagWithConfidence::new("house", 0.82));

                if features.spectral_centroid < 1000.0 {
                    genres.push(TagWithConfidence::new("deep-house", 0.78));
                }
            }

            // Trance/Progressive
            if (128.0..=140.0).contains(&bpm) && features.onset_strength > 0.6 {
                genres.push(TagWithConfidence::new("progressive", 0.80));
            }
        }

        // Filter by confidence
        Ok(genres.into_iter()
            .filter(|g| g.confidence >= self.confidence_threshold)
            .collect())
    }
}

/// Mood detector
pub struct MoodDetector {
    confidence_threshold: f32,
}

impl MoodDetector {
    pub fn new(config: &AIConfig) -> Result<Self> {
        Ok(Self {
            confidence_threshold: config.confidence_threshold,
        })
    }

    /// Detect mood from audio features
    pub fn detect(&self, features: &AudioFeatures) -> Result<Vec<TagWithConfidence>> {
        let mut moods = Vec::new();

        // Rule-based mood detection
        // TODO: Replace with ML model

        // Dark vs Uplifting (based on key and spectral features)
        if let Some(ref key) = features.key {
            if key.contains('m') || key.contains("min") {
                moods.push(TagWithConfidence::new("dark", 0.75));
                moods.push(TagWithConfidence::new("melancholic", 0.70));
            } else {
                moods.push(TagWithConfidence::new("uplifting", 0.72));
                moods.push(TagWithConfidence::new("euphoric", 0.68));
            }
        }

        // Energy-based moods
        if features.rms_energy > 0.7 {
            moods.push(TagWithConfidence::new("energetic", 0.85));
            moods.push(TagWithConfidence::new("driving", 0.80));
        } else if features.rms_energy < 0.4 {
            moods.push(TagWithConfidence::new("chill", 0.78));
            moods.push(TagWithConfidence::new("atmospheric", 0.75));
        }

        // Hypnotic (repetitive, stable tempo)
        if features.tempo_stability > 0.9 {
            moods.push(TagWithConfidence::new("hypnotic", 0.80));
        }

        Ok(moods.into_iter()
            .filter(|m| m.confidence >= self.confidence_threshold)
            .collect())
    }
}

/// Energy analyzer
pub struct EnergyAnalyzer {}

impl EnergyAnalyzer {
    pub fn new(_config: &AIConfig) -> Result<Self> {
        Ok(Self {})
    }

    /// Analyze energy levels
    pub fn analyze(&self, features: &AudioFeatures) -> Result<EnergyAnalysis> {
        // Calculate energy level (0-100)
        let energy_level = (features.rms_energy * 100.0).clamp(0.0, 100.0);

        // Danceability (based on tempo, onset strength)
        let danceability = if let Some(bpm) = features.bpm {
            let bpm_score = if (118.0..=135.0).contains(&bpm) { 0.9 } else { 0.5 };
            let onset_score = features.onset_strength;
            ((bpm_score + onset_score) / 2.0 * 100.0).clamp(0.0, 100.0)
        } else {
            50.0
        };

        // Aggression (based on spectral features)
        let aggression = ((features.spectral_flux + features.zero_crossing_rate) / 2.0 * 100.0)
            .clamp(0.0, 100.0);

        Ok(EnergyAnalysis {
            energy_level,
            danceability,
            aggression,
        })
    }
}

/// Energy analysis result
#[derive(Debug, Clone)]
pub struct EnergyAnalysis {
    pub energy_level: f32,
    pub danceability: f32,
    pub aggression: f32,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_genre_classification() {
        let config = AIConfig::default();
        let classifier = GenreClassifier::new(&config).unwrap();

        let mut features = AudioFeatures::default();
        features.bpm = Some(128.0);
        features.spectral_centroid = 1500.0;
        features.rms_energy = 0.8;

        let genres = classifier.classify(&features).unwrap();
        assert!(!genres.is_empty());
    }

    #[test]
    fn test_mood_detection() {
        let config = AIConfig::default();
        let detector = MoodDetector::new(&config).unwrap();

        let mut features = AudioFeatures::default();
        features.key = Some("Am".to_string());
        features.rms_energy = 0.8;

        let moods = detector.detect(&features).unwrap();
        assert!(!moods.is_empty());
    }
}
