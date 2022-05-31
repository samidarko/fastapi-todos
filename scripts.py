"""
Poetry commands
"""
import subprocess


def code_format():
    """
    Format the code.
    """
    subprocess.run(["isort", "."], check=False)
    subprocess.run(["black", "."], check=False)


def start():
    """
    Format the code.
    """
    subprocess.run(["uvicorn", "todos:app", "--reload"], check=False)
