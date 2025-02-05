import pathlib
from dataclasses import dataclass


@dataclass(frozen=True)
class SystemPaths:
	"""
    Defines paths to system-critical files and directories.

    This class provides constants representing the paths to the 'bin' directory and its contained files.
    It utilizes the pathlib library for path manipulation.

    Attributes:
        bin_folder (Path): Path to the 'bin' directory.
        mysql_config (Path): Path to the 'mysql_config.json' file within the 'bin' directory.
        doc_folder (Path): Path to the folder of docs.
        localizations (Path): Path to the file with localization.
    """
	bin_folder = pathlib.Path("bin")
	mysql_config = bin_folder / "mysql_config.json"
	env = bin_folder / ".env"
	doc_folder = bin_folder / "doc"
	localizations = bin_folder / "localizations.json"
