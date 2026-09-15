# Pools

A **Pool** is a source players can claim crates from (e.g. "Daily" or "Weekly")
on a cooldown, with an optional set of eligibility conditions. Each pool
becomes its own slash command.

## Commands

Pool commands are built dynamically when the extension loads. To sync
changes to a pool's config, run the `reloadcrates` text command.

## Conditions

Eligibility conditions stop a player from claiming crates from a pool.
All conditions on a pool must pass for a claim to succeed.

| Rule                       | Type      | Details                                                 |
|----------------------------|-----------|---------------------------------------------------------|
| Ball completion percentage | Number    | Checks against the player's ball completion percentage. |
| Ball count                 | Number    | Checks against the player's total ball count.           |
| Server                     | Server ID | Restricts claiming to a specific server.                |
| User                       | User ID   | Restricts claiming to a specific user.                  |

### Example

A "Daily" pool with a 24h cooldown and a `Ball completion percentage >= 50`
condition only lets players who've completed at least half their ball
collection claim from it once per day.
