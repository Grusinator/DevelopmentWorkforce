from ninja import Router
from ninja.security import django_auth

router = Router()


@router.get('/profile', auth=django_auth)
def get_profile(request):
    user = request.auth
    return {"username": user.username, "email": user.email}
