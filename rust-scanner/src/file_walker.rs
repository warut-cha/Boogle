use std::path::{Path, PathBuf};
use walkdir::WalkDir;
use anyhow::Result;

pub struct FileWalker {
    paths: Vec<PathBuf>,
}

impl FileWalker {
    pub fn new(paths: Vec<PathBuf>) -> Self {
        Self { paths }
    }

    pub fn walk(&self) -> Result<Vec<ScannableFile>> {
        let mut files = Vec::new();

        for path in &self.paths {
            if !path.exists() {
                eprintln!("Warning: Path does not exist: {}", path.display());
                continue;
            }

            for entry in WalkDir::new(path)
                .follow_links(false)
                .into_iter()
                .filter_map(|e| e.ok())
            {
                let path = entry.path();
                
                if !path.is_file() {
                    continue;
                }

                // Skip binary files and common non-text files
                if let Some(ext) = path.extension() {
                    let ext_str = ext.to_string_lossy().to_lowercase();
                    if matches!(
                        ext_str.as_str(),
                        "exe" | "dll" | "so" | "dylib" | "bin" | "jpg" | "jpeg" | "png" | "gif" | "pdf" | "zip" | "tar" | "gz"
                    ) {
                        continue;
                    }
                }

                // Determine repo name from path
                let repo_name = self.extract_repo_name(path);

                files.push(ScannableFile {
                    path: path.to_path_buf(),
                    repo_name,
                });
            }
        }

        Ok(files)
    }

    fn extract_repo_name(&self, file_path: &Path) -> String {
        // Find which base path this file belongs to
        for base_path in &self.paths {
            if file_path.starts_with(base_path) {
                if let Some(name) = base_path.file_name() {
                    return name.to_string_lossy().to_string();
                }
            }
        }
        
        // Fallback: use the first directory component
        file_path
            .components()
            .next()
            .and_then(|c| c.as_os_str().to_str())
            .unwrap_or("unknown")
            .to_string()
    }
}

#[derive(Debug, Clone)]
pub struct ScannableFile {
    pub path: PathBuf,
    pub repo_name: String,
}

impl ScannableFile {
    pub fn read_content(&self) -> Result<String> {
        std::fs::read_to_string(&self.path)
            .map_err(|e| anyhow::anyhow!("Failed to read {}: {}", self.path.display(), e))
    }

    pub fn relative_path(&self) -> String {
        self.path
            .to_string_lossy()
            .replace('\\', "/")
    }
}

// Made with Bob
