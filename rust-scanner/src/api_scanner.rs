use regex::Regex;
use anyhow::Result;
use crate::models::{Finding, FindingType, FindingCategory, Severity};
use crate::file_walker::ScannableFile;

pub struct ApiScanner {
    patterns: Vec<ApiPattern>,
}

struct ApiPattern {
    name: &'static str,
    regex: Regex,
    severity: Severity,
}

impl ApiScanner {
    pub fn new() -> Result<Self> {
        let patterns = vec![
            ApiPattern {
                name: "Deprecated API v1",
                regex: Regex::new(r#"(?i)["'`](/api/v1/[a-zA-Z0-9_\-/]+)["'`]"#)?,
                severity: Severity::Medium,
            },
            ApiPattern {
                name: "Legacy endpoint",
                regex: Regex::new(r#"(?i)["'`](/legacy/[a-zA-Z0-9_\-/]+)["'`]"#)?,
                severity: Severity::Medium,
            },
            ApiPattern {
                name: "Deprecated endpoint",
                regex: Regex::new(r#"(?i)["'`](/deprecated/[a-zA-Z0-9_\-/]+)["'`]"#)?,
                severity: Severity::Medium,
            },
            ApiPattern {
                name: "Export endpoint",
                regex: Regex::new(r#"(?i)["'`](/[a-zA-Z0-9_\-/]*(export|download|dump|backup)[a-zA-Z0-9_\-/]*)["'`]"#)?,
                severity: Severity::High,
            },
            ApiPattern {
                name: "Old API route",
                regex: Regex::new(r#"(?i)["'`](/old/[a-zA-Z0-9_\-/]+)["'`]"#)?,
                severity: Severity::Medium,
            },
            ApiPattern {
                name: "Route decorator with deprecated path",
                regex: Regex::new(r#"(?i)@(app\.route|router\.(get|post|put|delete))\s*\(\s*["'`](/api/v1/[a-zA-Z0-9_\-/]+)["'`]"#)?,
                severity: Severity::Medium,
            },
            ApiPattern {
                name: "Route decorator with export path",
                regex: Regex::new(r#"(?i)@(app\.route|router\.(get|post|put|delete))\s*\(\s*["'`](/[a-zA-Z0-9_\-/]*(export|download|dump)[a-zA-Z0-9_\-/]*)["'`]"#)?,
                severity: Severity::High,
            },
        ];

        Ok(Self { patterns })
    }

    pub fn scan(&self, file: &ScannableFile, finding_counter: &mut usize) -> Result<Vec<Finding>> {
        let content = file.read_content()?;
        let mut findings = Vec::new();

        // Only scan code files that might contain API definitions
        let file_path = file.relative_path();
        let is_code_file = file_path.ends_with(".py") 
            || file_path.ends_with(".js") 
            || file_path.ends_with(".ts")
            || file_path.ends_with(".go")
            || file_path.ends_with(".java")
            || file_path.ends_with(".rb")
            || file_path.ends_with(".php");

        if !is_code_file {
            return Ok(findings);
        }

        for (line_num, line) in content.lines().enumerate() {
            for pattern in &self.patterns {
                if let Some(captures) = pattern.regex.captures(line) {
                    let endpoint = captures.get(1)
                        .or_else(|| captures.get(4))
                        .or_else(|| captures.get(3))
                        .map(|m| m.as_str())
                        .unwrap_or("");

                    *finding_counter += 1;

                    let finding = Finding::new(
                        format!("FIND-{:03}", finding_counter),
                        file.repo_name.clone(),
                        FindingType::DeprecatedApi,
                        FindingCategory::LegacyApi,
                        pattern.severity.clone(),
                        file.relative_path(),
                        (line_num + 1) as u32,
                        format!("{} found", pattern.name),
                        endpoint.to_string(),
                    ).with_endpoint(endpoint.to_string());

                    findings.push(finding);
                }
            }
        }

        Ok(findings)
    }
}

// Made with Bob
