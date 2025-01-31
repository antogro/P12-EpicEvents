from rich.console import Console
from rich.table import Table
import os


class Display:
    def __init__(self) -> None:
        self.console = Console()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def table(
            self,
            title: str,
            items: list[dict],
            headers: list = [],
            exclude_headers=None
    ):
        print("\n")

        table = Table(
            title=title,
            padding=(0, 1),
            header_style="blue",
            title_style="violet",
            min_width=60
        )
        if not headers:
            try:
                headers = list(items[0].keys())
            except IndexError:
                headers = []

        if exclude_headers:
            headers = [
                header for header in headers if header not in exclude_headers
            ]

        for title in headers:
            table.add_column(str(title), style="cyan", justify="center")

        for item in items:
            values = [str(item.get(header, '')) for header in headers]
            table.add_row(*values)

        print('')
        self.console.print(table)
