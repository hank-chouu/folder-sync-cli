import os
import subprocess
from configparser import ConfigParser

import click


def get_remotes() -> list:
    return (
        subprocess.run(["rclone", "listremotes"], capture_output=True, text=True)
        .stdout.strip("\n")
        .split("\n")
    )


def show_all_remotes(all_remotes):
    click.secho(
        f"\nFound {len(all_remotes)} remote destinations from the rclone config:", fg="cyan"
    )
    for i in range(len(all_remotes)):
        click.echo("[ ", nl=False)
        click.secho(i, fg="green", nl=False)
        remote_strip = all_remotes[i]
        click.echo(f"]: {remote_strip}")


def is_cmd_valid(cmd):
    try:
        subprocess.run(
            ["which", cmd],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def is_local_folder_valid(local_folder):
    return os.path.exists(local_folder) and os.path.isdir(local_folder)


def is_remote_valid(remote):
    remotes = get_remotes()
    if remote in remotes:
        return True
    return False


def is_remote_folder_valid(remote, folder: str):
    # usnig whole remote stroage
    if not folder:
        return True
    click.secho(f"Validating remote folder...", fg="cyan")
    depth = len(folder.strip("/").split("/"))
    result = subprocess.run(
        ["rclone", "lsf", "--dirs-only", remote, f"--max-depth={depth}"],
        capture_output=True,
        text=True,
    )
    folders = result.stdout.strip("n").split("\n")
    if folder[-1] != "/":
        folder += "/"
    if folder not in folders:
        return False
    return True


def default_name(local_folder):
    return local_folder.strip("/").split("/")[-1].lower()


def validation(local_folder, remote_full):
    click.secho("Validating pair configuration...", fg="cyan")
    if not local_folder:
        click.secho("error: local is not configured.", fg="red", bold=True)
        raise click.exceptions.Exit(code=1)
    if not remote_full:
        click.secho("error: reomte is not configured.", fg="red", bold=True)
        raise click.exceptions.Exit(code=1)
    if not is_local_folder_valid(local_folder):
        click.secho(f"error: local folder {local_folder} is not valid.", fg="red", bold=True)
        raise click.exceptions.Exit(code=1)

    remote = remote_full.split(":")[0] + ":"
    remote_folder = remote_full.split(":")[1]

    if not is_remote_valid(remote):
        click.secho(f"error: remote stroage {remote} is not valid.", fg="red", bold=True)
        raise click.exceptions.Exit(code=1)

    if not is_remote_folder_valid(remote, remote_folder):
        click.secho(f"error: remote folder {remote_folder} is not valid.", fg="red", bold=True)
        raise click.exceptions.Exit(code=1)


def print_pair(pair_name, pairs: ConfigParser):
    click.secho("\n:: Pair name", fg="cyan", nl=False)
    click.echo(f": {pair_name}")
    click.secho(":: Local", fg="cyan", nl=False)
    click.echo(f": {pairs[pair_name]['local']}")
    click.secho(":: Remote", fg="cyan", nl=False)
    click.echo(f": {pairs[pair_name]['remote']}\n")