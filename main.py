import click
import re
import os
import subprocess
from configparser import ConfigParser

config_object = ConfigParser()
config_object.read("config.ini")


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
    pattern = r"^([a-zA-Z0-9_-]+):?([/a-zA-Z0-9_-]+/)+$"
    # not a valid dir
    match_ = re.search(pattern, remote_dir)
    if not match_:
        return False
    # not a valid drive
    stdout = subprocess.run(
        ["rclone", "listremotes"], capture_output=True, text=True
    ).stdout
    listremotes = stdout.split("\n")
    remote = match_[1] + ":"
    if remote not in listremotes:
        return False
    # not a valid path
    stdout = subprocess.run(
        ["rclone", "lsf", "--dirs-only", remote], capture_output=True, text=True
    ).stdout
    folders = stdout.split("\n")
    if match_[2] not in folders:
        return False

    return True


def is_local_valid(local_dir):
    return os.path.exists(local_dir) and os.path.isdir(local_dir)


@click.group()
def cli():
    pass


@click.command()
@click.option("--local", type=str)
@click.option("--remote", type=str)
def config(local, remote):
    if not is_rclone_exists():
        click.echo("Error: no rclone installed on this machine.")
        raise click.exceptions.Exit(code=1)

    if local is not None:
        if not is_local_valid(local):
            click.echo("Error: local dir is not valid.")
            raise click.exceptions.Exit(code=1)
        config_object["DIR_PATH"]["local"] = local
        with open("config.ini", "w") as conf:
            config_object.write(conf)
        click.echo(f"Local path is configured as {local}.")

    if remote is not None:
        if not is_remote_valid(remote):
            click.echo("Error: remote dir is not valid.")
            raise click.exceptions.Exit(code=1)
        config_object["DIR_PATH"]["remote"] = remote
        with open("config.ini", "w") as conf:
            config_object.write(conf)
        click.echo(f"Remote path is configured as {remote}.")


@click.command()
@click.option("--no-delete", default=False)
def pull(no_delete):
    if not is_rclone_exists():
        click.echo("Error: no rclone installed on this machine.")
        raise click.exceptions.Exit(code=1)

    program = "rclone"
    cmd = "sync"
    if no_delete:
        cmd = "copy"
    dirs = config_object["DIR_PATH"]
    local = dirs.get("local")
    remote = dirs.get("remote")

    ## check not none and dir exist
    if local is None:
        click.echo("Error: local path is not configured.")
        raise click.exceptions.Exit(code=1)
    if remote is None:
        click.echo("Error: reomte path is not configured.")
        raise click.exceptions.Exit(code=1)
    if not is_local_valid(local):
        click.echo("Error: local path is not valid.")
        raise click.exceptions.Exit(code=1)
    if not is_remote_valid(remote):
        click.echo("Error: reomte path is not valid.")
        raise click.exceptions.Exit(code=1)

    subprocess.run([program, cmd, remote, local])
    click.echo("Pull completed.")


@click.command()
@click.option("--no-delete", default=False)
def push(no_delete):
    if not is_rclone_exists():
        click.echo("Error: no rclone installed on this machine.")
        raise click.exceptions.Exit(code=1)

    program = "rclone"
    cmd = "sync"
    if no_delete:
        cmd = "copy"
    dirs = config_object["DIR_PATH"]
    local = dirs.get("local")
    remote = dirs.get("remote")

    ## check not none and dir exist
    if local is None:
        click.echo("Error: local path is not configured.")
        raise click.exceptions.Exit(code=1)
    if remote is None:
        click.echo("Error: reomte path is not configured.")
        raise click.exceptions.Exit(code=1)
    if not is_local_valid(local):
        click.echo("Error: local path is not valid.")
        raise click.exceptions.Exit(code=1)
    if not is_remote_valid(remote):
        click.echo("Error: reomte path is not valid.")
        raise click.exceptions.Exit(code=1)

    subprocess.run([program, cmd, local, remote])
    click.echo("Push completed.")



cli.add_command(config)
cli.add_command(pull)
cli.add_command(push)


if __name__ == "__main__":
    cli()
