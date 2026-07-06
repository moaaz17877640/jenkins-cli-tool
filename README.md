# Jenkins CLI Tool

A powerful, command-line interface to interact with your Jenkins server via its REST API. This tool allows you to authenticate, list jobs, check their statuses, and trigger builds (including parameterized builds) directly from your terminal.

## Setup and Authentication

   ```bash
   pip install -e .
   ```
   This will install `jenkins-cli` as a global command on your system!

2. **Set up Environment Variables**:
   You can securely store your credentials using a `.env` file in the project directory. The tool will automatically load them.
   Create a `.env` file with the following content:
   ```env
   JENKINS_URL=https://your-jenkins-server.com
   JENKINS_USER=your_username
   JENKINS_TOKEN=your_api_token
   ```

   *(Alternatively, you can authenticate manually using the `login` command to cache your credentials locally: `jenkins-cli login --user <user> --token <token>`)*

## Docker Support

If you don't want to install Python dependencies on your host machine, you can run the CLI entirely via Docker. A production-ready `Dockerfile` and `.dockerignore` are included to build an extremely tiny Alpine-based container.

1. **Build the image**:
   ```bash
   docker build -t jenkins-cli .
   ```

2. **Run using your `.env` file**:
   ```bash
   # List jobs
   docker run --rm --env-file .env jenkins-cli list

   # Check status
   docker run --rm --env-file .env jenkins-cli status "Projects"
   ```

## How to use the CLI Help (`-h`)

The CLI comes with built-in documentation and usage examples for every command. 

To view the main help page and see the list of all available commands, run:
```bash
jenkins-cli -h
```

If you want to know how a specific command works, what parameters it accepts, or see examples of how to use it, append `-h` after the command name.

**Examples:**
* `jenkins-cli list -h`
* `jenkins-cli status -h`
* `jenkins-cli trigger -h`

## Common Commands

Here is a quick overview of the main commands:

### List Pipelines
List jobs in the root directory:
```bash
jenkins-cli list
```

List jobs inside a specific folder:
```bash
jenkins-cli list "Projects"
jenkins-cli list "Projects/Backend"
```

### Check Pipeline Status
Get the status of a job (whether it is buildable, and the status of its last build):
```bash
# Check a job in the root folder
jenkins-cli status "my-job"

# Check a job inside nested folders
jenkins-cli status "Projects/Backend/API/my-job"
```

### Trigger a Pipeline
Trigger a standard build:
```bash
jenkins-cli trigger "Projects/Backend/my-job"
```

Trigger a parameterized build using the `-p` (or `--param`) flag:
```bash
jenkins-cli trigger "my-job" -p branch=main -p run_tests=true

# If your parameter contains spaces, make sure to wrap the entire key=value in quotes!
jenkins-cli trigger "Projects/Backend/my-job" -p "CAUSE=GITHUB PR"
```

## Architecture Summary
- **`jenkins_client.py`**: Handles API requests using `requests.Session` and manages connection states and authentication fallback/storage.
- **`cli.py`**: The entrypoint that uses `argparse` to parse commands and render the built-in help text.
