use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Severity {
    Info,
    Low,
    Medium,
    High,
    Critical,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum FindingType {
    HardcodedSecret,
    PrivateKey,
    DatabaseUrl,
    DeprecatedApi,
    RuntimeAnomaly,
    DatabaseAnomaly,
    InfrastructureRisk,
    SensitiveLogExposure,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum FindingCategory {
    SecretExposure,
    LegacyApi,
    RuntimeBehavior,
    DatabaseActivity,
    Infrastructure,
    Logging,
    Unknown,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum FindingSource {
    RustScanner,
    PythonAnalyzer,
    MockData,
    BobAnalysis,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Finding {
    pub finding_id: String,
    pub repo_name: String,
    pub finding_type: FindingType,
    pub category: FindingCategory,
    pub severity_hint: Severity,
    pub source: FindingSource,
    pub file: String,
    pub line: u32,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub endpoint: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub database_table: Option<String>,
    pub evidence: String,
    pub masked_value: String,
    pub timestamp: DateTime<Utc>,
}

impl Finding {
    pub fn new(
        finding_id: String,
        repo_name: String,
        finding_type: FindingType,
        category: FindingCategory,
        severity_hint: Severity,
        file: String,
        line: u32,
        evidence: String,
        masked_value: String,
    ) -> Self {
        Self {
            finding_id,
            repo_name,
            finding_type,
            category,
            severity_hint,
            source: FindingSource::RustScanner,
            file,
            line,
            endpoint: None,
            database_table: None,
            evidence,
            masked_value,
            timestamp: Utc::now(),
        }
    }

    pub fn with_endpoint(mut self, endpoint: String) -> Self {
        self.endpoint = Some(endpoint);
        self
    }

    pub fn with_database_table(mut self, table: String) -> Self {
        self.database_table = Some(table);
        self
    }
}

pub fn mask_secret(secret: &str) -> String {
    if secret.len() <= 8 {
        return "****".to_string();
    }
    let visible_chars = 4;
    let prefix = &secret[..visible_chars.min(secret.len())];
    let suffix = &secret[secret.len().saturating_sub(visible_chars)..];
    format!("{}****{}", prefix, suffix)
}

// Made with Bob
