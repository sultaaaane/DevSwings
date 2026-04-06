import sys
import time
import asyncio
from datetime import datetime
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.console import Console
from cli.client import DevSwingsClient
from cli.config import get_token

console = Console()


class GhostMode:
    def __init__(self):
        self.client = DevSwingsClient()
        self.active_session = None
        self.start_time = None

    def generate_status_line(self) -> Panel:
        if not self.start_time:
            return Panel(
                Text(
                    "👻 GHOST MODE: NO ACTIVE SESSION | Press Ctrl+C to exit",
                    style="bold #6c7086",
                ),
                style="on #11111b",
                expand=True,
            )

        delta = datetime.utcnow() - self.start_time
        minutes, seconds = divmod(int(delta.total_seconds()), 60)
        time_str = f"{minutes:02}:{seconds:02}"

        status_text = Text()
        status_text.append("⚡ DEVSWINGS ", style="bold #cba6f7")
        status_text.append(f"• SESSION ACTIVE ", style="#a6e3a1")
        status_text.append(f"[{time_str}] ", style="bold #fab387")
        status_text.append("• Project: General", style="#89b4fa")

        return Panel(status_text, style="on #181825", expand=True)

    async def run(self):
        if not get_token():
            console.print(
                "[red]Error: Not logged in. Please run the TUI ('python cli/app.py') to login first.[/red]"
            )
            return

        # Check for active session on start
        sessions = (
            await self.client.get_my_stats()
        )  # Could be refined to a 'get_active' endpoint
        # For ghost mode simplicity, we'll assume a session started if we just launched it
        # but in a real app, we'd poll the backend for the current open session.

        # Simulating start for now if one exists or just waiting for one
        self.start_time = datetime.utcnow()

        with Live(
            self.generate_status_line(), refresh_per_second=1, screen=False
        ) as live:
            try:
                while True:
                    live.update(self.generate_status_line())
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                console.print("\n[yellow]Ghost Mode Exited.[/yellow]")


if __name__ == "__main__":
    ghost = GhostMode()
    asyncio.run(ghost.run())
