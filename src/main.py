import typer
import logging
from textual.app import App
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Placeholder

from .config import Config
from .widgets.sidebar import JobsSidebar
from .ssh.cluster import SSHClient
from .htcondor.htcondor import HTCondorClient


cli = typer.Typer()


@cli.command()
def cluster(
    hostname: str = typer.Option(
        "login.cluster.is.localnet", help="The hostname of the cluster"
    ),
    port: int = typer.Option(22, help="The port to connect to the cluster"),
    username: str = typer.Option(
        "barmstrong", help="The username to connect to the cluster"
    ),
    private_key_path: str | None = typer.Option(
        None, help="The path to the private key to connect to the cluster"
    ),
):
    """Run the application."""
    config = Config(hostname, port, username, private_key_path)
    app = ClusterApp(config)
    app.run()


class ClusterApp(App):
    """Original cluster monitoring app (kept for backwards compatibility)."""

    CSS_PATH = "styles/cluster_tool.tcss"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def __init__(self, config: Config | None = None):
        super().__init__()
        self.config = config or Config(
            hostname="login.cluster.is.localnet",
            port=22,
            username="barmstrong",
            private_key_path=None,
        )
        self.ssh_client = None
        self.htcondor_client = None
        self.title = "Condor Client"
        self.logger = logging.getLogger(__name__)

    def compose(self):
        """Simple layout for cluster monitoring."""
        yield Header()
        with Horizontal():
            yield JobsSidebar(id="sidebar")
            with Vertical(id="main-content"):
                yield Placeholder("Main content")
        yield Footer()

    def on_mount(self) -> None:
        """Initialize SSH and HTCondor clients when the app starts."""
        self._initialize_clients()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def _initialize_clients(self) -> None:
        """Initialize SSH and HTCondor clients."""
        try:
            # Initialize SSH client
            self.ssh_client = SSHClient(self.config)

            # Connect to the cluster
            self.ssh_client.connect()
            print(f"Connected to cluster at {self.config.hostname}")

            # Initialize HTCondor client
            self.htcondor_client = HTCondorClient(self.ssh_client)

            # Set up the sidebar with the HTCondor client
            sidebar = self.query_one("#sidebar", JobsSidebar)
            sidebar.set_htcondor_client(self.htcondor_client, self.config.username)

        except Exception as e:
            self.logger.error(f"Failed to initialize clients: {e}")
            # Could show an error message to the user here

    def on_jobs_sidebar_job_selected(self, event: JobsSidebar.JobSelected) -> None:
        """Handle job selection from the sidebar."""
        self.logger.info(
            f"Selected job: {event.job.job_id} ({event.job.job_status_name})"
        )
        # Here you could update the main content area with job details

    def on_unmount(self) -> None:
        """Clean up connections when the app shuts down."""
        if self.ssh_client:
            try:
                self.ssh_client.disconnect()
                self.logger.info("Disconnected from cluster")
            except Exception as e:
                self.logger.error(f"Error disconnecting from cluster: {e}")


if __name__ == "__main__":
    cli()
