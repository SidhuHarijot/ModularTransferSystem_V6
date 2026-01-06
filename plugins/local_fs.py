import os
from core.interfaces import IDataSource, IDataDest
from core.smart_scanner import SmartScanner


class LocalSource(IDataSource):
    @property
    def display_name(self):
        return "Local File System"

    def scan_to_manifest(self, path, job_mgr, config=None):
        """
        The original interface supports a single `path`, but this project
        scans as *pairs* (src -> dest) so destinations can be computed and
        batches can be formed correctly.

        Use `scan_pair_to_manifest(src, dest, job_mgr, config)` instead.
        """
        raise RuntimeError(
            "Use scan_pair_to_manifest(src, dest, job_mgr, config) for this project."
        )


def scan_pair_to_manifest(src, dest, job_mgr, config=None):
    """Scan one src→dest pair into JobManager batches."""
    if config is None:
        config = {}
    scanner = SmartScanner(job_mgr)
    scanner.process_path(src, dest, config)


class LocalDest(IDataDest):
    @property
    def display_name(self):
        return "Local Folder"

    def exists(self, path):
        return os.path.exists(path)

    def ensure_dir(self, path):
        dir_path = path if os.path.splitext(path)[1] == "" else os.path.dirname(path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
