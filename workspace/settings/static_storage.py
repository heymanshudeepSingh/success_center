"""
Handling for static files.

"ManifestStatic" makes browsers automatically update to newer versions of static files, instead of relying on an
outdated cached file. (Note this only works in production, not development. See official docs at
https://docs.djangoproject.com/en/3.1/ref/contrib/staticfiles/#django.contrib.staticfiles.storage.ManifestStaticFilesStorage
for details)

However, it has a fallback of giving server errors in production if a static file is not found.
We override the class to make it more forgiving in this regard.
Courtesy of https://timonweb.com/django/make-djangos-collectstatic-command-forgiving/
"""

# System Imports.
from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class ForgivingManifestStaticFilesStorage(ManifestStaticFilesStorage):
    """
    Override original class to be less strict.
    """
    def hashed_name(self, name, content=None, filename=None):
        try:
            result = super().hashed_name(name, content, filename)
        except ValueError:
            # When the file is missing, let's forgive and ignore that.
            result = name
        return result
