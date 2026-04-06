from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Button, Digits, Label, Input
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.screen import Screen, ModalScreen
from textual.binding import Binding
import asyncio
from datetime import datetime, timedelta

from cli.client import DevSwingsClient
from cli.config import save_token, get_token
from cli.git_utils import is_git_repo, get_git_commits, get_last_commit_sha


class ReportScreen(ModalScreen[None]):
    """A screen for displaying work reports and statistics."""

    def compose(self) -> ComposeResult:
        with Vertical(id="login-container"):
            yield Label("WORK REPORT", classes="stat-label")
            yield ScrollableContainer(id="report-content")
            yield Button("Close", id="close-btn", variant="success")

    def __init__(self, stats: dict):
        super().__init__()
        self.stats = stats

    async def on_mount(self) -> None:
        content = self.query_one("#report-content", ScrollableContainer)

        # Format the stats into readable sections
        duration_hrs = self.stats.get("total_duration_minutes", 0) / 60

        yield_list = [
            Label(f"Total Sessions: [b]{self.stats.get('total_sessions', 0)}[/b]"),
            Label(f"Total Duration: [b]{duration_hrs:.1f} hours[/b]"),
            Label(
                f"Flow State Frequency: [b]{self.stats.get('flow_sessions_count', 0)} sessions[/b]"
            ),
            Label(
                f"Avg Start Energy: [b]{self.stats.get('average_energy_start', 0):.1f}/10[/b]"
            ),
            Label(
                f"Avg End Energy: [b]{self.stats.get('average_energy_end', 0):.1f}/10[/b]"
            ),
            Label(f"Total Commits: [b]{self.stats.get('total_commits', 0)}[/b]"),
        ]

        for widget in yield_list:
            content.mount(widget)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close-btn":
            self.dismiss()


class SessionStartScreen(ModalScreen[dict]):
    """A screen for starting a work session with mood and energy."""

    def compose(self) -> ComposeResult:
        with Vertical(id="login-container"):
            yield Label("START WORK SESSION", classes="stat-label")
            yield Label("Current Mood (e.g., Focus, Tired, Excited)")
            yield Input(placeholder="Mood", id="mood")
            yield Label("Energy Level (1-10)")
            yield Input(placeholder="7", id="energy", type="integer")
            with Horizontal():
                yield Button("Start", variant="success", id="start-btn")
                yield Button("Cancel", id="cancel-btn")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "start-btn":
            mood = self.query_one("#mood", Input).value
            energy_str = self.query_one("#energy", Input).value
            try:
                energy = int(energy_str) if energy_str else 7
                if not (1 <= energy <= 10):
                    raise ValueError()
            except ValueError:
                self.notify("Energy must be between 1 and 10.", severity="error")
                return

            self.dismiss({"mood": mood, "energy": energy})
        elif event.button.id == "cancel-btn":
            self.dismiss(None)


class SessionEndScreen(ModalScreen[dict]):
    """A screen for ending a work session with notes and blockers."""

    def compose(self) -> ComposeResult:
        with Vertical(id="login-container"):
            yield Label("COMPLETING SESSION", classes="stat-label")
            yield Label("Post-Work Energy (1-10)")
            yield Input(placeholder="5", id="energy", type="integer")
            yield Label("Flow State Achieved?")
            with Horizontal(id="flow-toggle"):
                yield Button("YES", variant="success", id="flow-yes")
                yield Button("NO", variant="error", id="flow-no")
            yield Input(placeholder="Notes (What did you do?)", id="notes")
            yield Input(placeholder="Blockers (What slowed you down?)", id="blockers")
            yield Button(
                "Finish & Save", variant="success", id="save-btn", classes="full-width"
            )

    def __init__(self):
        super().__init__()
        self.flow_achieved = True

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "flow-yes":
            self.flow_achieved = True
            self.notify("Flow recorded!")
        elif event.button.id == "flow-no":
            self.flow_achieved = False
            self.notify("No flow this time.")
        elif event.button.id == "save-btn":
            energy_str = self.query_one("#energy", Input).value
            notes = self.query_one("#notes", Input).value
            blockers = self.query_one("#blockers", Input).value
            try:
                energy = int(energy_str) if energy_str else 5
            except ValueError:
                energy = 5

            self.dismiss(
                {
                    "energy_end": energy,
                    "flow_achieved": self.flow_achieved,
                    "notes": notes,
                    "blockers": blockers,
                }
            )


class CreateProjectScreen(ModalScreen[bool]):
    """A screen for creating a new project."""

    def compose(self) -> ComposeResult:
        with Vertical(id="login-container"):
            yield Label("NEW PROJECT", classes="stat-label")
            yield Input(placeholder="Project Name", id="project-name")
            yield Input(
                placeholder="Weekly Goal (hours)", id="project-goal", type="integer"
            )
            with Horizontal():
                yield Button("Create", variant="success", id="create-btn")
                yield Button("Cancel", id="cancel-btn")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create-btn":
            name = self.query_one("#project-name", Input).value
            goal_str = self.query_one("#project-goal", Input).value

            if not name:
                self.notify("Project name is required.", severity="error")
                return

            try:
                goal = int(goal_str) if goal_str else 0
            except ValueError:
                self.notify("Goal must be a number.", severity="error")
                return

            client = DevSwingsClient()
            success = await client.create_project(name, goal)
            if success:
                self.notify(f"Project '{name}' created!", severity="success")
                self.dismiss(True)
            else:
                self.notify("Failed to create project.", severity="error")
        elif event.button.id == "cancel-btn":
            self.dismiss(False)


class RegisterScreen(ModalScreen[bool]):
    """A screen for user registration."""

    def compose(self) -> ComposeResult:
        with Vertical(id="login-container"):
            yield Label("CREATE ACCOUNT", classes="stat-label")
            yield Input(placeholder="Email", id="email")
            yield Input(placeholder="Password", password=True, id="password")
            yield Input(
                placeholder="Confirm Password", password=True, id="confirm_password"
            )
            with Horizontal():
                yield Button("Register", variant="success", id="register-btn")
                yield Button("Back to Login", id="back-btn")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "register-btn":
            email = self.query_one("#email", Input).value
            password = self.query_one("#password", Input).value
            confirm = self.query_one("#confirm_password", Input).value

            if not email or not password:
                self.notify("Email and password are required.", severity="error")
                return

            if password != confirm:
                self.notify("Passwords do not match.", severity="error")
                return

            client = DevSwingsClient()
            success = await client.register(email, password)
            if success:
                self.notify(
                    "Registration successful! Please login.", severity="success"
                )
                self.dismiss(True)
            else:
                self.notify(
                    "Registration failed. Email might be taken or password too short.",
                    severity="error",
                )
        elif event.button.id == "back-btn":
            self.dismiss(False)


class LoginScreen(ModalScreen[bool]):
    """A screen for user login."""

    def compose(self) -> ComposeResult:
        with Vertical(id="login-container"):
            yield Label("WELCOME TO DEVSWINGS", classes="stat-label")
            yield Input(placeholder="Email", id="email")
            yield Input(placeholder="Password", password=True, id="password")
            with Horizontal():
                yield Button("Login", variant="success", id="login-btn")
                yield Button("Register", id="goto-register-btn")
                yield Button("Cancel", id="cancel-btn")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "login-btn":
            email = self.query_one("#email", Input).value
            password = self.query_one("#password", Input).value
            client = DevSwingsClient()
            token = await client.login(email, password)
            if token:
                save_token(token)
                self.dismiss(True)
            else:
                self.notify("Login Failed. Check your credentials.", severity="error")
        elif event.button.id == "goto-register-btn":
            self.app.push_screen(RegisterScreen(), self.on_register_result)
        elif event.button.id == "cancel-btn":
            self.dismiss(False)

    def on_register_result(self, registered: bool) -> None:
        """If they registered successfully, we stay on the login screen so they can login."""
        pass


class DevSwingsApp(App):
    """The main DevSwings TUI Dashboard."""

    CSS_PATH = "styles.tcss"
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("n", "new_project", "New Project", show=True),
        Binding("v", "view_report", "View Report", show=True),
        Binding("s", "start_session", "Start", show=True),
        Binding("e", "end_session", "Stop", show=True),
        Binding("l", "login_action", "Login", show=True),
        Binding("r", "refresh_action", "Refresh", show=True),
        Binding("m", "sync_commits", "Sync Git", show=True),
        Binding("g", "ghost_mode", "Ghost Mode", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.client = DevSwingsClient()
        self.active_session_id = None
        self.selected_project_id = None
        self.start_datetime = None
        self.timer_active = False
        self.last_sync_sha = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Label("STREAKS", classes="stat-label")
                yield Label("🔥 -- Days", id="streak-label", classes="stat-value")
                yield Static("")
                yield Label("PROJECTS", classes="stat-label")
                yield ScrollableContainer(id="project-list")

            with Container(id="main-content"):
                with Vertical(classes="focus-card"):
                    yield Label("DEEP WORK", classes="stat-label")
                    yield Digits("00:00", id="timer")
                    yield Static("")
                    with Horizontal():
                        yield Button("Start", variant="success", id="start-btn")
                        yield Button("Stop", variant="error", id="stop-btn")
        yield Footer()

    async def on_mount(self) -> None:
        if not get_token():
            self.push_screen(LoginScreen(), self.on_login_result)
        else:
            await self.refresh_data()
            self.run_worker(self.commit_watcher_loop())

    def on_login_result(self, logged_in: bool) -> None:
        if logged_in:
            self.run_worker(self.refresh_data())
            self.run_worker(self.commit_watcher_loop())

    async def commit_watcher_loop(self) -> None:
        """Background loop to watch for new commits."""
        while True:
            await asyncio.sleep(60)  # Check every minute
            if is_git_repo():
                current_sha = get_last_commit_sha()
                if current_sha and current_sha != self.last_sync_sha:
                    # New commit detected
                    await self.sync_commits_logic()

    async def sync_commits_logic(self, verbose: bool = False) -> None:
        """Core logic to sync git commits."""
        if not is_git_repo():
            if verbose:
                self.notify("Not in a Git repository.", severity="error")
            return

        if verbose:
            self.notify("Syncing commits...")

        commits = get_git_commits(limit=20)
        if not commits:
            return

        # Prepare for batch creation - using list of dicts
        formatted_commits = []
        for c in commits:
            fc = {"sha": c["sha"], "message": c["message"]}
            if self.selected_project_id:
                fc["project_id"] = str(self.selected_project_id)
            formatted_commits.append(fc)

        success = await self.client.batch_create_commits(formatted_commits)
        if success:
            self.last_sync_sha = commits[0]["sha"]
            if verbose:
                self.notify("Commits synced successfully!", severity="information")
        elif verbose:
            self.notify("Failed to sync commits.", severity="error")

    async def action_sync_commits(self) -> None:
        """Manual sync triggered by 'm' key."""
        await self.sync_commits_logic(verbose=True)

    async def refresh_data(self) -> None:
        """Fetch real data from the API."""
        if not get_token():
            return

        # 1. Update Streaks
        streak_data = await self.client.get_streak()
        streak_label = self.query_one("#streak-label", Label)
        days = streak_data.get("current_streak", 0)
        streak_label.update(f"🔥 {days} Day{'s' if days != 1 else ''}")

        # 2. Update Projects
        projects = await self.client.get_projects()
        project_list = self.query_one("#project-list", ScrollableContainer)
        # Clear existing
        for child in list(project_list.children):
            child.remove()

        for proj in projects:
            goal = proj.get("weekly_goal_hours", 0)
            name = proj.get("name")
            proj_id = proj.get("id")

            project_label = Label(f" {name} ", classes="project-item")
            project_label.project_id = proj_id

            if self.selected_project_id == proj_id:
                project_label.add_class("selected-project")

            project_list.mount(project_label)

    async def on_click(self, event) -> None:
        """Handle clicking anywhere in the UI."""
        # Find the widget at the click coordinates
        try:
            target, _ = self.get_widget_at(event.screen_x, event.screen_y)
            if hasattr(target, "project_id"):
                self.selected_project_id = target.project_id
                # Use simplified notification text since renderable might be complex
                self.notify(f"Project Selected!", severity="information")
                await self.refresh_data()
        except Exception:
            pass

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "start-btn":
            await self.action_start_session()
        elif event.button.id == "stop-btn":
            await self.action_end_session()

    async def action_start_session(self) -> None:
        if self.timer_active:
            self.notify("Session already active!", severity="warning")
            return

        def handle_start(data: dict):
            if data:
                self.run_worker(self.finalize_start_session(data))

        self.push_screen(SessionStartScreen(), handle_start)

    async def finalize_start_session(self, data: dict) -> None:
        session = await self.client.create_session(
            self.selected_project_id, data["energy"], data["mood"]
        )
        if session:
            self.active_session_id = session["id"]
            self.start_datetime = datetime.utcnow()
            self.timer_active = True
            self.notify("Deep Work Session Started!", severity="information")
            self.run_worker(self.update_timer_loop())
        else:
            self.notify("Error starting session. Check backend.", severity="error")

    async def action_end_session(self) -> None:
        if not self.timer_active:
            return

        def handle_end(data: dict):
            if data:
                self.run_worker(self.finalize_end_session(data))

        self.push_screen(SessionEndScreen(), handle_end)

    async def finalize_end_session(self, data: dict) -> None:
        success = await self.client.end_session(
            self.active_session_id,
            data["energy_end"],
            data["flow_achieved"],
            data["notes"],
            data["blockers"],
        )
        if success:
            self.timer_active = False
            self.active_session_id = None
            self.query_one("#timer", Digits).update("00:00")
            self.notify("Session Completed!", severity="success")
            await self.refresh_data()

    async def update_timer_loop(self) -> None:
        """Background worker loop to update the timer every second."""
        while self.timer_active:
            now = datetime.utcnow()
            delta = now - self.start_datetime
            minutes, seconds = divmod(int(delta.total_seconds()), 60)
            time_str = f"{minutes:02}:{seconds:02}"
            self.query_one("#timer", Digits).update(time_str)
            await asyncio.sleep(1)

    async def login_action(self) -> None:
        self.push_screen(LoginScreen(), self.on_login_result)

    async def action_new_project(self) -> None:
        self.push_screen(
            CreateProjectScreen(),
            lambda success: self.run_worker(self.refresh_data()) if success else None,
        )

    async def action_view_report(self) -> None:
        """Fetch stats and show the report screen."""
        self.notify("Fetching report...", severity="information")
        stats = await self.client.get_my_stats(self.selected_project_id)
        if stats:
            self.push_screen(ReportScreen(stats))
        else:
            self.notify("Could not fetch stats.", severity="error")

    async def on_mount(self) -> None:
        if not get_token():
            self.push_screen(LoginScreen(), self.on_login_result)
        else:
            await self.refresh_data()

    def on_login_result(self, logged_in: bool) -> None:
        if logged_in:
            self.run_worker(self.refresh_data())

    async def refresh_data(self) -> None:
        """Fetch real data from the API."""
        if not get_token():
            return

        # 1. Update Streaks
        streak_data = await self.client.get_streak()
        streak_label = self.query_one("#streak-label", Label)
        days = streak_data.get("current_streak", 0)
        streak_label.update(f"🔥 {days} Day{'s' if days != 1 else ''}")

        # 2. Update Projects
        projects = await self.client.get_projects()
        project_list = self.query_one("#project-list", ScrollableContainer)
        # Clear existing
        for child in list(project_list.children):
            child.remove()

        for proj in projects:
            goal = proj.get("weekly_goal_hours", 0)
            name = proj.get("name")
            proj_id = proj.get("id")

            project_label = Label(f" {name} ", classes="project-item")
            project_label.project_id = proj_id

            if self.selected_project_id == proj_id:
                project_label.add_class("selected-project")

            project_list.mount(project_label)

    async def on_click(self, event) -> None:
        """Handle clicking anywhere in the UI."""
        # Find the widget at the click coordinates
        try:
            target, _ = self.get_widget_at(event.screen_x, event.screen_y)
            if hasattr(target, "project_id"):
                self.selected_project_id = target.project_id
                # Use simplified notification text since renderable might be complex
                self.notify(f"Project Selected!", severity="information")
                await self.refresh_data()
        except Exception:
            pass

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "start-btn":
            await self.action_start_session()
        elif event.button.id == "stop-btn":
            await self.action_end_session()

    async def action_start_session(self) -> None:
        if self.timer_active:
            self.notify("Session already active!", severity="warning")
            return

        def handle_start(data: dict):
            if data:
                self.run_worker(self.finalize_start_session(data))

        self.push_screen(SessionStartScreen(), handle_start)

    async def finalize_start_session(self, data: dict) -> None:
        session = await self.client.create_session(
            self.selected_project_id, data["energy"], data["mood"]
        )
        if session:
            self.active_session_id = session["id"]
            self.start_datetime = datetime.utcnow()
            self.timer_active = True
            self.notify("Deep Work Session Started!", severity="information")
            self.run_worker(self.update_timer_loop())
        else:
            self.notify("Error starting session. Check backend.", severity="error")

    async def action_end_session(self) -> None:
        if not self.timer_active:
            return

        def handle_end(data: dict):
            if data:
                self.run_worker(self.finalize_end_session(data))

        self.push_screen(SessionEndScreen(), handle_end)

    async def finalize_end_session(self, data: dict) -> None:
        success = await self.client.end_session(
            self.active_session_id,
            data["energy_end"],
            data["flow_achieved"],
            data["notes"],
            data["blockers"],
        )
        if success:
            self.timer_active = False
            self.active_session_id = None
            self.query_one("#timer", Digits).update("00:00")
            self.notify("Session Completed!", severity="success")
            await self.refresh_data()

    async def update_timer_loop(self) -> None:
        """Background worker loop to update the timer every second."""
        while self.timer_active:
            now = datetime.utcnow()
            delta = now - self.start_datetime
            minutes, seconds = divmod(int(delta.total_seconds()), 60)
            time_str = f"{minutes:02}:{seconds:02}"
            self.query_one("#timer", Digits).update(time_str)
            await asyncio.sleep(1)

    def action_login_action(self) -> None:
        self.push_screen(LoginScreen(), self.on_login_result)

    async def action_refresh_action(self) -> None:
        await self.refresh_data()

    def action_quit(self) -> None:
        self.exit()

    async def action_ghost_mode(self) -> None:
        """Trigger the Ghost Mode status script in the existing terminal."""
        if not self.active_session_id:
            self.notify(
                "Must have an active session to enter Ghost Mode!", severity="warning"
            )
            return

        self.notify("Entering Ghost Mode. Closing TUI...", severity="information")
        # In a real environment, you might spawn a process, but for this exercise
        # we'll suggest running it from the CLI.
        self.exit(result="ghost")


if __name__ == "__main__":
    app = DevSwingsApp()
    app.run()
