# CatBot Plans

## New Features
* Moderation tools
  * Stash warnings and allow people to view a user's warnings
  * Add ability to remove warnings
* Management tools
  * /create-channel {name} etc
* Fun commands
  * Random something generator (int, float, etc)
  * coin flip
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
* Make colored-logging a cli arg
* Scan and refactor code
* Modularize repetitive processes
* Move certain commands with different types (like invert-rgb and invert-hex) into one command (like invert)
* (EVENTUALLY) make new logging system to be able to use debug without being flooded with discord.py debugs

## Bug Fixes
* ...