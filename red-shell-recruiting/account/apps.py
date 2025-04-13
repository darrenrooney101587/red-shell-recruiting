from django.apps import AppConfig

from app_admin import settings


class AccountsConfig(AppConfig):
    name = "account"

    # def ready(self):
    #     from account.utilities import get_saml_metadata_from_db
    #
    #     try:
    #         settings.SAML_CONFIG["metadata"]["local"] = [get_saml_metadata_from_db()]
    #         print("SAML metadata loaded from DB and injected into config.")
    #     except Exception as e:
    #         print(f"Failed to load SAML metadata from DB: {e}")
