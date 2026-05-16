use regex::Regex;
use anyhow::Result;
use crate::models::{Finding, FindingType, FindingCategory, Severity};
use crate::file_walker::ScannableFile;

pub struct InfraScanner {
    patterns: Vec<InfraPattern>,
}

struct InfraPattern {
    name: &'static str,
    regex: Regex,
    severity: Severity,
    file_pattern: Option<&'static str>,
}

impl InfraScanner {
    pub fn new() -> Result<Self> {
        let patterns = vec![
            InfraPattern {
                name: "Dockerfile running as root",
                regex: Regex::new(r"(?i)^USER\s+root\s*$")?,
                severity: Severity::Medium,
                file_pattern: Some("Dockerfile"),
            },
            InfraPattern {
                name: "Dockerfile without USER directive",
                regex: Regex::new(r"(?i)^FROM\s+")?,
                severity: Severity::Low,
                file_pattern: Some("Dockerfile"),
            },
            InfraPattern {
                name: "Docker Compose exposed database port",
                regex: Regex::new(r#"(?i)ports:\s*-\s*["']?(3306|5432|27017|6379)"#)?,
                severity: Severity::High,
                file_pattern: Some("docker-compose"),
            },
            InfraPattern {
                name: "Privileged container",
                regex: Regex::new(r"(?i)privileged:\s*true")?,
                severity: Severity::High,
                file_pattern: Some("docker-compose"),
            },
            InfraPattern {
                name: "GitHub Actions secret exposure",
                regex: Regex::new(r"(?i)(echo|print|console\.log|logger)\s+.*\$\{\{\s*secrets\.")?,
                severity: Severity::Critical,
                file_pattern: Some(".yml"),
            },
            InfraPattern {
                name: "Gateway exposing deprecated endpoint",
                regex: Regex::new(r#"(?i)(path|route|location):\s*["']?(/api/v1/|/legacy/|/deprecated/)"#)?,
                severity: Severity::Medium,
                file_pattern: Some("gateway"),
            },
            InfraPattern {
                name: "Exposed admin endpoint",
                regex: Regex::new(r#"(?i)(path|route|location):\s*["']?(/admin|/console|/debug)"#)?,
                severity: Severity::High,
                file_pattern: None,
            },
            InfraPattern {
                name: "Insecure protocol in config",
                regex: Regex::new(r#"(?i)(url|endpoint|host):\s*["']?http://[^"'\s]+"#)?,
                severity: Severity::Medium,
                file_pattern: None,
            },
        ];

        Ok(Self { patterns })
    }

    pub fn scan(&self, file: &ScannableFile, finding_counter: &mut usize) -> Result<Vec<Finding>> {
        let content = file.read_content()?;
        let mut findings = Vec::new();

        let file_path = file.relative_path();
        let file_name = file.path.file_name()
            .and_then(|n| n.to_str())
            .unwrap_or("");

        // Only scan infrastructure files
        let is_infra_file = file_name.contains("Dockerfile")
            || file_name.contains("docker-compose")
            || file_name.ends_with(".yml")
            || file_name.ends_with(".yaml")
            || file_name.contains("gateway")
            || file_name.contains("config");

        if !is_infra_file {
            return Ok(findings);
        }

        // Special handling for Dockerfile USER directive check
        let mut has_user_directive = false;
        let mut dockerfile_from_line = None;

        for (line_num, line) in content.lines().enumerate() {
            let trimmed = line.trim();
            
            if file_name.contains("Dockerfile") {
                if trimmed.to_uppercase().starts_with("FROM ") {
                    dockerfile_from_line = Some(line_num);
                }
                if trimmed.to_uppercase().starts_with("USER ") && !trimmed.to_uppercase().contains("USER ROOT") {
                    has_user_directive = true;
                }
            }

            for pattern in &self.patterns {
                // Skip if file pattern doesn't match
                if let Some(file_pat) = pattern.file_pattern {
                    if !file_name.contains(file_pat) && !file_path.contains(file_pat) {
                        continue;
                    }
                }

                // Skip the "without USER directive" check during line scanning
                if pattern.name == "Dockerfile without USER directive" {
                    continue;
                }

                if let Some(captures) = pattern.regex.captures(line) {
                    let evidence_value = captures.get(1)
                        .or_else(|| captures.get(0))
                        .map(|m| m.as_str())
                        .unwrap_or("");

                    *finding_counter += 1;

                    let mut finding = Finding::new(
                        format!("FIND-{:03}", finding_counter),
                        file.repo_name.clone(),
                        FindingType::InfrastructureRisk,
                        FindingCategory::Infrastructure,
                        pattern.severity.clone(),
                        file.relative_path(),
                        (line_num + 1) as u32,
                        format!("{} detected", pattern.name),
                        evidence_value.to_string(),
                    );

                    // Extract endpoint if present
                    if pattern.name.contains("endpoint") || pattern.name.contains("Gateway") {
                        if let Some(endpoint_match) = captures.get(2) {
                            finding = finding.with_endpoint(endpoint_match.as_str().to_string());
                        }
                    }

                    findings.push(finding);
                }
            }
        }

        // Check for missing USER directive in Dockerfile
        if file_name.contains("Dockerfile") && !has_user_directive {
            if let Some(from_line) = dockerfile_from_line {
                *finding_counter += 1;
                let finding = Finding::new(
                    format!("FIND-{:03}", finding_counter),
                    file.repo_name.clone(),
                    FindingType::InfrastructureRisk,
                    FindingCategory::Infrastructure,
                    Severity::Low,
                    file.relative_path(),
                    (from_line + 1) as u32,
                    "Dockerfile missing USER directive (runs as root by default)".to_string(),
                    "No USER directive found".to_string(),
                );
                findings.push(finding);
            }
        }

        Ok(findings)
    }
}

// Made with Bob
