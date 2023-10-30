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
    if not is_cmd_valid("rclone"):
        click.secho(
            "Error: you need to first install rclone on this machine.", fg="red", bold=True
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

    # write to pairs.ini
    pairs[name] = {}
    pairs[name]["local"] = local
    pairs[name]["remote"] = remote + remote_folder
    with open(pairs_path, "w") as f:
        pairs.write(f)

    click.secho(f"\nConfiguration succeeded!", fg="green", bold=True)
    click.echo("Now you can run", nl=False)
    click.secho(f" folder-sync pull {name}", fg="cyan", nl=False)
    click.echo(" to sync local from remote, or run", nl=False)
    click.secho(f" folder-sync push {name}", fg="cyan", nl=False)
    click.echo(" to sync remote from local.")


@click.command()
@click.argument("name", type=str)
@click.option("--use-copy", is_flag=True, help="Use rclone copy instead of sync.")
@click.option("--fast", is_flag=True, help="Skip folder validations.")
def pull(name, use_copy, fast):
    """Pull from remote folder."""

    if not is_cmd_valid("rclone"):
        click.secho(
            "Error: you need to first install rclone on this machine.", fg="red", bold=True
        )
        raise click.exceptions.Exit(code=1)

    if name not in pairs.sections():
        click.secho(f"Invalid pair name. Please try again.", fg="red", bold=True)
        raise click.exceptions.Exit(code=1)

    program = "rclone"
    cmd = "sync"
    if use_copy:
        cmd = "copy"
    local_folder = pairs.get(name, "local")
    remote_full = pairs.get(name, "remote")
    if not fast:
        validation(local_folder, remote_full)
    try:
        click.echo("Pull started.")
        result = subprocess.run(
            [program, cmd, remote_full, local_folder, "-P"], stderr=subprocess.PIPE, text=True
        )
        if not result.stderr:
            click.echo("Pull completed.")
        else:
            click.echo(result.stderr.strip("\n"))
    except subprocess.CalledProcessError as e:
        click.echo(e)


@click.command()
@click.argument("name", type=str)
@click.option("--use-copy", is_flag=True, help="Use rclone copy instead of sync.")
@click.option("--fast", is_flag=True, help="Skip folder validations.")
def push(name, use_copy, fast):
    """Push local to remote."""
    if not is_cmd_valid("rclone"):
        click.secho(
            "Error: you need to first install rclone on this machine.", fg="red", bold=True
        )
        raise click.exceptions.Exit(code=1)

    if name not in pairs.sections():
        click.secho(f"Invalid pair name. Please try again.", fg="red", bold=True)
        raise click.exceptions.Exit(code=1)

    program = "rclone"
    cmd = "sync"
    if use_copy:
        cmd = "copy"
    local_folder = pairs.get(name, "local")
    remote_full = pairs.get(name, "remote")
    if not fast:
        validation(local_folder, remote_full)
    try:
        click.echo("Push Started.")
        result = subprocess.run(
            [program, cmd, local_folder, remote_full, "-P"], stderr=subprocess.PIPE, text=True
        )
        if not result.stderr:
            click.echo("Push completed.")
        else:
            click.echo(result.stderr.strip("\n"))
    except subprocess.CalledProcessError as e:
        click.echo(e)


cli.add_command(new)
cli.add_command(pull)
cli.add_command(push)


if __name__ == "__main__":
    cli()
