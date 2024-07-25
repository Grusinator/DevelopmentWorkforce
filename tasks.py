

import os
import webbrowser
from pathlib import Path

import invoke

docker_path = Path("devops/docker")


@invoke.task
def docker_run(ctx, env=""):
    base_compose = docker_path / "docker-compose.yml"
    # env_compose = docker_path / f"docker-compose.{env}.yml"
    ctx.run(f"docker-compose -f {base_compose} up --build")