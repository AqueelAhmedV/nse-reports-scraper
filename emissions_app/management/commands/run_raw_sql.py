from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Execute raw SQL queries'


    def handle(self, *args, **options):
        sql = input("Enter your SQL query: ")
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                if cursor.description:
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                    self.stdout.write("Columns: " + ", ".join(columns))
                    self.stdout.write("Results:")
                    for row in rows:
                        self.stdout.write(", ".join(str(cell) for cell in row))
                else:
                    self.stdout.write("Query executed successfully.")
        except Exception as e:
            self.stderr.write(f"An error occurred: {e}")