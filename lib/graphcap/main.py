import click
from dotenv import load_dotenv

load_dotenv()


@click.group()
def cli():
    """graphcap CLI tool"""
    pass


if __name__ == "__main__":
    cli()
