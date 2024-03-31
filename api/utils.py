from api.models import User


def dashboard_callback(request, context):
    context.update({
        "variable": User.objects.all()
    })

    return context
