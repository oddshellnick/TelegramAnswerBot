import pathlib

class SystemPaths:
    """
    Defines paths to system-critical files and directories.

    This class provides constants representing the paths to the 'bin' directory and
    its contained files: 'auth_data.json' and 'doc.txt'. It utilizes the pathlib
    library for path manipulation.

    Attributes:
        bin_path (Path): Path to the 'bin' directory.
        auth_data (Path): Path to the 'auth_data.json' file within the 'bin' directory.
        doc (Path): Path to the 'doc.txt' file within the 'bin' directory.

    :Usage:
        # Access the path to the auth_data.json file:
        auth_filepath = SystemPaths.auth_data
    """
    bin_path = pathlib.Path("bin")
    auth_data = bin_path / "auth_data.json"
    doc = bin_path / "doc.txt"
