# folder-sync-cli

Use simple push/pull commands to perform rclone syncing commands.

## Install

It is recommended in [PEP 618](https://peps.python.org/pep-0668/) to use `pipx` for installing python CLI tool.

```
pipx install folder-sync-cli
```

## Usage

```
Usage: folder-sync [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  info    Show info for a pair or all pairs
  new     Create a new local/remote pair.
  pull    Pull from remote folder.
  push    Push local to remote.
  remove  Remove a pair or all pairs.
```