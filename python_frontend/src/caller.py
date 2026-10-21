import logging
import subprocess
from pathlib import Path
from tkinter import messagebox

logger = logging.getLogger(__name__)


def _run(debug, key_path, java_class_path):
    command = [
        "java",
        "-cp",
        str(java_class_path),
        "controller.Controller",
        str(key_path),
    ]
    try:
        response = subprocess.run(
            command,
            cwd=Path(java_class_path).parents[1],
            capture_output=True,
            text=True,
            check=False,
        )
        Path(key_path).unlink(missing_ok=True)
        if debug:
            logger.debug(
                "Backend completed with exit code %d; stdout=%r; stderr=%r",
                response.returncode,
                response.stdout.strip(),
                response.stderr.strip(),
            )

        return response
    except OSError as error:
        Path(key_path).unlink(missing_ok=True)
        if debug:
            logger.exception("Unable to start the Java backend")
        messagebox.showerror("Error", f"Could not start the Java backend: {error}")
        return None


def call(debug, key_path, java_class_path):
    response = _run(debug, key_path, java_class_path)
    if response is None:
        return False
    if response.returncode != 0:
        messagebox.showerror("Error", response.stderr.strip() or "The backend rejected the request.")
    elif debug:
        logger.info("Backend accepted the request")
    return response.returncode == 0


def call_with_output(debug, key_path, java_class_path):
    response = _run(debug, key_path, java_class_path)
    if response is None:
        return False, ""
    if response.returncode != 0:
        messagebox.showerror("Error", response.stderr.strip() or "The backend rejected the request.")
        return False, ""
    return True, response.stdout
