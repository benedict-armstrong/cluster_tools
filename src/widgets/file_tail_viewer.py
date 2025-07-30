from typing import Optional
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static, TextArea
from textual.reactive import reactive
from ..ssh.cluster import SSHClient


class FileTailViewer(Vertical):
    """A widget that displays the tail of a file with auto-refresh capability."""

    file_path: reactive[Optional[str]] = reactive(None)
    content: reactive[str] = reactive("")

    def __init__(
        self,
        title: str,
        ssh_client: Optional[SSHClient] = None,
        file_path: Optional[str] = None,
        tail_lines: int = 50,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.title = title
        self.ssh_client = ssh_client
        self.tail_lines = tail_lines
        self.file_path = file_path

    def compose(self) -> ComposeResult:
        """Compose the file viewer layout."""
        yield Static(
            self._get_header_text(), classes="file-viewer-header", id="file-header"
        )
        yield TextArea("", read_only=True, show_line_numbers=False, id="file-content")

    def on_mount(self) -> None:
        """Initialize content after the widget is mounted."""
        # Update header with current file path
        self._update_header()

        # Set initial content based on current file_path
        if self.file_path:
            self.refresh_content()
        else:
            self.content = "No file specified"

    def watch_file_path(self, new_path: Optional[str]) -> None:
        """Called when file_path changes."""
        # Only update if the widget is mounted
        if not self.is_mounted:
            return

        # Update the header with the new file path
        self._update_header()

        if new_path:
            self.refresh_content()
        else:
            self.content = "No file specified"

    def watch_content(self, new_content: str) -> None:
        """Called when content changes."""
        # Only update if the widget is mounted and composed
        if self.is_mounted:
            try:
                text_area = self.query_one("#file-content", TextArea)
                text_area.text = new_content
                # Scroll to bottom to show latest content
                text_area.scroll_end()
            except Exception:
                # Widget not fully composed yet, ignore
                pass

    def refresh_content(self) -> None:
        """Refresh the file content by reading the tail of the file."""
        if not self.ssh_client:
            self.content = "No SSH client available"
            return

        if not self.file_path:
            self.content = "No file path specified"
            return

        try:
            # Use tail command to get last N lines
            command = f"tail -n {self.tail_lines} '{self.file_path}' 2>/dev/null || echo 'File not found or not readable'"
            result = self.ssh_client.execute_command(command)

            if result.exit_code == 0:
                content = result.stdout.strip()
                if content and content != "File not found or not readable":
                    self.content = content
                else:
                    self.content = f"File not found: {self.file_path}"
            else:
                self.content = f"Error reading file: {result.stderr}"

        except Exception as e:
            self.content = f"Error: {str(e)}"

    def set_file(self, file_path: Optional[str]) -> None:
        """Set a new file path to display."""
        self.file_path = file_path

    def _get_header_text(self) -> str:
        """Get the header text showing title and file path."""
        if self.file_path:
            return f"{self.title}: {self.file_path}"
        else:
            return f"{self.title}: No file"

    def _update_header(self) -> None:
        """Update the header text with current file path."""
        if self.is_mounted:
            try:
                header = self.query_one("#file-header", Static)
                header.update(self._get_header_text())
            except Exception:
                # Widget not fully composed yet, ignore
                pass
