import click
import uvicorn


@click.command()
@click.option('--port', default=32100, help='Port to run the server on')
def dev(port):
    """Development server command."""
    uvicorn.run("server.main:app", host="0.0.0.0", port=port, reload=True)


if __name__ == "__main__":
    dev()
