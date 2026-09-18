from datetime import date

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

from cars.models import Brand, CarData, Configuration, Generation, Model, Protocol


PREFIX = "E2E-"
PASSWORD = "E2E-test-password-2026"
USERS = {
    "measurer": "e2e_measurer",
    "operator": "e2e_operator",
    "manager": "e2e_manager",
}


class Command(BaseCommand):
    help = "Prepare or clean isolated users and protocols for real frontend E2E tests."

    def add_arguments(self, parser):
        parser.add_argument("action", choices=("prepare", "cleanup"))

    def handle(self, *args, **options):
        if options["action"] == "cleanup":
            self.cleanup()
            self.stdout.write("E2E_FIXTURE_CLEANED")
            return

        users = {}
        for role, username in USERS.items():
            group, _ = Group.objects.get_or_create(name=role)
            user, _ = User.objects.get_or_create(username=username)
            user.set_password(PASSWORD)
            user.is_active = True
            user.save(update_fields=["password", "is_active"])
            user.groups.set([group])
            users[role] = user

        Protocol.objects.filter(protocol_number__startswith=PREFIX).delete()
        CarData.objects.filter(configuration__name__startswith=PREFIX).delete()
        Configuration.objects.filter(name__startswith=PREFIX).delete()
        Generation.objects.filter(name__startswith=PREFIX).delete()
        Model.objects.filter(name__startswith=PREFIX).delete()
        Brand.objects.filter(name__startswith=PREFIX).delete()

        brand = Brand.objects.create(
            name=f"{PREFIX}KIA",
            link="https://example.com/e2e-kia",
        )
        model = Model.objects.create(
            name=f"{PREFIX}RIO",
            link="https://example.com/e2e-rio",
            brand=brand,
        )
        generation_a = Generation.objects.create(
            name=f"{PREFIX}Generation A",
            link="https://example.com/e2e-generation-a",
            model=model,
            generation_num=1,
            date_start="01.2020",
            date_end="12.2021",
            region="europe",
        )
        generation_b = Generation.objects.create(
            name=f"{PREFIX}Generation B",
            link="https://example.com/e2e-generation-b",
            model=model,
            generation_num=2,
            date_start="01.2022",
            date_end="12.2023",
            region="europe",
        )
        configuration_a = Configuration.objects.create(
            name=f"{PREFIX}Configuration A",
            link="https://example.com/e2e-configuration-a",
            generation=generation_a,
            engine_name="E2E Engine A",
            date_start="01.2020",
            date_end="12.2021",
        )
        configuration_b = Configuration.objects.create(
            name=f"{PREFIX}Configuration B",
            link="https://example.com/e2e-configuration-b",
            generation=generation_b,
            engine_name="E2E Engine B",
            date_start="01.2022",
            date_end="12.2023",
        )
        CarData.objects.create(
            configuration=configuration_a,
            configuration_name=configuration_a.name,
            manufacture_year=2020,
            front_tires="185/65R15",
            rear_tires="185/65R15",
            fuel_type="petrol",
            transmission="automatic",
            drive_type="front",
        )
        CarData.objects.create(
            configuration=configuration_b,
            configuration_name=configuration_b.name,
            manufacture_year=2022,
            front_tires="195/55R16",
            rear_tires="195/55R16",
            fuel_type="petrol",
            transmission="automatic",
            drive_type="front",
        )
        first = Protocol.objects.create(
            protocol_number=f"{PREFIX}WORKFLOW",
            user=users["measurer"],
            protocol_date=date.today(),
            model=model,
            owner_name="E2E workflow owner",
            brand_name="KIA",
            commercial_name="RIO",
            status="measurement",
        )
        second = Protocol.objects.create(
            protocol_number=f"{PREFIX}LOCK",
            user=users["measurer"],
            protocol_date=date.today(),
            model=model,
            owner_name="E2E lock owner",
            brand_name="KIA",
            commercial_name="RIO",
            status="measurement",
        )
        selection = Protocol.objects.create(
            protocol_number=f"{PREFIX}SELECTION",
            user=users["measurer"],
            protocol_date=date.today(),
            model=model,
            owner_name="E2E selection owner",
            brand_name="KIA",
            commercial_name="RIO",
            status="measurement",
        )

        self.stdout.write(f"E2E_PROTOCOL_ID={first.id}")
        self.stdout.write(f"E2E_LOCK_PROTOCOL_ID={second.id}")
        self.stdout.write(f"E2E_SELECTION_PROTOCOL_ID={selection.id}")
        self.stdout.write(f"E2E_GENERATION_A_ID={generation_a.id}")
        self.stdout.write(f"E2E_GENERATION_B_ID={generation_b.id}")
        self.stdout.write(f"E2E_CONFIGURATION_A_ID={configuration_a.id}")
        self.stdout.write(f"E2E_CONFIGURATION_B_ID={configuration_b.id}")
        self.stdout.write(f"E2E_PASSWORD={PASSWORD}")

    def cleanup(self):
        Protocol.objects.filter(protocol_number__startswith=PREFIX).delete()
        CarData.objects.filter(configuration__name__startswith=PREFIX).delete()
        Configuration.objects.filter(name__startswith=PREFIX).delete()
        Generation.objects.filter(name__startswith=PREFIX).delete()
        Model.objects.filter(name__startswith=PREFIX).delete()
        Brand.objects.filter(name__startswith=PREFIX).delete()
        User.objects.filter(username__in=USERS.values()).delete()
