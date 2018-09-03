"""
Core route handling for channels websockets.
"""

from channels.routing import ProtocolTypeRouter


application = ProtocolTypeRouter({
    # Note, django views are "added by default".
})
