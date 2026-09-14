# note: Import Python tools used to retrieve basic
# read-only information about the local computer.
from datetime import datetime
from pathlib import Path
import platform
import socket


# note: Import the JARVIS tool-registration system.
from tools.registry import register_tool


# note: Retrieve basic information about the computer
# running JARVIS without modifying the system.
def get_system_info():

    """Return basic read-only system information."""

    return {
        "operating_system": platform.system(),
        "os_version": platform.release(),
        "computer_name": socket.gethostname(),
        "architecture": platform.machine(),
        "python_version": platform.python_version()
    }


# note: Retrieve the current local date, time, and timezone
# from the computer running JARVIS.
def get_current_datetime():

    """Return the current local date and time."""

    current_time = datetime.now().astimezone()

    return {
        "date": current_time.strftime(
            "%Y-%m-%d"
        ),
        "time": current_time.strftime(
            "%I:%M:%S %p"
        ),
        "timezone": current_time.tzname(),
        "utc_offset": current_time.strftime(
            "%z"
        )
    }


# note: List the files and folders located directly inside
# the JARVIS project directory without modifying anything.
def list_project_directory():

    """Return the contents of the JARVIS project directory."""

    project_directory = Path.cwd()

    items = []

    for item in sorted(
        project_directory.iterdir(),
        key=lambda path: path.name.lower()
    ):

        # note: Skip hidden files and folders so normal tool
        # responses remain focused on project content.
        if item.name.startswith(
            "."
        ):

            continue

        item_type = (
            "directory"
            if item.is_dir()
            else "file"
        )

        items.append(
            {
                "name": item.name,
                "type": item_type
            }
        )

    return {
        "directory": str(
            project_directory
        ),
        "items": items
    }


# note: Register the system-information tool with an explicit
# description of the read-only information it can retrieve.
register_tool(
    name="get_system_info",
    description=(
        "Retrieve read-only system information including "
        "the operating system, OS version, computer name, "
        "computer architecture, and Python version."
    ),
    permission_level="safe_read",
    function=get_system_info
)


# note: Register the current-date-and-time tool as a
# read-only JARVIS capability.
register_tool(
    name="get_current_datetime",
    description=(
        "Retrieve the current local date, time, "
        "timezone, and UTC offset."
    ),
    permission_level="safe_read",
    function=get_current_datetime
)


# note: Register the project-directory listing tool.
# This tool currently lists only the JARVIS project root.
register_tool(
    name="list_project_directory",
    description=(
        "List the files and folders directly inside "
        "the JARVIS project directory."
    ),
    permission_level="safe_read",
    function=list_project_directory
)
