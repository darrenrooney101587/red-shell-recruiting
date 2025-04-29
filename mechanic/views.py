import os

from django.conf import settings
from red_shell_recruiting.tasks import test_redis_celery_connection
import django
from django.http import JsonResponse
from django.shortcuts import render


def index(request):
    sensitive_settings = [
        "SECRET_KEY",
        "EMAIL_HOST_USER",
        "EMAIL_USE_TLS",
        "EMAIL_PORT",
        "EMAIL_BACKEND",
        "PASSWORD_RESET_TIMEOUT",
        "PASSWORD_HASHERS",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
    ]

    django_env_list = [
        {
            "name": "Django Version",
            "value": django.get_version(),
        }
    ]

    for setting_name in dir(settings):
        if setting_name.isupper() and setting_name not in sensitive_settings:
            setting_value = getattr(settings, setting_name)

            if setting_name == "DATABASES":
                for db_name, db_config in setting_value.items():
                    django_env_list.extend(
                        [
                            {
                                "name": f"DATABASE_{db_name.upper()}_ENGINE",
                                "value": db_config["ENGINE"],
                            },
                            {
                                "name": f"DATABASE_{db_name.upper()}_NAME",
                                "value": db_config["NAME"],
                            },
                            {
                                "name": f"DATABASE_{db_name.upper()}_USER",
                                "value": db_config["USER"],
                            },
                            {
                                "name": f"DATABASE_{db_name.upper()}_HOST",
                                "value": db_config["HOST"],
                            },
                            {
                                "name": f"DATABASE_{db_name.upper()}_PORT",
                                "value": db_config["PORT"],
                            },
                        ]
                    )
            else:
                # convert complex objects to string
                if isinstance(setting_value, (dict, list, tuple)):
                    setting_value = str(setting_value)
                django_env_list.append(
                    {
                        "name": setting_name,
                        "value": setting_value,
                    }
                )

    context = {
        "django_env_list": django_env_list,
        "databases": settings.DATABASES.keys(),
    }

    if (
        request.user.is_authenticated
        and request.user.is_superuser
        and request.GET.get("show_env")
        and str(request.user).strip() == "darren.rooney"
    ):
        context["env_list"] = [{"name": k, "value": v} for k, v in os.environ.items()]

    return render(request, "mechanic/index.html", context)


def redis_celery_connection(request):
    try:
        result = test_redis_celery_connection.delay()
        result.get(timeout=5)
        return JsonResponse({"message": "Redis and Celery are connected!"})
    except Exception as e:
        return JsonResponse(
            {"message": f"Redis/Celery connection failed: {str(e)}"}, status=500
        )
