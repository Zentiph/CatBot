//! The entrypoint of FizzBuzz.

use clap::{ArgAction, Parser};

/// Run FizzBuzz with optional arguments
#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    /// Launch the bot in debug mode for more verbose logging.
    #[arg(short, long, action = ArgAction::SetTrue, default_value_t = false)]
    debug: bool,

    /// Path to the file where logs will be written.
    #[arg(long)]
    log_file: Option<String>,

    /// Enable/disable console logging. Defaults to true.
    #[arg(long, action = ArgAction::SetFalse, default_value_t = true)]
    console_logging: bool,

    /// Enable/disable colored console logging via ANSI codes. Defaults to true.
    #[arg(long, action = ArgAction::SetFalse, default_value_t = true)]
    colored_logs: bool,

    /// Show the environment variables related to the bot on startup.
    #[arg(long, action = ArgAction::SetTrue, default_value_t = false)]
    show_env: bool,

    /// A token to override the one in the environment. Use for testing under a different application.
    #[arg(long, default_value = None)]
    token_override: Option<String>,
}

#[tokio::main]
async fn main() {
    let args = Args::parse();
}
