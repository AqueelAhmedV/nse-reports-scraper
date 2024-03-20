from django.core.management.base import BaseCommand
from django.db import connection
class Command(BaseCommand):
    help = 'Execute raw SQL queries'

    # ANSI escape codes for colors
    COLORS = {
        'HEADER': '\033[95m',
        'OKBLUE': '\033[94m',
        'OKGREEN': '\033[92m',
        'WARNING': '\033[93m',
        'FAIL': '\033[91m',
        'ENDC': '\033[0m',
        'BOLD': '\033[1m',
        'UNDERLINE': '\033[4m'
    }

    def colored_output(self, text, color):
        return f"{self.COLORS[color]}{text}{self.COLORS['ENDC']}"

    def handle(self, *args, **options):
        prompt = self.colored_output("Enter your SQL query: ", 'OKBLUE')
        sql = input(prompt)
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                if cursor.description:
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                    self.stdout.write(self.colored_output("Columns: ", 'OKBLUE') + ", ".join(columns))
                    self.stdout.write(self.colored_output("Results:", 'OKGREEN'))
                    for row in rows:
                        self.stdout.write(", ".join(self.colored_output(str(cell), 'WARNING') for cell in row))
                else:
                    self.stdout.write(self.colored_output("No Results.", 'WARNING'))
        except Exception as e:
            self.stderr.write(self.colored_output(f"An error occurred: {e}", 'FAIL'))
