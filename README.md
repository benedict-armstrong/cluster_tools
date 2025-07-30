# Cluster Tools

A Python application for monitoring and managing HTCondor jobs on remote clusters via SSH.

## Features

- **SSH Connection**: Secure connection to remote clusters using paramiko
- **HTCondor Integration**: Retrieve and monitor HTCondor jobs using `condor_q`
- **Job Status Monitoring**: Real-time job status and summaries
- **Terminal UI**: Built with Textual for rich terminal interfaces (coming soon!)

## Installation

1. Install dependencies with UV:
```bash
uv sync
```

2. Or install with pip:
```bash
pip install paramiko textual textual-dev
```

## Configuration

1. Copy the example configuration:
```bash
cp example_config.py my_config.py
```

2. Update `my_config.py` with your cluster details:
```python
from src.config import Config

config = Config(
    hostname="your-cluster.example.com",
    port=22,
    username="your_username",
    private_key_path="~/.ssh/id_rsa"  # Optional
)
```

## Usage

### Test Connection

Test your SSH and HTCondor setup:
```bash
python -m src.main test
```

### Run the Application

Start the terminal interface:
```bash
python -m src.main
```

## Architecture

- **`src.config`**: Configuration management
- **`src.ssh.cluster`**: SSH client for remote connections
- **`src.htcondor.htcondor`**: HTCondor job management and parsing
- **`src.main`**: Main application and TUI

## HTCondor Job Information

The application retrieves and displays:
- Job ID (cluster.proc)
- Job Status (Idle, Running, Completed, etc.)
- Submit time
- Command and arguments
- Job requirements

## SSH Authentication

The application supports:
- SSH key authentication (recommended)
- Default SSH key locations (`~/.ssh/id_rsa`, etc.)
- Custom private key paths
- SSH agent integration via paramiko

## Development

### Project Structure
```
cluster_tools/
├── src/
│   ├── config.py          # Configuration classes
│   ├── main.py            # Main application
│   ├── ssh/
│   │   └── cluster.py     # SSH client implementation
│   └── htcondor/
│       └── htcondor.py    # HTCondor job management
├── pyproject.toml         # Project dependencies
└── README.md             # This file
```

### Running Tests
```bash
python -m src.main test
```

## Troubleshooting

### SSH Connection Issues
- Verify your SSH key is properly configured
- Check that you can manually SSH to the cluster
- Ensure the hostname and port are correct
- Try with verbose logging by setting `logging.DEBUG`

### HTCondor Issues
- Verify HTCondor is installed on the cluster
- Check that `condor_q` command works manually
- Ensure your user has permission to query jobs

## Next Steps

- [ ] Implement full Textual TUI for job monitoring
- [ ] Add job log viewing capabilities
- [ ] Support for job submission and management
- [ ] Add configuration file support
- [ ] Implement job filtering and search
- [ ] Add real-time job status updates

## Requirements

- Python 3.12+
- paramiko (SSH client)
- textual (Terminal UI framework)
- Access to an HTCondor cluster via SSH
