//! All of the command modules for FizzBuzz.

use std::collections::HashMap;

use serenity::all::{CommandInteraction, Context, CreateCommand};
use tracing::error;

/// A command category.
///
/// # Variants
///
/// - `Color` - Color and color role commands.
/// - `Fun` - Fun commands.
/// - `Help` - Help commands.
/// - `Moderation` - Moderation commands.
/// - `Misc` - Miscellaneous commands.
pub enum CommandCategory {
    Color,
    Fun,
    Help,
    Moderation,
    Misc,
}

/// Information about a command..
///
/// # Fields
///
/// - `name` (`&'static str`) - The name of the command.
/// - `description` (`&'static str`) - The description of the command.
/// - `category` (`CommandCategory`) - The category of the command.
/// - `params` (`HashMap<String`) - A map of parameter names to their descriptions.
/// - `examples` (`Option<Vec<String>>`) - A list of examples of how to use the command.
/// - `notes` (`Option<Vec<String>>`) - Any special notes about the command.
pub struct CommandInfo {
    pub name: &'static str,
    pub description: &'static str,
    pub category: CommandCategory,
    pub params: HashMap<String, String>,
    pub examples: Option<Vec<String>>,
    pub notes: Option<Vec<String>>,
}

/// A command.
///
/// # Fields
///
/// - `info` (`CommandInfo`) - Information about the command.
/// - `register` (`fn() -> CreateCommand`) - The function that registers the command.
/// - `run` (`for<'a> fn(&'a Context`) - The function that runs the command.
pub struct Command {
    pub info: CommandInfo,
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
        .find(|cmd| cmd.info.name == command.data.name);

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
/// # Required Arguments
///
/// - `name` (`&'static str`) - The name of the command.
/// - `description` (`&'static str`) - The description of the command.
/// - `category` (`CommandCategory`) - The category of the command.
/// - `params` (`{ "name" => "description", ... }`) - Map of parameter names to descriptions.
/// - `register` (`fn() -> CreateCommand`) - The function that registers the command.
/// - `run` (`async fn`) - The function that runs the command.
///
/// # Optional Arguments
///
/// - `examples` (`["example1", ...]`) - Examples of how to use the command.
/// - `notes` (`["note1", ...]`) - Special notes about the command.
///
/// # Example
///
/// ```rust
/// register_command!(
///     name: "foo",
///     description: "Does foo",
///     category: CommandCategory::Misc,
///     params: { "arg" => "Some argument" },
///     register: register,
///     run: run,
///     examples: ["/foo bar"],
///     notes: ["Only usable in servers"],
/// );
/// ```
#[macro_export]
macro_rules! register_command {
    (
        name: $name:expr,
        description: $desc:expr,
        category: $cat:expr,
        params: { $($pk:expr => $pv:expr),* $(,)? },
        register: $register:expr,
        run: $run:expr
        $(, examples: [$($ex:expr),* $(,)?])?
        $(, notes: [$($note:expr),* $(,)?])?
        $(,)?
    ) => {
        inventory::submit! {
            $crate::commands::Command {
                info: $crate::commands::CommandInfo {
                    name: $name,
                    description: $desc,
                    category: $cat,
                    params: {
                        let mut map = std::collections::HashMap::new();
                        $(map.insert($pk.to_string(), $pv.to_string());)*
                        map
                    },
                    examples: {
                        let mut _val: Option<Vec<String>> = None;
                        $(_val = Some(vec![$($ex.to_string()),*]);)?
                        _val
                    },
                    notes: {
                        let mut _val: Option<Vec<String>> = None;
                        $(_val = Some(vec![$($note.to_string()),*]);)?
                        _val
                    },
                },
                register: $register,
                run: |ctx, cmd| Box::pin($run(ctx, cmd)),
            }
        }
    };
}
