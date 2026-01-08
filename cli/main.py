import typer
from pathlib import Path
import subprocess


# python -m cli.main - генерирует пару нужных ключей

app = typer.Typer(
    name="auth-service-cli",
    help="CLI-утилиты для проекта Auth-service",
    no_args_is_help=True,
)


def find_project_root() -> Path:
    current = Path.cwd().resolve()
    while current != current.parent:
        if (current / "pyproject.toml").exists() or (current / "src").exists():
            return current
        current = current.parent
    raise RuntimeError("Не удалось найти корень проекта (нет pyproject.toml или src/)")


@app.command()
def keys_generate(
    bits: int = typer.Option(4096, "--bits", "-b", help="Длина ключа в битах"),
    keys_dir: str = typer.Option(
        "keys", "--dir", "-d", help="Папка для ключей относительно корня"
    ),
):
    """Генерирует пару RSA-ключей для JWT"""
    project_root = find_project_root()
    keys_dir_path = project_root / keys_dir
    keys_dir_path.mkdir(exist_ok=True)

    private_path = keys_dir_path / "private_key.pem"
    public_path = keys_dir_path / "public_key.pem"

    typer.echo(f"Генерируем RSA-{bits} пару...")

    # Генерация приватного
    subprocess.run(
        ["openssl", "genrsa", "-out", str(private_path), str(bits)], check=True
    )
    # Публичный
    subprocess.run(
        [
            "openssl",
            "rsa",
            "-in",
            str(private_path),
            "-pubout",
            "-out",
            str(public_path),
        ],
        check=True,
    )

    private_path.chmod(0o600)
    public_path.chmod(0o644)

    typer.echo("✅ Ключи успешно сгенерированы!")
    typer.echo(f"   Приватный: {private_path.relative_to(project_root)}")
    typer.echo(f"   Публичный:  {public_path.relative_to(project_root)}")


if __name__ == "__main__":
    app()
