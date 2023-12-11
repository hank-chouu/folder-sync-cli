import os
import re
import subprocess
import sys
from configparser import ConfigParser

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import click

from folder_sync.utils import (
    default_name,
    get_remotes,
    is_cmd_valid,
    is_local_folder_valid,
    is_remote_folder_valid,
    show_all_remotes,
    validation,
    print_pair,
)

pairs = ConfigParser()
pairs_path = os.path.abspath(os.path.dirname(__file__)) + "/pairs.ini"
if not os.path.exists(pairs_path):
    with open(pairs_path, "w") as f:
        pairs.write(f)
pairs.read(pairs_path)


@click.group()
def cli():
    pass


@click.command()
def new():
    """Create a new local/remote pair."""
    if not is_cmd_valid("rclone"):
        click.secho(
            "error: you need to first install rclone on this machine.", fg="red", bold=True
        )
        raise click.exceptions.Exit(code=1)
    click.echo("\n::: Making a new local/remote pair :::\n")

    # local folder
    local = click.prompt(click.style("Local folder path", fg="cyan"))
    while not is_local_folder_valid(local):
        click.secho("Invalid local path. Please try again.\n", fg="red", bold=True)
        local = click.prompt(click.style("Local folder path", fg="cyan"))

    # remote stroage
    all_remotes = get_remotes()
    show_all_remotes(all_remotes)
    remote_idx = click.prompt(click.style("\nEnter the remote # to pair", fg="cyan"))
    while remote_idx not in [str(idx) for idx in range(len(all_remotes))]:
        click.secho(f"Value {remote_idx} is invalid. Please try again.", fg="red", bold=True)
        show_all_remotes(all_remotes)
        remote_idx = click.prompt(click.style("\nEnter the remote # to pair", fg="cyan"))
    remote = all_remotes[int(remote_idx)].strip("\n")

    # remote folder
    remote_folder = click.prompt(
        click.style(
            "\nEnter the remote folder, or leave blank to sync the whole remote stroage",
            fg="cyan",
        ),
        default="",
    )
    path_regex = r"^[a-zA-Z0-9_/-]*(/[a-zA-Z0-9_/-]+)*$"
    while not re.match(path_regex, remote_folder):
        click.secho(f"Invalid value. Please try again.", fg="red", bold=True)
        remote_folder = click.prompt(
            click.style(
                "\nEnter the remote folder, or leave blank to sync the whole remote stroage",
                fg="cyan",
            ),
            type=str,
            default="",
        )
    while not is_remote_folder_valid(remote, remote_folder):
        click.secho(
            f"Invalid path for the remote stroage. Please try again.", fg="red", bold=True
        )
        remote_folder = click.prompt(
            click.style(
                "\nEnter the remote folder, or leave blank to sync the whole remote stroage",
                fg="cyan",
            ),
            default="",
        )
        path_regex = r"^[a-zA-Z0-9_/-]*(/[a-zA-Z0-9_/-]+)*$"
        while not re.match(path_regex, remote_folder):
            click.secho(f"Invalid value. Please try again.", fg="red", bold=True)
            remote_folder = click.prompt(
                click.style(
                    "\nEnter the remote folder, or leave blank to sync the whole remote stroage",
                    fg="cyan",
                ),
                default="",
            )
    click.secho(f"Passed!", fg="green", bold=True)
    if remote_folder and remote_folder[-1] != "/":
        remote_folder += "/"

    # pair name
    name = click.prompt(click.style("\nName this pair", fg="cyan"), default=default_name(local))
    while name in pairs.sections():
        click.secho(f"Duplicated pair name. Please try again.", fg="red", bold=True)
        name = click.prompt(
            click.style("\nName this pair", fg="cyan"), default=default_name(local)
        )

    # exclude hidden files
    exclude_hidden_files = click.prompt(
        click.style("\nExclude hidden files? [y/N]", fg="cyan"), default="y"
    ).lower()
    while exclude_hidden_files not in ["y", "n"]:
        click.secho(f"Invalid input.", fg="red", bold=True)
        exclude_hidden_files = click.prompt(
            click.style("\nExclude hidden files? [y/N]", fg="cyan"), default="y"
        ).lower()

    # exclude hidden folders
    exclude_hidden_folders = click.prompt(
        click.style("\nExclude hidden folders? [y/N]", fg="cyan"), default="y"
    ).lower()
    while exclude_hidden_folders not in ["y", "n"]:
        click.secho(f"Invalid input.", fg="red", bold=True)
        exclude_hidden_folders = click.prompt(
            click.style("\nExclude hidden files? [y/N]", fg="cyan"), default="y"
        ).lower()

    # write to pairs.ini
    pairs[name] = {}
    pairs[name]["local"] = local
    pairs[name]["remote"] = remote + remote_folder
    pairs[name]["exclude_hidden_files"] = exclude_hidden_files
    pairs[name]["exclude_hidden_folders"] = exclude_hidden_folders

    with open(pairs_path, "w") as f:
        pairs.write(f)

    click.secho(f"Configuration succeeded!", fg="green", bold=True)
    click.secho("\nNow you can run", fg="cyan", nl=False)
    click.echo(f" folder-sync pull {name}", nl=False)
    click.secho(" to sync local from remote, or run", fg="cyan", nl=False)
    click.echo(f" folder-sync push {name}", nl=False)
    click.secho(" to sync remote from local.", fg="cyan")


@click.command()
@click.argument("name", type=str)
@click.option("--use-copy", is_flag=True, help="Use rclone copy instead of sync.")
@click.option("--skip-val", is_flag=True, help="Skip folder validations.")
@click.option("-s", "small_files", is_flag=True, help="Optimze for tranfer small files.")
@click.option("-l", "large_files", is_flag=True, help="Optimze for tranfer large files.")
def pull(name, use_copy, skip_val, small_files, large_files):
    """Pull from remote folder."""

    if not is_cmd_valid("rclone"):
        click.secho(
            "error: you need to first install rclone on this machine.", fg="red", bold=True
        )
        raise click.exceptions.Exit(code=1)

    if name not in pairs.sections():
        click.secho(f"Invalid pair name. Please try again.", fg="red", bold=True)
        raise click.exceptions.Exit(code=1)

    if small_files is True and large_files is True:
        click.secho(f"Invalid usage. Pass either -s or -l", fg="red", bold=True)
        raise click.exceptions.Exit(code=1)

    program = "rclone"
    cmd = "sync"
    if use_copy:
        cmd = "copy"
    local_folder = pairs.get(name, "local")
    remote_full = pairs.get(name, "remote")
    full_cmd = [program, cmd, remote_full, local_folder, "-P"]

    if pairs.get(name, "exclude_hidden_files") == "y":
        full_cmd.extend(["--exclude", "'**/.**'"])
    if pairs.get(name, "exclude_hidden_folders") == "y":
        full_cmd.extend(["--exclude", "'/.**'"])

    if small_files is True:
        full_cmd.extend(["--checkers", "64", "--transfers", "32"])
    elif large_files is True:
        full_cmd.extend(["--transfers", "1"])

    if not skip_val:
        validation(local_folder, remote_full)
    try:
        click.echo("Pull started.")
        result = subprocess.run(full_cmd, stderr=subprocess.PIPE, text=True)
        if not result.stderr:
            click.echo("Pull completed.")
        else:
            click.echo(result.stderr.strip("\n"))
    except subprocess.CalledProcessError as e:
        click.secho(e, fg="red", bold=True)


@click.command()
@click.argument("name", type=str)
@click.option("--use-copy", is_flag=True, help="Use rclone copy instead of sync.")
@click.option("--skip-val", is_flag=True, help="Skip folder validations.")
@click.option("-s", "small_files", is_flag=True, help="Optimze for tranfer small files.")
@click.option("-l", "large_files", is_flag=True, help="Optimze for tranfer large files.")
def push(name, use_copy, skip_val, small_files, large_files):
    """Push local to remote."""
    if not is_cmd_valid("rclone"):
        click.secho(
            "error: you need to first install rclone on this machine.", fg="red", bold=True
        )
        raise click.exceptions.Exit(code=1)

    if name not in pairs.sections():
        click.secho(f"Invalid pair name. Please try again.", fg="red", bold=True)
        raise click.exceptions.Exit(code=1)

    if small_files is True and large_files is True:
        click.secho(f"Invalid usage. Pass either -s or -l", fg="red", bold=True)
        raise click.exceptions.Exit(code=1)

    program = "rclone"
    cmd = "sync"
    if use_copy:
        cmd = "copy"
    local_folder = pairs.get(name, "local")
    remote_full = pairs.get(name, "remote")

    full_cmd = [program, cmd, local_folder, remote_full, "-P"]

    if pairs.get(name, "exclude_hidden_files") == "y":
        full_cmd.extend(["--exclude", "'.*'"])
    if pairs.get(name, "exclude_hidden_folders") == "y":
        full_cmd.extend(["--exclude", "'.*/**'"])

    if small_files is True:
        full_cmd.extend(["--checkers", "64", "--transfers", "32"])
    elif large_files is True:
        full_cmd.extend(["--transfers", "1"])

    if not skip_val:
        validation(local_folder, remote_full)
    try:
        click.echo("Push Started.")
        result = subprocess.run(full_cmd, stderr=subprocess.PIPE, text=True)
        if not result.stderr:
            click.echo("Push completed.")
        else:
            click.echo(result.stderr.strip("\n"))
    except subprocess.CalledProcessError as e:
        click.secho(e, fg="red", bold=True)


@click.command()
@click.argument("name", nargs=-1, type=str)
@click.option("--all", "show_all", is_flag=True, default=False)
def info(name, show_all):
    """Show info for a pair or all pairs"""
    if not name and show_all is False:
        click.secho(
            "You must provide a pair name or use --all to show all pair infos.", fg="cyan"
        )
        raise click.exceptions.Exit(code=1)
    elif name and show_all is True:
        click.secho("You should either provide a pair name or use --all.", fg="cyan")
        raise click.exceptions.Exit(code=1)
    elif len(name) > 1:
        click.secho("You should provide one pair name at a time.", fg="cyan")
        raise click.exceptions.Exit(code=1)
    elif show_all is True:
        if len(pairs.sections()) == 0:
            click.echo("There is no pair to show.")
        for pair in pairs.sections():
            print_pair(pair, pairs)
    elif len(name) == 1:
        if name[0] not in pairs.sections():
            click.secho("error: pair not found.", fg="red", bold=True)
        else:
            print_pair(name[0], pairs)


@click.command()
@click.argument("name", nargs=-1, type=str)
@click.option("--all", "remove_all", is_flag=True, default=False)
def remove(name, remove_all):
    """Remove a pair or all pairs."""
    if not name and remove_all is False:
        click.secho("You must provide a pair name or use --all to remove all pairs.", fg="cyan")
        raise click.exceptions.Exit(code=1)
    elif name and remove_all is True:
        click.secho("You should either provide a pair name or use --all.", fg="cyan")
        raise click.exceptions.Exit(code=1)
    elif len(name) > 1:
        click.secho("You should provide one pair name at a time.", fg="cyan")
        raise click.exceptions.Exit(code=1)
    elif remove_all is True:
        if click.confirm(
            click.style("This will removed all configured pairs. Proceed?", fg="cyan")
        ):
            if len(pairs.sections()) == 0:
                click.echo("There is no pair to be removed.")
            else:
                for pair in pairs.sections():
                    pairs.remove_section(pair)
                    with open(pairs_path, "w") as f:
                        pairs.write(f)
                    click.secho("Sync pair ", fg="cyan", nl=False)
                    click.echo(f"{pair} ", nl=False)
                    click.secho("removed.", fg="cyan")
    elif len(name) == 1:
        if name[0] not in pairs.sections():
            click.secho("error: pair not found.", fg="red", bold=True)
        else:
            pairs.remove_section(name[0])
            with open(pairs_path, "w") as f:
                pairs.write(f)
            click.secho("Sync pair ", fg="cyan", nl=False)
            click.echo(f"{name[0]} ", nl=False)
            click.secho("removed.", fg="cyan")


cli.add_command(new)
cli.add_command(pull)
cli.add_command(push)
cli.add_command(info)
cli.add_command(remove)


if __name__ == "__main__":
    cli()
