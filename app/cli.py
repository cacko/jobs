import typer
from rich import print
from app.main import serve
from app.database import create_tables

cli = typer.Typer()


@cli.command()
def serve_api():
    serve()

@cli.command()
def init_db():
    create_tables()


@cli.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if not ctx.invoked_subcommand:
        ctx.invoke(serve_api)


if __name__ == '__main__':
    cli()
