from django.apps import AppConfig


class CaeHomeConfig(AppConfig):
    name = 'cae_home'
    verbose_name = 'CAE Home'

    def ready(self):
        # Connect signals.
        from . import signals
