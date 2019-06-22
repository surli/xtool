import logging, os
from packaging import version as Version

from .configuration import ConfigManager
from .configuration import Environment

from .downloaders import VersionDownloader
from .downloaders import SnapshotVersionDownloader

class VersionManager:
    logger = logging.getLogger('VersionManager')
    # version from which we started to use platform instead of enterprise
    migrationVersion = Version.parse("9.5")

    def __init__(self, configManager):
        self.configManager = configManager

    def getArchiveBaseName(self, version):
        if (Version.parse(version) >= self.migrationVersion):
            return 'xwiki-platform-distribution-flavor-jetty-hsqldb-{}'.format(version)
        else:
            return 'xwiki-enterprise-jetty-hsqldb-{}'.format(version)

    # Generate the file name used for a given version
    def getArchiveName(self, version):
        return '{}.zip'.format(self.getArchiveBaseName(version))

    # Generate the file path used for a given version
    def getArchivePath(self, version):
        return '{}/{}'.format(Environment.dataDir, self.getArchiveName(version))

    def download(self, version):
        if (version.endswith('-SNAPSHOT')):
            SnapshotVersionDownloader(version, self, self.configManager).download()
        else:
            # Use the standard version downloader
            VersionDownloader(version, self, self.configManager).download()

    def delete(self, version):
        os.remove(self.getArchivePath(version))

    def clean(self):
        instances = self.configManager.instances()
        versions = self.configManager.versions().copy()
        for instance in instances:
            if instance["version"] in versions:
                versions.remove(instance["version"])
        for version in versions:
            self.delete(version)