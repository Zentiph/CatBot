# CatBot Changelog
A collective history of all the changes made to CatBot.

## v0.11.1
* Replaced logging with pawprints
* Added Formatters to LoggerOutputs in pawprints

## v0.10.1
* Renamed /self-stats to /bot-stats

## v0.10.0
* Added stats cog
  * Renamed /stats to /self-stats
* Refactored code to prevent repetition
* Added /member-count
* Fixed stats embed field misalignment
* Add emojis to bot responses
* Split /math log into two commands
  * /math log {x} {base} {ndigits}
  * /math ln {x} {ndigits}
  * /math log's base param is now defaulted to 10 rather than None for e
* Changed all /math command responses to send embeds
* Added ndigits param to some math commands
* Slight /stats formatting changes

## v0.9.0
* Added datetime module
  * /date-time date-time
  * /date-time date
  * /date-time time
  * /date-time weekday
  * /date-time days-until
* Refactored command names/groups to better organize commands
* Grouped icon and authored embed generation into one function
* Merged color modules into one module
* Fixed math module /nroot command complex arithmetic
* Added --coloredlogs CLI arg

## v0.8.3
* Added /flip-coin to fun module
* Added help support for fun module
* Small code refactors

## v0.8.2
* Fixed most math answers not being bolded
* Added rounding option to most math functions

## v0.8.1
* Fixed extra parenthesis in /ceil results
* Added warning message about arithmetic overflow for math commands

## v0.8.0
* Added random commands to start fun modules
  * /random integer
  * /random decimal
  * /random choice
  * /shuffle

## v0.7.1
* Added total servers to stats command

## v0.7.0
* Added /stats command
* Refactored some code

## v0.6.1
* Added bulk commands to math module
  * /sum
  * /prod
  * /gcd-bulk
  * /lcm-bulk

## v0.6.0
* Added math commands
  * Standard operations
  * Special functions (factorial, etc.)
  * More

## v0.5.1
* Fixed management commands not showing up in the help menu

## v0.5.0
* Added management commands
  * /echo
  * /announce
  * /dm

## v0.4.4
* Fixed uncaught error when muting/unmuting a user not in voice
* Small consistency fixes

## v0.4.3
* Added more moderation commands
  * /warn
  * /kick
  * /mute
  * /unmute
* Small bug fixes

## v0.4.2
* Added more moderation commands
  * /timeout add
  * /timeout reduce
  * /timeout remove
  * /unban
  * /clear (similar to purge)
* Small bug fixes

## v0.4.1
* Added embed author text and image to all embeds

## v0.4.0
* Started moderation commands
  * Only /ban as of now
* Added help commands to /help menu
* Added colored admin command logging to a specific channel
* Small bug fixes

## v0.3.2
* Renamed role-assign commands to color-role

## v0.3.1
* Added color-info role command

## v0.3.0
* Added help commands
  * Category ver to get commands in a group
  * Command ver to get help for a specific command

## v0.2.2
* Updated logging format

## v0.2.1
* Added colored stream logging
* Reformatted project directory
* Small bug fixes

## v0.2.0
* Added color tools commands
  * Color inversion
  * Color info
  * Access predefined colors list
  * Random color generator
* Added an optional seed parameter to both random functions

## v0.1.1
* Changed changelog formatting (meta)
* Fixed color inconsistency in banner

## v0.1.0
* Created CatBot
* Added color roles commands
  * Hex and RGB color role assignment
  * Predefined color assignment
  * Role color copying
  * Role color resetting