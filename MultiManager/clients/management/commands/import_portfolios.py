import csv
from django.core.management.base import BaseCommand
from clients.models import Portfolio
from django.conf import settings
import os


class Command(BaseCommand):
    help = "Import portfolios from CSV"

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR, "clients", "data", "Graviton_List_MM.csv")

        with open(file_path, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                Portfolio.objects.get_or_create(
                    name=row["Portfolio_Name"].strip(),             # Portfolio_Name should be the true unique key
                    defaults={
                        'client_group': row["Client_Grouping"].strip(),
                        'risk_profile': row["Risk_Profile"].strip(),
                        'fund_category': row["Fund_Category"].strip(),
                    }
                )

        self.stdout.write(self.style.SUCCESS("Data imported successfully!"))