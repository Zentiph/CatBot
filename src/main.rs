//! The entrypoint of FizzBuzz.

use clap::{ArgAction, Parser};
use dotenvy::dotenv;
use envy::from_env;
use fizzbuzz::{commands, logging};
use serde::Deserialize;
use serenity::{
    Client,
    all::{ActivityData, Command, Context, EventHandler, GatewayIntents, Interaction, Ready},
    async_trait,
};
use tracing::{error, info, warn};

/// The environment variables required for FizzBuzz to run.
///
/// # Fields
///
/// - `token` (`String`) - The Discord bot token.
/// - `db_dir` (`String`) - The path to the directory where the bot's DBs are stored.
#[derive(Debug, Deserialize)]
struct Environment {
    token: String,
    db_dir: String,
}

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

    /// A token to override the one in the environment. Use for testing under a different application.
    #[arg(long, default_value = None)]
    token_override: Option<String>,
}

/// The main bot struct.
///
/// # Fields
///
/// - `debug` (`bool`) - Whether the bot is running in debug mode.
struct Bot {
    debug: bool,
}

#[async_trait]
impl EventHandler for Bot {
    async fn ready(&self, ctx: Context, ready: Ready) {
        match Command::set_global_commands(&ctx.http, commands::all_commands()).await {
            Ok(cmds) => info!("Registered {} commands", cmds.len()),
            Err(e) => {
                error!("Failed to register commands: {e}");
                return;
            }
        }

        if self.debug {
            ctx.set_activity(Some(ActivityData::playing("⚠ TESTING ⚠")));
            warn!(
                "The application has been started in testing mode; \
            ignore if this is intentional"
            );
        } else {
            ctx.set_activity(Some(ActivityData::playing("/help")));
        }

        info!(
            "Logged in as {} and commands have been synced",
            ready.user.name
        );
    }

    async fn interaction_create(&self, ctx: Context, interaction: Interaction) {
        if let Interaction::Command(cmd) = interaction {
            commands::handle(&ctx, &cmd).await;
        }
    }
}

/// Run the bot.
#[tokio::main]
async fn main() {
    let args = Args::parse();
    dotenv().ok();
    let env = from_env::<Environment>().expect("Invalid environment configuration");

    logging::config_tracing(
        args.debug,
        args.log_file,
        args.console_logging,
        args.colored_logs,
    )
    .expect("Failed to configure logging");

    let token = args.token_override.unwrap_or(env.token);

    let mut client = Client::builder(&token, GatewayIntents::all())
        .event_handler(Bot { debug: args.debug })
        .await
        .expect("Failed to create client");

    if let Err(e) = client.start().await {
        error!("Failed to start client: {e}");
    }
}
