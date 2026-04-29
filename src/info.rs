//! Information about FizzBuzz and its run conditions.

use std::sync::OnceLock;

use chrono::{DateTime, Utc};

/// The current release version of FizzBuzz.
pub const VERSION: &str = env!("CARGO_PKG_VERSION");

/// The application ID of the bot.
pub const BOT_APP_ID: u64 = 1303870147873996902;
/// The application ID of the prototype bot.
pub const PROTOTYPE_BOT_APP_ID: u64 = 1437156873722921053;

/// The time that the program started.
static START_TIME: OnceLock<DateTime<Utc>> = OnceLock::new();
/// Initializes the start time of the program.
pub fn init_start_time() {
    START_TIME.get_or_init(Utc::now);
}
/// Returns the start time of the program.
///
/// # Returns
///
/// - `DateTime<Utc>` - The start time.
pub fn start_time() -> DateTime<Utc> {
    *START_TIME.get().expect("Start time not initialized")
}

/// Returns the uptime of the program as a human-readable string.
///
/// # Returns
///
/// - `String` - The uptime.
pub fn get_uptime_string() -> String {
    let uptime = Utc::now() - start_time();
    let total_secs = uptime.num_seconds();
    let days = total_secs / 86400;
    let hours = (total_secs % 86400) / 3600;
    let minutes = (total_secs % 3600) / 60;
    let seconds = total_secs % 60;
    format!("{days} days, {hours} hours, {minutes} minutes, {seconds} seconds")
}

pub fn host() -> String {
    format!(
        "{} {}",
        sysinfo::System::name().unwrap_or_else(|| "Unknown".into()),
        sysinfo::System::os_version().unwrap_or_else(|| "".into())
    )
}
