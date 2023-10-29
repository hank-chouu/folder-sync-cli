import subprocess
import re
import os

import click

def show_all_remotes(all_remotes):

    click.secho(f"\nFound {len(all_remotes)} remote destinations from the rclone config:", fg="cyan")
    for i in range(len(all_remotes)):
        click.echo("[ ", nl=False)
        click.secho(i, fg="green", nl=False)
        remote_strip = all_remotes[i].strip("\n")
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
    
def is_local_valid(local_dir):
    return os.path.exists(local_dir) and os.path.isdir(local_dir)


def is_remote_destination_valid(remote, folder:str):

    # usnig whole remote stroage
    if not folder:
        return True
    click.secho(f"\nValidating remote folder...", fg="cyan")
    depth = len(folder.strip("/").split("/"))
    result = subprocess.run(
        ["rclone", "lsf", "--dirs-only", remote, f"--max-depth={depth}"], capture_output=True, text=True
    )
    folders = result.stdout.strip("n").split("\n")    
    if folder[-1] != "/":
        folder += "/"
    if folder not in folders:
        return False
    return True


def default_name(local_folder):
    return local_folder.strip("/").split("/")[-1].lower()




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