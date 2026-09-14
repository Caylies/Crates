# Configuration

Crates can be configured from the Django admin panel. A settings instance will automatically be created when the package cog is loaded. If a settings instance doesn't exist yet, you can create one from the panel.

Package settings automatically resync every 60 seconds. Some settings require the package to be reloaded using the `[p]reload crates.package` command.

<!-- Decrease your zoom if you have difficulty reading the grid table. -->

+------------------------+-------------------------------------------------------------------------------------------------+
| Setting                | Details                                                                                         |
+========================+=================================================================================================+
| Crate name             | The singular name of crates.                                                                    |
+------------------------+-------------------------------------------------------------------------------------------------+
| Plural crate name      | The plural name of crates.                                                                      |
+------------------------+-------------------------------------------------------------------------------------------------+
| Crates slash name      | Overrides "/crates" slash command. Package must be reloaded to take effect.                     |
+------------------------+-------------------------------------------------------------------------------------------------+
| Menu color             | The accent color for view containers in hex format. Leave blank for none.                       |
+------------------------+-------------------------------------------------------------------------------------------------+
