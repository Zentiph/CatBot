//! All of the command modules for FizzBuzz.

use serenity::all::{CommandInteraction, Context, CreateCommand};
use tracing::error;

/// A command.
///
/// # Fields
///
/// - `name` (`&'static str`) - The name of the command.
/// - `register` (`fn() -> CreateCommand`) - The function that registers the command.
/// - `run` (`for<'a> fn(&'a Context`) - The function that runs the command.
pub struct Command {
    pub name: &'static str,
    pub register: fn() -> CreateCommand,
    pub run: for<'a> fn(
        &'a Context,
        &'a CommandInteraction,
    ) -> futures::future::BoxFuture<'a, anyhow::Result<()>>,
}

inventory::collect!(Command);

/// Get all commands.
///
/// # Returns
///
/// - `Vec<CreateCommand>` - A vector of all commands.
pub fn all_commands() -> Vec<CreateCommand> {
    inventory::iter::<Command>
        .into_iter()
        .map(|cmd| (cmd.register)())
        .collect()
}

/// Handle a command.
///
/// # Arguments
///
/// - `ctx` (`&Context`) - The event context.
/// - `command` (`&CommandInteraction`) - The command.
pub async fn handle(ctx: &Context, command: &CommandInteraction) {
    let handler = inventory::iter::<Command>
        .into_iter()
        .find(|cmd| cmd.name == command.data.name);

    match handler {
        Some(cmd) => {
            if let Err(e) = (cmd.run)(ctx, command).await {
                error!("Command '{}' failed: {e}", command.data.name);
            }
        }
        None => error!("Unknown command: {}", command.data.name),
    }
}

/// Register a command.
///
/// # Arguments
///
/// - `name` (`&'static str`) - The name of the command.
/// - `register` (`fn() -> CreateCommand`) - The function that registers the command.
/// - `run` (`for<'a> fn(&'a Context, &'a CommandInteraction) -> futures::future::BoxFuture<'a, anyhow::Result<()>>`) - The function that runs the command.
#[macro_export]
macro_rules! register_command {
    ($name:literal, $register:expr, $run:expr) => {
        inventory::submit! {
            $crate::commands::Command {
                name: $name,
                register: $register,
                run: |ctx, cmd| Box::pin($run(ctx, cmd)),
            }
        }
    };
}
