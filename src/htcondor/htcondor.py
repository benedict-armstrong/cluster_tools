import json
from typing import List, Dict, Optional

from ..ssh.cluster import SSHClient
from .types import CondorJob


class HTCondorClient:
    """Client for interacting with HTCondor through SSH."""

    def __init__(self, ssh_client: SSHClient):
        self.ssh_client = ssh_client

    def get_user_jobs(self, username: str) -> List[CondorJob]:
        """
        Get all jobs for a specific user.

        Args:
            username: Username to query jobs for

        Returns:
            List of CondorJob objects

        Raises:
            RuntimeError: If command execution fails or returns invalid data
        """
        command = f"condor_q {username} -json"

        try:
            exit_code, stdout, stderr = self.ssh_client.execute_command(command)

            if exit_code != 0:
                error_msg = f"condor_q command failed (exit code {exit_code}): {stderr}"
                print(error_msg)
                raise RuntimeError(error_msg)

            if not stdout.strip():
                print(f"No jobs found for user {username}")
                return []

            # Parse JSON output
            try:
                job_data = json.loads(stdout)
                jobs = []

                # HTCondor JSON format can be a list of jobs or empty
                if isinstance(job_data, list):
                    for job_dict in job_data:
                        try:
                            job = CondorJob.from_dict(job_dict)
                            jobs.append(job)
                        except Exception as e:
                            print(f"Failed to parse job data: {e}")
                            continue

                print(f"Retrieved {len(jobs)} jobs for user {username}")
                return jobs

            except json.JSONDecodeError as e:
                error_msg = f"Failed to parse condor_q JSON output: {e}"
                print(error_msg)
                raise RuntimeError(error_msg)

        except Exception as e:
            print(f"Failed to retrieve jobs for user {username}: {e}")
            raise

    def get_job_status_summary(self, username: str) -> Dict[str, int]:
        """
        Get a summary of job statuses for a user.

        Args:
            username: Username to query jobs for

        Returns:
            Dictionary with status names as keys and counts as values
        """
        jobs = self.get_user_jobs(username)
        summary = {}

        for job in jobs:
            status = job.job_status_name
            summary[status] = summary.get(status, 0) + 1

        return summary

    def get_job_logs(self, job_id: str) -> Optional[str]:
        """
        Get log file content for a specific job (placeholder for future implementation).

        Args:
            job_id: Job ID in format "cluster.proc"

        Returns:
            Log content if available, None otherwise
        """
        # This is a placeholder - actual implementation would depend on
        # HTCondor configuration and log file locations
        print(f"Log retrieval not yet implemented for job {job_id}")
        return None
