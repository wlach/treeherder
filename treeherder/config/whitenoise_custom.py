import re

from whitenoise.middleware import WhiteNoiseMiddleware


class CustomWhiteNoise(WhiteNoiseMiddleware):
    """
    Adds two additional features to WhiteNoise:

    1) Serving index pages for directory paths (such as the site root).
    2) Setting long max-age headers for files created by grunt-cache-busting.
    """

    # Matches grunt-cache-busting's style of hash filenames. eg:
    #   index.min-feae259e2c205af67b0e91306f9363fa.js
    IMMUTABLE_FILE_RE = re.compile(r'\.min-[a-f0-9]{32}\.(js|css)$')
    INDEX_NAME = 'index.html'

    def update_files_dictionary(self, *args):
        """Add support for serving index pages for directory paths."""
        super(CustomWhiteNoise, self).update_files_dictionary(*args)
        index_page_suffix = "/" + self.INDEX_NAME
        index_name_length = len(self.INDEX_NAME)
        index_files = {}
        for url, static_file in self.files.items():
            # Add an additional fake filename to serve index pages for '/'.
            if url.endswith(index_page_suffix):
                index_files[url[:-index_name_length]] = static_file
        self.files.update(index_files)

    def find_file(self, url):
        """Add support for serving index pages for directory paths when in DEBUG mode."""
        # In debug mode, find_file() is used to serve files directly from the filesystem
        # instead of using the list in `self.files`, so we append the index filename so
        # that will be served if present.
        if url[-1] == '/':
            url += self.INDEX_NAME
        return super(CustomWhiteNoise, self).find_file(url)

    def is_immutable_file(self, path, url):
        """Support grunt-cache-busting style filenames when setting long max-age headers."""
        if self.IMMUTABLE_FILE_RE.search(url):
            return True
        # Otherwise fall back to the default method, so we catch filenames in the
        # style output by GzipManifestStaticFilesStorage during collectstatic. eg:
        #   bootstrap.min.abda843684d0.js
        return super(CustomWhiteNoise, self).is_immutable_file(path, url)
