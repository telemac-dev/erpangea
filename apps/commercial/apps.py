from django.apps import AppConfig

class CommercialConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.commercial'
    label = 'commercial'

    def ready(self):
        import apps.commercial.signals
