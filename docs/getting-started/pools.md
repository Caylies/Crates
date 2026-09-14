# Pools

A **Pool** is a source players can claim crates from (e.g. "Daily" and "Weekly") by a cooldown and an optional set of conditions. Each pool becomes its own slash command.

## Commands

Pool commands are dynamitcally built when the extension loads. To reflect changes to a pool, run the `reloadcrates` text command.

## Conditions

Elegibility conditions stop the player from claiming crates from a pool.

+----------------------------+-----------+--------------------------------------------------------------------------------------+
| Rule                       | Type      | Details                                                                              |
+============================+===========+======================================================================================+
| Ball completion percentage | Number    | Measures against the player's ball completion percentage.                            |
+----------------------------+-----------+--------------------------------------------------------------------------------------+
| Ball count                 | Number    | Measures against the player's total ball count.                                      |
+----------------------------+-----------+--------------------------------------------------------------------------------------+
| Server                     | Server ID | Checks if a player is in the specified server.                                       |
+----------------------------+-----------+--------------------------------------------------------------------------------------+
| User                       | User ID   | Checks if a player is the specified user.                                            |
+----------------------------+-----------+--------------------------------------------------------------------------------------+
