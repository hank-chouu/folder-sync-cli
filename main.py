import click
import re
import subprocess
from configparser import ConfigParser

config_object = ConfigParser()
config_object.read("config.ini")

@click.group
def cli():
    pass

def if_remote_valid(remote_dir):

    pattern = r'^([a-zA-Z0-9_-]+):([/a-zA-Z0-9_-]+/)+$'
    
    if not re.match(pattern, remote_dir):
        return False
    listremotes = subprocess.run(["rclone", "listremotes"], capture_output=True)
    remote = re.search(pattern, remote_dir)[1]
    if remote not in listremotes:
        return False
    
    return True




@cli.command
@click.option("--local", type=str)
@click.option("--remote", type=str)
def config(local, remote):

    pass



@cli.command
@click.option("--no-delete", default=False)
def pull(no_delete):

    program = "rclone"
    cmd = "sync --progress"
    if no_delete:
        cmd = "copy --progress"
    dirs = config_object["DIR_PATH"]
    local = dirs.get("local")
    remote = dirs.get("remote")

    ## check not none and dir exist

    subprocess.run([program, cmd, remote, local])

@cli.command
@click.option("--no-delete", default=False)
def push(no_delete):

    program = "rclone"
    cmd = "sync --progress"
    if no_delete:
        cmd = "copy --progress"
    dirs = config_object["DIR_PATH"]
    local = dirs.get("local")
    remote = dirs.get("remote")

    ## check not none and dir exist

    subprocess.run([program, cmd, local, remote])


if __name__ == "__main__":
    cli()
    