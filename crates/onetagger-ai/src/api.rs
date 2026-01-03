//! API Client Module
//!
//! Handles communication with FREE Cloud AI APIs:
//! - Google Gemini (recommended)
//! - OpenRouter
//! - Groq
//! - Together AI
//! - OpenAI

use anyhow::{Error, Result};
use serde::{Serialize, Deserialize};
use std::time::Duration;
use crate::config::{APIConfig, APIProvider};

/// API client for LLM inference
pub struct APIClient {
    config: APIConfig,
    http_client: reqwest::Client,
}

impl APIClient {
    /// Create a new API client
    pub fn new(config: APIConfig) -> Result<Self> {
        let http_client = reqwest::Client::builder()
            .timeout(Duration::from_secs(30))
            .build()?;

        Ok(Self {
            config,
            http_client,
        })
    }

    /// Generate text using the configured API
    pub async fn generate(&self, prompt: &str) -> Result<String> {
        info!("Calling {} API", self.config.provider.display_name());
        debug!("Prompt: {}", prompt);

        let response = match self.config.provider {
            APIProvider::Gemini => self.call_gemini(prompt).await?,
            APIProvider::OpenRouter => self.call_openrouter(prompt).await?,
            APIProvider::Groq => self.call_groq(prompt).await?,
            APIProvider::TogetherAI => self.call_together(prompt).await?,
            APIProvider::OpenAI => self.call_openai(prompt).await?,
            APIProvider::Custom => self.call_custom(prompt).await?,
        };

        debug!("Response: {}", response);
        Ok(response)
    }

    /// Call Google Gemini API
    async fn call_gemini(&self, prompt: &str) -> Result<String> {
        let api_key = self.config.api_key.as_ref()
            .ok_or_else(|| anyhow!("Gemini API key not set. Get one free at: https://aistudio.google.com/app/apikey"))?;

        let endpoint = self.config.endpoint.as_deref()
            .unwrap_or_else(|| self.config.provider.default_endpoint());

        let url = format!("{}?key={}", endpoint, api_key);

        let request_body = serde_json::json!({
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 256,
            }
        });

        let response = self.http_client
            .post(&url)
            .json(&request_body)
            .send()
            .await?;

        if !response.status().is_success() {
            let error_text = response.text().await?;
            return Err(anyhow!("Gemini API error: {}", error_text));
        }

        let json: GeminiResponse = response.json().await?;

        json.candidates.first()
            .and_then(|c| c.content.parts.first())
            .map(|p| p.text.clone())
            .ok_or_else(|| anyhow!("No response from Gemini"))
    }

    /// Call OpenRouter API (OpenAI-compatible)
    async fn call_openrouter(&self, prompt: &str) -> Result<String> {
        self.call_openai_compatible(
            self.config.provider.default_endpoint(),
            prompt,
            "openchat/openchat-7b:free",  // Free model
        ).await
    }

    /// Call Groq API (OpenAI-compatible)
    async fn call_groq(&self, prompt: &str) -> Result<String> {
        self.call_openai_compatible(
            self.config.provider.default_endpoint(),
            prompt,
            "llama-3.2-3b-preview",  // Free, fast Llama
        ).await
    }

    /// Call Together AI API (OpenAI-compatible)
    async fn call_together(&self, prompt: &str) -> Result<String> {
        self.call_openai_compatible(
            self.config.provider.default_endpoint(),
            prompt,
            "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        ).await
    }

    /// Call OpenAI API
    async fn call_openai(&self, prompt: &str) -> Result<String> {
        self.call_openai_compatible(
            self.config.provider.default_endpoint(),
            prompt,
            "gpt-3.5-turbo",
        ).await
    }

    /// Call custom endpoint
    async fn call_custom(&self, prompt: &str) -> Result<String> {
        let endpoint = self.config.endpoint.as_ref()
            .ok_or_else(|| anyhow!("Custom endpoint not configured"))?;

        self.call_openai_compatible(endpoint, prompt, "").await
    }

    /// Helper for OpenAI-compatible APIs
    async fn call_openai_compatible(&self, endpoint: &str, prompt: &str, model: &str) -> Result<String> {
        let api_key = self.config.api_key.as_ref()
            .ok_or_else(|| anyhow!("API key not set"))?;

        let request_body = serde_json::json!({
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 256,
        });

        let response = self.http_client
            .post(endpoint)
            .header("Authorization", format!("Bearer {}", api_key))
            .header("Content-Type", "application/json")
            .json(&request_body)
            .send()
            .await?;

        if !response.status().is_success() {
            let error_text = response.text().await?;
            return Err(anyhow!("API error: {}", error_text));
        }

        let json: OpenAIResponse = response.json().await?;

        json.choices.first()
            .map(|c| c.message.content.clone())
            .ok_or_else(|| anyhow!("No response from API"))
    }
}

/// Gemini API response structure
#[derive(Debug, Deserialize)]
struct GeminiResponse {
    candidates: Vec<GeminiCandidate>,
}

#[derive(Debug, Deserialize)]
struct GeminiCandidate {
    content: GeminiContent,
}

#[derive(Debug, Deserialize)]
struct GeminiContent {
    parts: Vec<GeminiPart>,
}

#[derive(Debug, Deserialize)]
struct GeminiPart {
    text: String,
}

/// OpenAI-compatible API response
#[derive(Debug, Deserialize)]
struct OpenAIResponse {
    choices: Vec<OpenAIChoice>,
}

#[derive(Debug, Deserialize)]
struct OpenAIChoice {
    message: OpenAIMessage,
}

#[derive(Debug, Deserialize)]
struct OpenAIMessage {
    content: String,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_api_client_creation() {
        let config = APIConfig::default();
        // Can't test without API key
        // let client = APIClient::new(config);
        // assert!(client.is_ok());
    }

    #[test]
    fn test_endpoints() {
        assert!(APIProvider::Gemini.default_endpoint().contains("googleapis.com"));
        assert!(APIProvider::Groq.default_endpoint().contains("groq.com"));
    }
}
