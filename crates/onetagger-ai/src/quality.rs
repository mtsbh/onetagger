//! Quality Control Module
//!
//! Validates track metadata and suggests corrections

use anyhow::{Error, Result};
use serde::{Serialize, Deserialize};
use onetagger_tagger::Track;
use crate::features::AudioFeatures;

/// Quality control checker
pub struct QualityControl {
    strictness: f32,
}

impl QualityControl {
    pub fn new(strictness: f32) -> Self {
        Self { strictness }
    }

    /// Validate a track's metadata
    pub fn validate(&self, track: &Track, features: &AudioFeatures) -> Result<ValidationResult> {
        let mut issues = Vec::new();
        let mut suggestions = Vec::new();

        // Check BPM consistency
        if let (Some(tagged_bpm), Some(detected_bpm)) = (track.bpm, features.bpm) {
            let diff = (tagged_bpm as f32 - detected_bpm).abs();
            if diff > 5.0 {
                issues.push(ValidationIssue {
                    severity: IssueSeverity::Warning,
                    field: "BPM".to_string(),
                    message: format!("Tagged BPM ({}) differs from detected ({})", tagged_bpm, detected_bpm),
                });
                suggestions.push(format!("Consider updating BPM to {}", detected_bpm));
            }
        }

        // Check for missing critical tags
        if track.genres.is_empty() {
            issues.push(ValidationIssue {
                severity: IssueSeverity::Error,
                field: "Genre".to_string(),
                message: "No genre tags found".to_string(),
            });
        }

        if track.artists.is_empty() {
            issues.push(ValidationIssue {
                severity: IssueSeverity::Error,
                field: "Artist".to_string(),
                message: "No artist information".to_string(),
            });
        }

        // Calculate quality score
        let completeness = self.calculate_completeness(track);
        let consistency = if issues.is_empty() { 1.0 } else {
            1.0 - (issues.len() as f32 * 0.1)
        };
        let quality_score = (completeness + consistency) / 2.0;

        Ok(ValidationResult {
            quality_score,
            completeness,
            issues,
            suggestions,
        })
    }

    /// Calculate metadata completeness (0-1)
    fn calculate_completeness(&self, track: &Track) -> f32 {
        let mut score = 0.0;
        let mut max_score = 0.0;

        // Critical fields (weight: 2)
        max_score += 2.0;
        if !track.artists.is_empty() { score += 2.0; }

        max_score += 2.0;
        if !track.genres.is_empty() { score += 2.0; }

        // Important fields (weight: 1)
        max_score += 1.0;
        if track.bpm.is_some() { score += 1.0; }

        max_score += 1.0;
        if track.key.is_some() { score += 1.0; }

        max_score += 1.0;
        if track.label.is_some() { score += 1.0; }

        max_score += 1.0;
        if track.release_date.is_some() || track.release_year.is_some() { score += 1.0; }

        max_score += 1.0;
        if track.art.is_some() { score += 1.0; }

        if max_score > 0.0 {
            score / max_score
        } else {
            0.0
        }
    }
}

/// Validation result
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ValidationResult {
    pub quality_score: f32,
    pub completeness: f32,
    pub issues: Vec<ValidationIssue>,
    pub suggestions: Vec<String>,
}

/// A validation issue
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ValidationIssue {
    pub severity: IssueSeverity,
    pub field: String,
    pub message: String,
}

/// Issue severity
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "lowercase")]
pub enum IssueSeverity {
    Error,
    Warning,
    Info,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_quality_control() {
        let qc = QualityControl::new(0.7);
        assert_eq!(qc.strictness, 0.7);
    }
}
