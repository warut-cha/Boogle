use regex::Regex;
use anyhow::Result;
use crate::models::{Finding, FindingType, FindingCategory, Severity, mask_secret};
use crate::file_walker::ScannableFile;

pub struct SecretScanner {
    patterns: Vec<SecretPattern>,
}

struct SecretPattern {
    name: &'static str,
    regex: Regex,
    finding_type: FindingType,
    severity: Severity,
}

impl SecretScanner {
    pub fn new() -> Result<Self> {
        let patterns = vec![
            SecretPattern {
                name: "API Key",
                regex: Regex::new(r#"(?i)(api[_-]?key|apikey)\s*[:=]\s*["']?([a-zA-Z0-9_\-]{20,}|sk_[a-zA-Z0-9_\-]{20,})["']?"#)?,
                finding_type: FindingType::HardcodedSecret,
                severity: Severity::High,
            },
            SecretPattern {
                name: "Secret Key",
                regex: Regex::new(r#"(?i)(secret[_-]?key|secretkey)\s*[:=]\s*["']?([a-zA-Z0-9_\-]{20,})["']?"#)?,
                finding_type: FindingType::HardcodedSecret,
                severity: Severity::High,
            },
            SecretPattern {
                name: "Access Token",
                regex: Regex::new(r#"(?i)(access[_-]?token|accesstoken)\s*[:=]\s*["']?([a-zA-Z0-9_\-]{20,})["']?"#)?,
                finding_type: FindingType::HardcodedSecret,
                severity: Severity::High,
            },
            SecretPattern {
                name: "Password",
                regex: Regex::new(r#"(?i)(password|passwd|pwd)\s*[:=]\s*["']([^"'\s]{8,})["']"#)?,
                finding_type: FindingType::HardcodedSecret,
                severity: Severity::High,
            },
            SecretPattern {
                name: "Authorization Bearer",
                regex: Regex::new(r#"(?i)authorization\s*[:=]\s*["']?bearer\s+([a-zA-Z0-9_\-\.]{20,})["']?"#)?,
                finding_type: FindingType::HardcodedSecret,
                severity: Severity::Critical,
            },
            SecretPattern {
                name: "Private Key",
                regex: Regex::new(r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----")?,
                finding_type: FindingType::PrivateKey,
                severity: Severity::Critical,
            },
            SecretPattern {
                name: "SSH Private Key",
                regex: Regex::new(r"-----BEGIN\s+OPENSSH\s+PRIVATE\s+KEY-----")?,
                finding_type: FindingType::PrivateKey,
                severity: Severity::Critical,
            },
            SecretPattern {
                name: "Database URL with credentials",
                regex: Regex::new(r#"(?i)(mongodb|mysql|postgresql|postgres)://([^:]+):([^@]+)@"#)?,
                finding_type: FindingType::DatabaseUrl,
                severity: Severity::Critical,
            },
            SecretPattern {
                name: "AWS Access Key",
                regex: Regex::new(r#"(?i)aws_access_key_id\s*[:=]\s*['"]?(AKIA[0-9A-Z]{16})['"]?"#)?,
                finding_type: FindingType::HardcodedSecret,
                severity: Severity::Critical,
            },
            SecretPattern {
                name: "AWS Secret Key",
                regex: Regex::new(r#"(?i)(aws[_-]?secret[_-]?access[_-]?key|aws_secret_key)\s*[:=]\s*['"]?([a-zA-Z0-9/+=]{40})['"]?"#)?,
                finding_type: FindingType::HardcodedSecret,
                severity: Severity::Critical,
            },
        ];

        Ok(Self { patterns })
    }

    pub fn scan(&self, file: &ScannableFile, finding_counter: &mut usize) -> Result<Vec<Finding>> {
        let content = file.read_content()?;
        let mut findings = Vec::new();

        for (line_num, line) in content.lines().enumerate() {
            for pattern in &self.patterns {
                if let Some(captures) = pattern.regex.captures(line) {
                    let secret_value = if captures.len() > 2 {
                        captures.get(2).map(|m| m.as_str()).unwrap_or("")
                    } else if captures.len() > 1 {
                        captures.get(1).map(|m| m.as_str()).unwrap_or("")
                    } else {
                        captures.get(0).map(|m| m.as_str()).unwrap_or("")
                    };

                    let masked = mask_secret(secret_value);
                    *finding_counter += 1;

                    let finding = Finding::new(
                        format!("FIND-{:03}", finding_counter),
                        file.repo_name.clone(),
                        pattern.finding_type.clone(),
                        FindingCategory::SecretExposure,
                        pattern.severity.clone(),
                        file.relative_path(),
                        (line_num + 1) as u32,
                        format!("Possible {} detected", pattern.name),
                        masked,
                    );

                    findings.push(finding);
                }
            }
        }

        Ok(findings)
    }
}

// Made with Bob
