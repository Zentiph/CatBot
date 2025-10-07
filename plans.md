# CatBot Plans
Plans with any exclamation points are planned to be worked on this major update cycle.
The more exclamation points, the more urgent/desired a change is.

## New Features
* Moderation tools
  * Stash warnings and allow people to view a user's warnings
  * Add ability to remove warnings
* Management tools
  * /create-channel {name} etc
* Fun commands
  * mini games (tic tac toe, etc)
* Server stats
  * Server ID
  * creation date
  * owner
  * etc
* Math commands
  * other cartesian equations, etc
  * TrigCog
  * CalculusCog
  * CalculatorCog
  * Add ability to pass strings as numbers ("pi", "e", "tau")
  * BinaryCog
* Take inspiration from other bot's commands
* /quote that makes a quote of someone with their pfp like make it a quote bot
* /permissions command
  * shows what permissions the bot has in the current channel or a specified channel
* /encode {message} {method}
  * method ideas:
  * base64
  * hex
  * caesar cipher
  * etc
* builtin python functions
  * hash
  * etc
* image editing/creation stuff
  * /meme {image} {caption} {font}
  * etc
* discord timestamp generator command

## Improvements
* Implement pawprints logging !
* Ability to return number calculations in scientific notation
* Add LaTeX support for math answers
* Add tests for all functions that don't directly involve discord.py functionality !!
* Try to remove as many type ignore comments as possible !
* move all non-directly involved funcs in cog modules to their own utils modules !!
  * give them all .pyi files
* put specific responses that involve emojis into functions to promote reusability and easy changes later on
  * e.g. create_success_message(msg: str) -> str
* clear as many mypy and pylint ignore/disables as possible
* Find a better way to do /help !!
  * Have a dict mapping funcs to simple names that can be used in help
* Update tests (mainly for pawprints) !!
* Add version of /help with no args that gives a general overview of how CatBot works, what features it has, and how to use the other /help commands
* Add .env auto generator when bot is run and .env can't be found. It will add all needed fields and default to empty, then quit stating that the .env needs to be filled out.
* change commands with lines (-) for spaces to be one word
  * (discord autofill stops for commands like cat-pic if you type catpic)
* MOVE TO DISCORD.JS EVENTUALLY

## Bug Fixes
* ...
