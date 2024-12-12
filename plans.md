# CatBot Plans

## New Features
* Moderation tools
  * Stash warnings and allow people to view a user's warnings
  * Add ability to remove warnings
* Management tools
  * /create-channel {name} etc
* Fun commands
  * mini games (tic tac toe, etc)
  * /time {timezone}
  * /cat-pic
  * /avatar {user}
  * /banner {user}
* Bot stats
  * /uptime
  * /command-count
* Server stats
  * /user-count
  * /bot-count
  * /member-count
* Math commands
  * other cartesian equations, etc
  * TrigCog
  * CalculusCog
  * CalculatorCog
  * StatisticsCog
  * Add ability to pass strings as numbers ("pi", "e", "tau")
  * BinaryCog

## Improvements
* Scan and refactor code
* Modularize repetitive processes
* Move certain commands with different types (like invert-rgb and invert-hex) into one command (like invert)
* (EVENTUALLY) make new logging system to be able to use debug without being flooded with discord.py debugs
* Add parents to command groups for better organization
* Ability to return number calculations in scientific notation
* Turn math answers into embeds
* Add LaTeX support for math answers
* Delete unnecessary repetitions from docstrings
* Move time stuff to its own module
* Options for military time, time formatting, etc
* Add emojis to messages/embeds to show which category a command was used in or just to add flair
* Add tests for all functions that don't directly involve discord.py functionality
* Put module commands into categories to better organize commands
* Rename commands in commands.py to fit their new command names

## Bug Fixes
* ...