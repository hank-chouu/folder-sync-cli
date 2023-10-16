import os
import re
import subprocess
from configparser import ConfigParser

import click

config_object = ConfigParser()
configfile_path = os.path.abspath(os.path.dirname(__file__)) + "/config.ini"
if not os.path.exists(configfile_path):
    config_object.add_section("DIR_PATH")
    config_object.set("DIR_PATH", "local", "")
    config_object.set("DIR_PATH", "remote", "")
    with open(configfile_path, "w") as configfile:
        config_object.write(configfile)
config_object.read(configfile_path)


def is_rclone_exists():
    try:
        subprocess.run(
            ["which", "rclone"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def is_remote_valid(remote_dir):
    # not a valid dir
    pattern = r"^([a-zA-Z0-9_-]+):?([/a-zA-Z0-9_-]+/)+$"
    match_ = re.search(pattern, remote_dir)
    if not match_:
        return False

    # not a valid drive
    result = subprocess.run(["rclone", "listremotes"], capture_output=True, text=True)
    listremotes = result.stdout.split("\n")
    remote = match_[1] + ":"
    if remote not in listremotes:
        return False

    # not a valid path
    result = subprocess.run(
        ["rclone", "lsf", "--dirs-only", remote], capture_output=True, text=True
    )
    folders = result.stdout.split("\n")
    if match_[2] not in folders:
        return False
    return True


def is_local_valid(local_dir):
    return os.path.exists(local_dir) and os.path.isdir(local_dir)


def validation(local, remote):
    if not local:
        click.echo("Error: local path is not configured.")
        raise click.exceptions.Exit(code=1)
    if not remote:
        click.echo("Error: reomte path is not configured.")
        raise click.exceptions.Exit(code=1)
    if not is_local_valid(local):
        click.echo("Error: local path is not valid.")
        raise click.exceptions.Exit(code=1)
    if not is_remote_valid(remote):
        click.echo("Error: reomte path is not valid.")
        raise click.exceptions.Exit(code=1)


@click.group()
def cli():
    pass


@click.command()
@click.option("--set-local", type=str, help="Configure local folder.")
@click.option("--set-remote", type=str, help="Configure reomte folder.")
def config(set_local, set_remote):
    """Show or configure local and reomte paths."""
    if not is_rclone_exists():
        click.echo("Error: no rclone installed on this machine.")
        raise click.exceptions.Exit(code=1)

    if set_local is None and set_remote is None:
        config_local = config_object.get("DIR_PATH", "local")
        if config_local:
            click.echo(f"local = {config_local}")
        config_remote = config_object.get("DIR_PATH", "remote")
        if config_remote:
            click.echo(f"remote = {config_remote}")

    if set_local is not None:
        if not is_local_valid(set_local):
            click.echo("Error: local path is not valid.")
            raise click.exceptions.Exit(code=1)
        config_object.set("DIR_PATH", "local", set_local)
        with open(configfile_path, "w") as configfile:
            config_object.write(configfile)
        click.echo(f"Local path is configured as {set_local}.")

    if set_remote is not None:
        if not is_remote_valid(set_remote):
            click.echo("Error: remote path is not valid.")
            raise click.exceptions.Exit(code=1)
        config_object.set("DIR_PATH", "remote", set_remote)
        with open(configfile_path, "w") as configfile:
            config_object.write(configfile)
        click.echo(f"Remote path is configured as {set_remote}.")


@click.command()
@click.option("--use-copy", is_flag=True, help="Use rclone copy instead of sync.")
@click.option("--fast", is_flag=True, help="Skip path validations.")
def pull(use_copy, fast):
    """Pull from remote folder."""
    if not is_rclone_exists():
        click.echo("Error: no rclone installed on this machine.")
        raise click.exceptions.Exit(code=1)

    program = "rclone"
    cmd = "sync"
    if use_copy:
        cmd = "copy"
    local = config_object.get("DIR_PATH", "local")
    remote = config_object.get("DIR_PATH", "remote")
    if not fast:
        click.echo("Validating config files...")
        validation(local, remote)
    try:
        click.echo("Pull started.")
        result = subprocess.run(
            [program, cmd, remote, local, "-P"], stderr=subprocess.PIPE, text=True
        )
        if not result.stderr:
            click.echo("Pull completed.")
        else:
            click.echo(result.stderr.strip("\n"))
    except subprocess.CalledProcessError as e:
        click.echo(e)


@click.command()
@click.option("--use-copy", is_flag=True, help="Use rclone copy instead of sync.")
@click.option("--fast", is_flag=True, help="Skip path validations.")
def push(use_copy, fast):
    """Push local to remote."""
    if not is_rclone_exists():
        click.echo("Error: no rclone installed on this machine.")
        raise click.exceptions.Exit(code=1)

    program = "rclone"
    cmd = "sync"
    if use_copy:
        cmd = "copy"
    dirs = config_object["DIR_PATH"]
    local = dirs.get("local")
    remote = dirs.get("remote")
    if not fast:
        click.echo("Validating config files...")
        validation(local, remote)
    try:
        result = subprocess.run(
            [program, cmd, local, remote, "-P"], stderr=subprocess.PIPE, text=True
        )
        if not result.stderr:
            click.echo("Push completed.")
        else:
            click.echo(result.stderr.strip("\n"))
    except subprocess.CalledProcessError as e:
        click.echo(e)


cli.add_command(config)
cli.add_command(pull)
cli.add_command(push)


if __name__ == "__main__":
    cli()
