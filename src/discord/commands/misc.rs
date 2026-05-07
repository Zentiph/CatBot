//! Miscellaneous commands.

use crate::{discord::commands::CommandCategory, logging::log_app_command};
use chrono::{DateTime, Datelike, Utc};
use serenity::all::{
    CommandInteraction, Context, CreateInteractionResponse,
    CreateInteractionResponseMessage,
};
use sysinfo::{System, get_current_pid};

use crate::register_command;

/// Get the ordinal suffix for a number.
///
/// # Arguments
///
/// - `n` (`u32`) - The number.
///
/// # Returns
///
/// - `String` - The ordinal suffix (e.g. "st", "nd", "rd", "th").
fn ordinal_suffix(n: u32) -> String {
    if (11..13).contains(&(&n % 100)) {
        "th".to_string()
    } else {
        match n % 10 {
            1 => "st".to_string(),
            2 => "nd".to_string(),
            3 => "rd".to_string(),
            _ => "th".to_string(),
        }
    }
}

/// Convert a date to a human-readable format.
///
/// # Arguments
///
/// - `date` (`DateTime<Utc>`) - The date.
///
/// # Returns
///
/// - `String` - The human-readable date.
fn human_readable_date(date: DateTime<Utc>) -> String {
    let day = date.day();
    format!("{}{} {}", day, ordinal_suffix(day), date.format("%B %Y"))
}

register_command!(
    name: "stats",
    description: "Get stats about FizzBuzz.",
    category: CommandCategory::Misc,
    params: {},
    run: async |ctx: &Context, interaction: &CommandInteraction| {
        log_app_command(interaction);

        interaction.defer(&ctx.http).await?;

        let guilds = ctx.cache.guild_count().to_string();
        let memory_mb = System::new_all().process(get_current_pid().unwrap()).unwrap().memory() as f64 / (1024.0 * 1024.0);

        interaction.create_response(
            &ctx.http,
            CreateInteractionResponse::Message(
                CreateInteractionResponseMessage::new().content("Test"))).await?;
        Ok(())
    },
);
