//! Miscellaneous commands.

use crate::discord::commands::command;
use crate::logging::log_app_command;
use chrono::{DateTime, Datelike, Utc};
use serenity::all::{
    CommandInteraction, Context, CreateInteractionResponse, CreateInteractionResponseMessage,
};
use sysinfo::{System, get_current_pid};

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

fn human_readable_date(date: DateTime<Utc>) -> String {
    let day = date.day();
    format!("{}{} {}", day, ordinal_suffix(day), date.format("%B %Y"))
}

#[command(
    name = "stats",
    description = "Get stats about FizzBuzz.",
    category = Misc,
)]
async fn stats(ctx: &Context, interaction: &CommandInteraction) -> anyhow::Result<()> {
    log_app_command(interaction);

    interaction.defer(&ctx.http).await?;

    let guilds = ctx.cache.guild_count().to_string();
    let memory_mb = System::new_all()
        .process(get_current_pid().unwrap())
        .unwrap()
        .memory() as f64
        / (1024.0 * 1024.0);

    interaction
        .create_response(
            &ctx.http,
            CreateInteractionResponse::Message(
                CreateInteractionResponseMessage::new().content("Test"),
            ),
        )
        .await?;
    Ok(())
}
