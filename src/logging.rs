use std::fs::OpenOptions;

use serenity::all::{CommandInteraction, ResolvedValue};
use tracing::{debug, info};
use tracing_subscriber::{EnvFilter, Layer, fmt, layer::SubscriberExt, util::SubscriberInitExt};

/// The format for logging timestamps.
const TIME_FORMAT: &str = "%Y-%m-%d %H:%M:%S";

/// Configures the logging setup for FizzBuzz.
///
/// # Arguments
///
/// - `debug_mode` (`bool`) - Whether to enable debug mode (more verbose logging).
/// - `log_file` (`Option<String>`) - The file to log to, if any.
/// - `console_logging` (`bool`) - Whether to enable console logging.
/// - `colored_logs` (`bool`) - Whether to color console logs.
///
/// # Returns
///
/// - `anyhow::Result<()>` - The result of the operation.
///
/// # Errors
///
/// Returns an error if the logging setup fails.
pub fn config_tracing(
    debug_mode: bool,
    log_file: Option<String>,
    console_logging: bool,
    colored_logs: bool,
) -> anyhow::Result<()> {
    let level = if debug_mode { "debug" } else { "info" };
    let filter = EnvFilter::new(level);

    let mut layers: Vec<Box<dyn Layer<_> + Send + Sync>> = Vec::new();

    if let Some(log_file) = log_file {
        let file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(log_file)?;
        file.set_len(0)?;

        layers.push(
            fmt::layer()
                .with_target(true)
                .with_file(true)
                .with_line_number(true)
                .with_timer(fmt::time::ChronoLocal::new(TIME_FORMAT.to_string()))
                .with_ansi(false) // file logging should never use ANSI
                .with_writer(file)
                .boxed(),
        );
    }

    if console_logging {
        layers.push(
            fmt::layer()
                .with_target(true)
                .with_file(true)
                .with_line_number(true)
                .with_timer(fmt::time::ChronoLocal::new(TIME_FORMAT.to_string()))
                .with_ansi(colored_logs)
                .boxed(),
        );
    }

    tracing_subscriber::registry()
        .with(filter)
        .with(layers)
        .init();

    info!(
        "FizzBuzz logging config: debug={debug_mode}, console_logging={console_logging}, colored_logs={colored_logs}"
    );

    Ok(())
}

/// Log a command group setup.
///
/// # Arguments
///
/// - `name` (`&str`) - The name of the command group.
pub fn log_command_group_setup(name: &str) {
    info!("{name} command group loaded");
}

/// Log an app command interaction.
///
/// This will only log if the `debug` feature is enabled.
///
/// # Arguments
///
/// - `interaction` (`&CommandInteraction`) - The interaction instance of the command.
pub fn log_app_command(interaction: &CommandInteraction) {
    // don't build if debug isn't enabled
    if !tracing::enabled!(tracing::Level::DEBUG) {
        return;
    }

    let command_name = &interaction.data.name;

    let params = interaction
        .data
        .options()
        .iter()
        .map(|opt| {
            let value = match &opt.value {
                ResolvedValue::String(s) => format!("{s:?}"),
                ResolvedValue::Integer(i) => format!("{i:?}"),
                ResolvedValue::Number(n) => format!("{n:?}"),
                ResolvedValue::Boolean(b) => format!("{b:?}"),
                ResolvedValue::User(u, _) => format!("{:?}", u.name),
                ResolvedValue::Channel(c) => format!("{:?}", c.name),
                ResolvedValue::Role(r) => format!("{:?}", r.name),
                ResolvedValue::Attachment(a) => format!("{:?}", a.filename),
                _ => "unknown".to_string(),
            };
            format!("{}={}", opt.name, value)
        })
        .collect::<Vec<_>>()
        .join(" ");

    let user = &interaction.user;

    debug!("/{command_name} {params} invoked by {user}");
}
