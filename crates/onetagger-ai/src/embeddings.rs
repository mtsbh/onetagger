//! Semantic Embeddings Module
//!
//! Generates embeddings for better track matching

use anyhow::{Error, Result};
use crate::features::AudioFeatures;
use onetagger_tagger::Track;

/// Embedding generator for semantic matching
pub struct EmbeddingGenerator {}

impl EmbeddingGenerator {
    pub fn new() -> Self {
        Self {}
    }

    /// Generate embedding from audio features
    pub fn generate_audio_embedding(&self, features: &AudioFeatures) -> Result<Vec<f32>> {
        // TODO: Use ONNX model to generate embeddings
        // For now, create a simple feature vector
        let mut embedding = Vec::new();

        // Normalize features to 0-1 range
        embedding.push(features.bpm.unwrap_or(120.0) / 200.0);
        embedding.push(features.spectral_centroid / 5000.0);
        embedding.push(features.rms_energy);
        embedding.extend(&features.mfccs);

        Ok(embedding)
    }

    /// Generate text embedding from title/artist
    pub fn generate_text_embedding(&self, text: &str) -> Result<Vec<f32>> {
        // TODO: Use sentence transformer model
        // For now, simple hash-based embedding
        let mut embedding = vec![0.0; 384];  // Standard sentence embedding size

        for (i, ch) in text.chars().enumerate().take(384) {
            embedding[i] = (ch as u32 % 256) as f32 / 255.0;
        }

        Ok(embedding)
    }
}

impl Default for EmbeddingGenerator {
    fn default() -> Self {
        Self::new()
    }
}

/// Semantic matcher using embeddings
pub struct SemanticMatcher {
    generator: EmbeddingGenerator,
}

impl SemanticMatcher {
    pub fn new() -> Self {
        Self {
            generator: EmbeddingGenerator::new(),
        }
    }

    /// Calculate similarity between two tracks
    pub fn calculate_similarity(&self, track1: &Track, track2: &Track) -> Result<f32> {
        let text1 = format!("{} {}", track1.artists.join(" "), track1.title);
        let text2 = format!("{} {}", track2.artists.join(" "), track2.title);

        let emb1 = self.generator.generate_text_embedding(&text1)?;
        let emb2 = self.generator.generate_text_embedding(&text2)?;

        Ok(cosine_similarity(&emb1, &emb2))
    }
}

impl Default for SemanticMatcher {
    fn default() -> Self {
        Self::new()
    }
}

/// Calculate cosine similarity between two vectors
fn cosine_similarity(a: &[f32], b: &[f32]) -> f32 {
    if a.len() != b.len() {
        return 0.0;
    }

    let dot_product: f32 = a.iter().zip(b.iter()).map(|(x, y)| x * y).sum();
    let norm_a: f32 = a.iter().map(|x| x * x).sum::<f32>().sqrt();
    let norm_b: f32 = b.iter().map(|x| x * x).sum::<f32>().sqrt();

    if norm_a == 0.0 || norm_b == 0.0 {
        return 0.0;
    }

    (dot_product / (norm_a * norm_b)).clamp(0.0, 1.0)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cosine_similarity() {
        let a = vec![1.0, 0.0, 0.0];
        let b = vec![1.0, 0.0, 0.0];
        assert_eq!(cosine_similarity(&a, &b), 1.0);

        let c = vec![1.0, 0.0];
        let d = vec![0.0, 1.0];
        assert_eq!(cosine_similarity(&c, &d), 0.0);
    }
}
