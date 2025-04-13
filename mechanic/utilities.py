from django.http import JsonResponse
from django.conf import settings
from django.db import connections, OperationalError


def test_database_connection(request):
    db_alias = request.GET.get("db_alias")

    if not db_alias or db_alias not in settings.DATABASES:
        return JsonResponse(
            {"status": "error", "message": "Invalid database alias"}, status=400
        )

    try:
        with connections[db_alias].cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse(
            {"status": "success", "message": f"Connection to {db_alias} successful"}
        )
    except OperationalError as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
