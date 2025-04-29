def get_client_ip_address(request):
    """
    Retrieve client IP address while handling cases where the app is behind a proxy.
    """
    x_forwarded_for = request.META.get("HTTP_X_REAL_IP")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")

    if not ip:
        raise ValueError("Could not determine client IP address")
    return ip


def get_saml_metadata_from_db():
    import tempfile

    # from bms_security.models import AgencyConfiguration
    #
    # config = AgencyConfiguration.objects.get(
    #     identifier="BMS_ADMIN",
    #     agency_id=-1,
    #     auth_type=AgencyConfiguration.AUTH_FILE,
    # )
    #
    # if not config.auth_config:
    #     raise ValueError("No SAML metadata found in AgencyConfiguration")
    #
    # metadata_bytes = (
    #     config.auth_config.encode("utf-8")
    #     if isinstance(config.auth_config, str)
    #     else config.auth_config
    # )

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xml", mode="wb")
    # tmp.write(metadata_bytes)
    tmp.flush()
    return tmp.name
