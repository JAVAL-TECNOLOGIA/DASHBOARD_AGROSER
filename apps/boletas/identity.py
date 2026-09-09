"""Validación compartida del registro inicial de identidad."""
from .models import WorkerIdentityProfile


def identity_complete(user):
    return WorkerIdentityProfile.objects.filter(
        user=user, consent_accepted=True, signature__gt="", photo__gt=""
    ).exists()
