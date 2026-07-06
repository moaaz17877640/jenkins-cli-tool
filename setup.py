from setuptools import setup, find_packages
#INFO:this make the script executable from anywhere by running 'jenkins-cli'
#INFO: after running 'pip install -e .' in the project directory
setup(
    name="jenkins-cli",
    version="1.0.0",
    description="A powerful command-line interface to interact with your Jenkins server.",
    packages=find_packages(),
    install_requires=[
        "requests",
        "python-dotenv"
    ],
    entry_points={
        "console_scripts": [
            "jenkins-cli=jenkins_cli.cli:main",
        ],
    },
    python_requires=">=3.6",
)
