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
  * /cat-pic !
  * /avatar {user} !
  * /banner {user} !
* Server stats
  * /user-count !
  * /bot-count !
  * /member-count !
* Math commands
  * other cartesian equations, etc
  * TrigCog !
  * CalculusCog
  * CalculatorCog
  * StatisticsCog !
  * Add ability to pass strings as numbers ("pi", "e", "tau")
  * BinaryCog

## Improvements
* Scan and refactor code !
* Modularize repetitive processes !!
* Move certain commands with different types (like invert-rgb and invert-hex) into one command (like invert) !!
* (EVENTUALLY) make new logging system to be able to use debug without being flooded with discord.py debugs
* Ability to return number calculations in scientific notation
* Turn math answers into embeds !
* Add LaTeX support for math answers
* Delete unnecessary repetitions from docstrings !!
* Add emojis to messages/embeds to show which category a command was used in or just to add flair !!
* Add tests for all functions that don't directly involve discord.py functionality !!
* Rename commands in commands.py to fit their new command names !!!
* Change embeds that only have one field to just have it in the title and description instead !!

## Bug Fixes
* ...