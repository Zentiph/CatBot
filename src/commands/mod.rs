//! All of the command modules for FizzBuzz.

pub mod misc;

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
/// - `params` (`&'static [(&'static str, &'static str)]`) - Parameter names and descriptions.
/// - `examples` (`Option<&'static [&'static str]>`) - Examples of how to use the command.
/// - `notes` (`Option<&'static [&'static str]>`) - Any special notes about the command.
pub struct CommandInfo {
    pub name: &'static str,
    pub description: &'static str,
    pub category: CommandCategory,
    pub params: &'static [(&'static str, &'static str)],
    pub examples: Option<&'static [&'static str]>,
    pub notes: Option<&'static [&'static str]>,
}

/// A command.
///
/// # Fields
///
/// - `info` (`CommandInfo`) - Information about the command.
/// - `run` (`for<'a> fn(&'a Context`) - The function that runs the command.
pub struct Command {
    pub info: CommandInfo,
    pub run: for<'a> fn(
        &'a Context,
        &'a CommandInteraction,
    ) -> futures::future::BoxFuture<'a, anyhow::Result<()>>,
}
impl Command {
    /// Get the help text for the command.
    ///
    /// # Arguments
    ///
    /// - `&self` (`&Command`) - The command.
    ///
    /// # Returns
    ///
    /// - `String` - The help text.
    pub fn help(&self) -> String {
        let mut help = String::new();

        help.push_str(self.info.description);

        help.push_str("\n**Parameters:**");
        for (param, desc) in self.info.params {
            help.push_str(&format!("\n`{}`: {}", param, desc));
        }

        if let Some(examples) = self.info.examples {
            help.push_str("\n**Examples:**");
            for example in examples {
                help.push_str(&format!("\n`{}`", example));
            }
        }
        if let Some(notes) = self.info.notes {
            help.push_str("\n**Notes:**");
            for note in notes {
                help.push_str(&format!("\n`{}`", note));
            }
        }

        help
    }
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
        .map(|cmd| CreateCommand::new(cmd.info.name).description(cmd.info.description))
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
                    params: &[$(($pk, $pv),)*],
                    examples: {
                        let _val: Option<&'static [&'static str]> = None;
                        $(let _val = Some(&[$($ex,)*] as &[&str]);)?
                        _val
                    },
                    notes: {
                        let _val: Option<&'static [&'static str]> = None;
                        $(let _val = Some(&[$($note,)*] as &[&str]);)?
                        _val
                    },
                },
                run: |ctx, cmd| Box::pin($run(ctx, cmd)),
            }
        }
    };
}
