from django.apps import AppConfig
# Creating apathway that passes through the signal in order for it to be triggered when running server
class ClientsConfig(AppConfig):
    name = 'clients'

    def ready(self):
        import clients.signal