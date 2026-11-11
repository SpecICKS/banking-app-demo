import subprocess
from pathlib import Path
from tkinter import messagebox


def _run(debug, key_path, java_class_path):
    command = [
        "java",
        f"-Dbackend.debug={'true' if debug else 'false'}",
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
        return response
    except OSError as error:
        Path(key_path).unlink(missing_ok=True)
        messagebox.showerror("Error", f"Could not start the Java backend: {error}")
        return None


def call(debug, key_path, java_class_path):
    response = _run(debug, key_path, java_class_path)
    if response is None:
        return False
    if response.returncode != 0:
        messagebox.showerror("Error", response.stderr.strip() or "The backend rejected the request.")
    return response.returncode == 0


def call_with_output(debug, key_path, java_class_path):
    response = _run(debug, key_path, java_class_path)
    if response is None:
        return False, ""
    if response.returncode != 0:
        messagebox.showerror("Error", response.stderr.strip() or "The backend rejected the request.")
        return False, ""
    return True, response.stdout
