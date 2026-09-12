//! Cloud-provider API key storage via OS keychain (`keyring` crate) for Live Copilot.
//!
//! Service name: `"adversaria-copilot"`.
//! Accounts: `"anthropic-api-key"` and `"deepseek-api-key"`.
//!
//! Never log or leak the key.

use std::sync::Mutex;

const SERVICE: &str = "adversaria-copilot";
const ANTHROPIC_ACCOUNT: &str = "anthropic-api-key";
const DEEPSEEK_ACCOUNT: &str = "deepseek-api-key";
const ANTHROPIC_DEV_FILE: &str = "dev-copilot-key";
const DEEPSEEK_DEV_FILE: &str = "dev-copilot-deepseek-key";

/// Process-wide cache: outer None = not yet loaded from keychain/disk,
/// Some(None) = checked and no key found, Some(Some(k)) = cached key.
static KEY_CACHE: Mutex<Option<Option<String>>> = Mutex::new(None);
static DEEPSEEK_KEY_CACHE: Mutex<Option<Option<String>>> = Mutex::new(None);

/// Set the Anthropic API key in the OS keychain.
/// Rejects empty/blank keys with "API key is empty.".
pub fn set_api_key(key: &str) -> Result<(), String> {
    set_provider_api_key(key, ANTHROPIC_ACCOUNT, ANTHROPIC_DEV_FILE, &KEY_CACHE)
}

/// Set the DeepSeek API key in the OS keychain.
pub fn set_deepseek_api_key(key: &str) -> Result<(), String> {
    set_provider_api_key(
        key,
        DEEPSEEK_ACCOUNT,
        DEEPSEEK_DEV_FILE,
        &DEEPSEEK_KEY_CACHE,
    )
}

fn set_provider_api_key(
    key: &str,
    account: &str,
    dev_file: &str,
    cache: &Mutex<Option<Option<String>>>,
) -> Result<(), String> {
    let trimmed = key.trim();
    if trimmed.is_empty() {
        return Err("API key is empty.".to_string());
    }

    let entry = keyring::Entry::new(SERVICE, account).map_err(|e| format!("keyring open: {e}"))?;

    let res = entry.set_password(trimmed);
    #[cfg(debug_assertions)]
    {
        if let Err(e) = res {
            dev_write_key(dev_file, trimmed)
                .map_err(|de| format!("keyring write: {e}; dev write: {de}"))?;
        }
    }
    #[cfg(not(debug_assertions))]
    {
        res.map_err(|e| format!("keyring write: {e}"))?;
    }

    *cache.lock().unwrap() = Some(Some(trimmed.to_string()));
    Ok(())
}

/// Read the Anthropic API key from cache, OS keychain, or debug dev-file.
/// Returns `Ok(None)` if no key is stored.
pub fn get_api_key() -> Result<Option<String>, String> {
    get_provider_api_key(ANTHROPIC_ACCOUNT, ANTHROPIC_DEV_FILE, &KEY_CACHE)
}

/// Read the DeepSeek API key from cache, OS keychain, or debug dev-file.
pub fn get_deepseek_api_key() -> Result<Option<String>, String> {
    get_provider_api_key(DEEPSEEK_ACCOUNT, DEEPSEEK_DEV_FILE, &DEEPSEEK_KEY_CACHE)
}

fn get_provider_api_key(
    account: &str,
    dev_file: &str,
    cache: &Mutex<Option<Option<String>>>,
) -> Result<Option<String>, String> {
    if let Some(cached) = cache.lock().unwrap().as_ref() {
        return Ok(cached.clone());
    }

    let entry = keyring::Entry::new(SERVICE, account).map_err(|e| format!("keyring open: {e}"))?;

    let loaded = match entry.get_password() {
        Ok(k) => Some(k),
        Err(keyring::Error::NoEntry) => {
            #[cfg(debug_assertions)]
            {
                dev_read_key(dev_file)?
            }
            #[cfg(not(debug_assertions))]
            {
                None
            }
        }
        Err(e) => {
            #[cfg(debug_assertions)]
            {
                if let Ok(Some(k)) = dev_read_key(dev_file) {
                    Some(k)
                } else {
                    return Err(format!("keyring read: {e}"));
                }
            }
            #[cfg(not(debug_assertions))]
            {
                return Err(format!("keyring read: {e}"));
            }
        }
    };

    *cache.lock().unwrap() = Some(loaded.clone());
    Ok(loaded)
}

/// Check if an Anthropic API key is saved.
pub fn has_api_key() -> Result<bool, String> {
    Ok(get_api_key()?.is_some())
}

/// Check if a DeepSeek API key is saved.
pub fn has_deepseek_api_key() -> Result<bool, String> {
    Ok(get_deepseek_api_key()?.is_some())
}

/// Delete the stored Anthropic API key.
/// Returns `Ok(())` if already gone (NoEntry).
pub fn clear_api_key() -> Result<(), String> {
    clear_provider_api_key(ANTHROPIC_ACCOUNT, ANTHROPIC_DEV_FILE, &KEY_CACHE)
}

/// Delete the stored DeepSeek API key.
pub fn clear_deepseek_api_key() -> Result<(), String> {
    clear_provider_api_key(DEEPSEEK_ACCOUNT, DEEPSEEK_DEV_FILE, &DEEPSEEK_KEY_CACHE)
}

fn clear_provider_api_key(
    account: &str,
    dev_file: &str,
    cache: &Mutex<Option<Option<String>>>,
) -> Result<(), String> {
    let entry = keyring::Entry::new(SERVICE, account).map_err(|e| format!("keyring open: {e}"))?;

    let res = match entry.delete_credential() {
        Ok(()) => Ok(()),
        Err(keyring::Error::NoEntry) => Ok(()),
        Err(e) => {
            #[cfg(debug_assertions)]
            {
                let _ = e;
                Ok(())
            }
            #[cfg(not(debug_assertions))]
            {
                Err(format!("keyring delete: {e}"))
            }
        }
    };

    #[cfg(debug_assertions)]
    {
        let path = crate::config::app_data_dir().join(dev_file);
        let _ = std::fs::remove_file(path);
    }

    *cache.lock().unwrap() = Some(None);
    res
}

#[cfg(debug_assertions)]
fn dev_read_key(filename: &str) -> Result<Option<String>, String> {
    let path = crate::config::app_data_dir().join(filename);
    if let Ok(existing) = std::fs::read_to_string(&path) {
        let trimmed = existing.trim();
        if !trimmed.is_empty() {
            return Ok(Some(trimmed.to_string()));
        }
    }
    Ok(None)
}

#[cfg(debug_assertions)]
fn dev_write_key(filename: &str, key: &str) -> Result<(), String> {
    let path = crate::config::app_data_dir().join(filename);
    std::fs::write(&path, key).map_err(|e| {
        format!(
            "Could not store the dev copilot key at {}: {e}",
            path.display()
        )
    })?;
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let _ = std::fs::set_permissions(&path, std::fs::Permissions::from_mode(0o600));
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn set_api_key_rejects_empty_or_whitespace() {
        assert_eq!(set_api_key("").unwrap_err(), "API key is empty.");
        assert_eq!(set_api_key("   \n\t  ").unwrap_err(), "API key is empty.");
    }

    #[test]
    fn cache_round_trip() {
        *KEY_CACHE.lock().unwrap() = Some(Some("sk-ant-test-123".to_string()));
        assert_eq!(get_api_key().unwrap(), Some("sk-ant-test-123".to_string()));
        assert!(has_api_key().unwrap());

        *KEY_CACHE.lock().unwrap() = Some(None);
        assert_eq!(get_api_key().unwrap(), None);
        assert!(!has_api_key().unwrap());
    }

    #[test]
    fn deepseek_cache_is_independent() {
        *KEY_CACHE.lock().unwrap() = Some(Some("sk-ant-test-123".to_string()));
        *DEEPSEEK_KEY_CACHE.lock().unwrap() = Some(Some("sk-deepseek-test".to_string()));
        assert_eq!(get_api_key().unwrap().as_deref(), Some("sk-ant-test-123"));
        assert_eq!(
            get_deepseek_api_key().unwrap().as_deref(),
            Some("sk-deepseek-test")
        );
        assert!(has_deepseek_api_key().unwrap());
    }
}
