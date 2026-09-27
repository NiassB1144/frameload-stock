
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = "Crée les groupes ADMIN, MANAGER et EMPLOYEE"

    def handle(self, *args, **kwargs):

        groupes = [
            "ADMIN",
            "MANAGER",
            "EMPLOYEE",
        ]

        for nom in groupes:
            groupe, created = Group.objects.get_or_create(name=nom)

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Groupe {nom} créé avec succès."
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Groupe {nom} existe déjà."
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Les groupes ont été préparés."
            )
        )

