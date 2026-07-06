import argparse
import sys
from .jenkins_client import JenkinsClient

def main():
    # INFO: this is the main entry point of the script
    main_description = """
Jenkins CLI Tool
----------------
A powerful command-line interface to interact with your Jenkins server.
It automatically loads secrets from a `.env` file if present, or you can
use the `login` command to cache them.

Examples:
  jenkins-cli list
  jenkins-cli status "Projects/Backend"
"""
    parser = argparse.ArgumentParser(
        description=main_description,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # INFO: login command is used to login to jenkins server and save the credentials to ~/.jenkins_cli_config.json
    login_epilog = """
Examples:
  # Authenticate with username and token
  jenkins-cli login --user admin --token 11234abcd5678efgh
  
  # Authenticate with a custom URL
  jenkins-cli login --url https://my-jenkins.com --user admin --token secret
"""
    login_parser = subparsers.add_parser(
        "login", 
        help="Authenticate with Jenkins and save the session",
        description="Authenticate with Jenkins and save the credentials to ~/.jenkins_cli_config.json.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=login_epilog
    )
    login_parser.add_argument("--url", help="Jenkins server URL")
    login_parser.add_argument("--user", required=False, help="Jenkins username")
    login_parser.add_argument("--token", required=False, help="Jenkins API token")

    # List command
    list_epilog = """
Examples:
  # List all jobs and folders in the root directory
  jenkins-cli list
  
  # List jobs inside a specific folder
  jenkins-cli list "Projects"
  
  # List jobs inside a nested folder
  jenkins-cli list "Projects/Backend/API"
"""
    list_parser = subparsers.add_parser(
        "list", 
        help="List Jenkins jobs and folders",
        description="List all Jenkins jobs, pipelines, and folders in a specific path.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=list_epilog
    )
    list_parser.add_argument("path", nargs='?', default="", help="Path to the folder (leave empty to list root jobs)")

    # INFO: status command is used to get the status of a specific Jenkins job  
    status_epilog = """
Examples:
  # Check status of a root job
  jenkins-cli status "my-pipeline"
  
  # Check status of a job inside folders
  jenkins-cli status "Projects/Backend/API/my-pipeline"
"""
    status_parser = subparsers.add_parser(
        "status", 
        help="Get status of a specific Jenkins job",
        description="Retrieve the buildability and last build status of a specified Jenkins job.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=status_epilog
    )
    status_parser.add_argument("path", help="Path to the job (e.g., 'my-job' or 'folder/my-job')")

    # INFO: trigger command is used to trigger a Jenkins job  
    trigger_epilog = """
Examples:
  # Trigger a standard job
  jenkins-cli trigger "my-pipeline"
  
  # Trigger a job inside a folder
  jenkins-cli trigger "Projects/Backend/API/my-pipeline"
  
  # Trigger a parameterized job with string parameters
  jenkins-cli trigger "my-pipeline" -p branch=main -p environment=prod
"""
    trigger_parser = subparsers.add_parser(
        "trigger", 
        help="Trigger a Jenkins job (supports parameters)",
        description="Trigger a Jenkins job to build immediately. You can pass parameters using the -p flag.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=trigger_epilog
    )
    trigger_parser.add_argument("path", help="Path to the job (e.g., 'my-job' or 'folder/my-job')")
    trigger_parser.add_argument("-p", "--param", action="append", help="Build parameters in key=value format (can be used multiple times)")

    args = parser.parse_args()

    # INFO: if no command provided, print help
    if not args.command:
        parser.print_help()
        sys.exit(1)

    client = JenkinsClient()

    if args.command == "login":
        client.save_config(args.url, args.user, args.token)
    elif args.command == "list":
        client.list_jobs(args.path)
    elif args.command == "status":
        client.get_status(args.path)
    elif args.command == "trigger":
        params_dict = {}
        if args.param:
            for p in args.param:
                if "=" in p:
                    k, v = p.split("=", 1)
                    params_dict[k] = v
                else:
                    print(f"Invalid parameter format: {p}. Use key=value.")
                    sys.exit(1)
        client.trigger_build(args.path, params=params_dict if params_dict else None)
# INFO: this is the main entry point of the script
if __name__ == "__main__":
    main()
