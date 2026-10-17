from django.contrib.auth.views import LoginView


class RoleLoginView(LoginView):
    """Login page that always lands on /afterlogin so each role reaches its own dashboard."""
    redirect_authenticated_user = False
