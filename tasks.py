from pathlib import Path

from invoke import task, Collection

docker_path = Path("devops/docker")


@task
def docker_run(ctx, env=""):
    """run docker dompose with build arg"""
    base_compose = docker_path / "docker-compose.yml"
    # env_compose = docker_path / f"docker-compose.{env}.yml"
    ctx.run(f"docker-compose -f {base_compose} up --build")
