"""
Realistic load profile for SWA ERP based on actual user journeys.

User roles and their typical workflows:
- PM (Project Manager): Full access - dashboards, project CRUD, client management, time approval, exports
- Designer: Project detail, tasks, time entries, documents
- Viewer: Read-only dashboards, project/client lists and details

Weight distribution based on SWA staff activities (from MEETINGS_MASTER.md):
- 60% reads (dashboards, lists, detail views)
- 25% periodic writes (create inquiry, log time, issue token, document ref)
- 10% heavy operations (PDF export, report generation)
- 5% authentication (login/refresh)
"""
import random
import uuid
from datetime import date, timedelta
from locust import HttpUser, task, between, events
from locust.exception import StopUser


class AuthenticatedUser(HttpUser):
    """Base class with authentication handling."""
    
    abstract = True  # Don't instantiate this base class
    wait_time = between(1, 3)  # Think time between requests
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None
        self.refresh_token = None
        self.user_id = None
        self.role = None
        self.project_ids = []
        self.client_ids = []
        self.task_ids = []
    
    def on_start(self):
        """Login and fetch reference data on start."""
        self.login()
        if self.token:
            self.fetch_reference_data()
    
    def login(self):
        """Authenticate and store tokens."""
        email = getattr(self, 'test_email', 'pm@swa.local')
        password = getattr(self, 'test_password', 'pm123!')
        
        with self.client.post(
            "/api/auth/login",
            json={"email": email, "password": password},
            catch_response=True,
            name="/api/auth/login"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                self.client.headers["Authorization"] = f"Bearer {self.token}"
                response.success()
            else:
                response.failure(f"Login failed: {response.status_code} - {response.text}")
    
    def refresh_access_token(self):
        """Refresh the access token."""
        if not self.refresh_token:
            return False
        
        with self.client.post(
            "/api/auth/refresh",
            json={"refresh_token": self.refresh_token},
            catch_response=True,
            name="/api/auth/refresh"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.client.headers["Authorization"] = f"Bearer {self.token}"
                response.success()
                return True
            else:
                response.failure(f"Token refresh failed: {response.status_code}")
                return False
    
    def fetch_reference_data(self):
        """Fetch project and client IDs for use in subsequent requests."""
        # Fetch projects
        with self.client.get(
            "/api/projects?page_size=100",
            catch_response=True,
            name="/api/projects (list)"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.project_ids = [p["id"] for p in data.get("items", [])]
                response.success()
            else:
                response.failure(f"Failed to fetch projects: {response.status_code}")
        
        # Fetch clients
        with self.client.get(
            "/api/clients?page_size=100",
            catch_response=True,
            name="/api/clients (list)"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.client_ids = [c["id"] for c in data.get("items", [])]
                response.success()
            else:
                response.failure(f"Failed to fetch clients: {response.status_code}")


class PMUser(AuthenticatedUser):
    """Project Manager - Full access user.
    
    Typical PM workflow:
    1. Check executive dashboard (high priority)
    2. Browse project list and details
    3. Manage clients (list, create, view)
    4. Approve timesheets
    5. Generate exports (PDF reports)
    6. Create inquiries/BOQs occasionally
    """
    weight = 5  # 50% of users are PMs
    
    test_email = "pm@swa.local"
    test_password = "pm123!"
    
    def on_start(self):
        super().on_start()
        # PMs start by checking the executive dashboard
        self.check_executive_dashboard()
    
    @task(15)
    def check_executive_dashboard(self):
        """Primary dashboard - most frequent PM action."""
        self.client.get(
            "/api/dashboard/executive",
            name="/api/dashboard/executive"
        )
    
    @task(10)
    def check_project_health_report(self):
        """Project health report."""
        self.client.get(
            "/api/reports/project-health",
            name="/api/reports/project-health"
        )
    
    @task(10)
    def list_projects(self):
        """List projects with pagination."""
        page = random.randint(1, 3)
        self.client.get(
            f"/api/projects?page={page}&page_size=20",
            name="/api/projects (list paginated)"
        )
    
    @task(8)
    def get_project_detail(self):
        """View a specific project detail."""
        if not self.project_ids:
            return
        project_id = random.choice(self.project_ids)
        self.client.get(
            f"/api/projects/{project_id}",
            name="/api/projects/{id} (detail)"
        )
    
    @task(6)
    def list_clients(self):
        """List clients."""
        page = random.randint(1, 2)
        self.client.get(
            f"/api/clients?page={page}&page_size=20",
            name="/api/clients (list paginated)"
        )
    
    @task(4)
    def get_client_detail(self):
        """View a specific client detail."""
        if not self.client_ids:
            return
        client_id = random.choice(self.client_ids)
        self.client.get(
            f"/api/clients/{client_id}",
            name="/api/clients/{id} (detail)"
        )
    
    @task(4)
    def list_my_tasks(self):
        """List my tasks."""
        self.client.get(
            "/api/tasks/my-tasks?page=1&page_size=20",
            name="/api/tasks/my-tasks (list)"
        )
    
    @task(3)
    def list_timesheets(self):
        """List timesheets for approval."""
        self.client.get(
            "/api/timesheets?page=1&page_size=20",
            name="/api/timesheets (list)"
        )
    
    @task(2)
    def create_inquiry(self):
        """Create a new inquiry (periodic write)."""
        if not self.client_ids:
            return
        client_id = random.choice(self.client_ids)
        # Fetch client name
        with self.client.get(
            f"/api/clients/{client_id}",
            catch_response=True,
            name="/api/clients/{id} (for inquiry)"
        ) as resp:
            if resp.status_code == 200:
                client_name = resp.json().get("name", "Unknown Client")
            else:
                client_name = "Unknown Client"
        
        self.client.post(
            "/api/inquiries",
            json={
                "inquiry_date": str(date.today()),
                "inquiry_type": "general",
                "inquiry_source": "web",
                "client_name": client_name,
                "requirement_summary": f"Load test inquiry {random.randint(1, 10000)}",
                "priority": "medium",
                "status": "New"
            },
            name="/api/inquiries (create)"
        )
    
    @task(2)
    def create_project(self):
        """Create a new project (periodic write)."""
        if not self.client_ids:
            return
        client_id = random.choice(self.client_ids)
        self.client.post(
            "/api/projects",
            json={
                "client_id": str(client_id),
                "name": f"Load Test Project {random.randint(1, 10000)}",
                "code": f"LT-{random.randint(1000, 9999)}",
                "description": "Created during load testing",
                "status": "Lead"
            },
            name="/api/projects (create)"
        )
    
    @task(2)
    def generate_project_summary_pdf(self):
        """Generate project summary PDF (heavy operation)."""
        if not self.project_ids:
            return
        project_id = random.choice(self.project_ids)
        self.client.get(
            f"/api/exports/projects/{project_id}/summary.pdf",
            name="/api/exports/projects/{id}/summary.pdf"
        )
    
    @task(1)
    def generate_financial_report_pdf(self):
        """Generate financial report PDF (heavy operation)."""
        end_date = date.today()
        start_date = end_date - timedelta(days=90)
        self.client.get(
            f"/api/exports/reports/financial.pdf?start_date={start_date}&end_date={end_date}",
            name="/api/exports/reports/financial.pdf"
        )
    
    @task(1)
    def export_project_slides(self):
        """Export project slides (heavy operation)."""
        if not self.project_ids:
            return
        project_id = random.choice(self.project_ids)
        self.client.get(
            f"/api/exports/projects/{project_id}/slides.pdf",
            name="/api/exports/projects/{id}/slides.pdf"
        )


class DesignerUser(AuthenticatedUser):
    """Designer - Project execution focused.
    
    Typical Designer workflow:
    1. View assigned projects
    2. View/update tasks
    3. Log time entries
    4. View documents
    5. Submit timesheets
    """
    weight = 3  # 30% of users are Designers
    
    test_email = "pm@swa.local"  # Reuse PM for now since we only seeded 2 users
    test_password = "pm123!"
    
    @task(12)
    def list_my_projects(self):
        """List projects."""
        self.client.get(
            "/api/projects?page=1&page_size=20",
            name="/api/projects (list) [designer]"
        )
    
    @task(10)
    def get_project_detail(self):
        """View project detail."""
        if not self.project_ids:
            return
        project_id = random.choice(self.project_ids)
        self.client.get(
            f"/api/projects/{project_id}",
            name="/api/projects/{id} (detail) [designer]"
        )
    
    @task(8)
    def list_project_tasks(self):
        """List tasks for a project."""
        if not self.project_ids:
            return
        project_id = random.choice(self.project_ids)
        self.client.get(
            f"/api/projects/{project_id}/tasks?page=1&page_size=20",
            name="/api/projects/{id}/tasks (list) [designer]"
        )
    
    @task(6)
    def get_task_detail(self):
        """View task detail."""
        if not self.project_ids:
            return
        project_id = random.choice(self.project_ids)
        with self.client.get(
            f"/api/projects/{project_id}/tasks?page=1&page_size=5",
            catch_response=True,
            name="/api/projects/{id}/tasks (fetch for detail) [designer]"
        ) as resp:
            if resp.status_code == 200:
                data = resp.json()
                tasks = data.get("items", [])
                if tasks:
                    task_id = random.choice(tasks)["id"]
                    self.client.get(
                        f"/api/tasks/{task_id}",
                        name="/api/tasks/{id} (detail) [designer]"
                    )
    
    @task(5)
    def create_time_entry(self):
        """Log time entry (periodic write)."""
        if not self.project_ids:
            return
        project_id = random.choice(self.project_ids)
        # Get a task for this project
        with self.client.get(
            f"/api/projects/{project_id}/tasks?page=1&page_size=1",
            catch_response=True,
            name="/api/projects/{id}/tasks (fetch for time entry) [designer]"
        ) as resp:
            if resp.status_code == 200:
                data = resp.json()
                tasks = data.get("items", [])
                if tasks:
                    task_id = tasks[0]["id"]
                    self.client.post(
                        "/api/time-entries",
                        json={
                            "project_id": str(project_id),
                            "task_id": str(task_id),
                            "date": str(date.today()),
                            "hours": round(random.uniform(0.5, 4.0), 2),
                            "description": "Load test time entry",
                            "is_billable": True
                        },
                        name="/api/time-entries (create) [designer]"
                    )
    
    @task(4)
    def list_time_entries(self):
        """List time entries."""
        self.client.get(
            "/api/time-entries?page=1&page_size=20",
            name="/api/time-entries (list) [designer]"
        )
    
    @task(3)
    def list_timesheets(self):
        """List timesheets."""
        self.client.get(
            "/api/timesheets?page=1&page_size=20",
            name="/api/timesheets (list) [designer]"
        )
    
    @task(2)
    def generate_timesheet(self):
        """Generate weekly timesheet."""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        self.client.post(
            f"/api/timesheets/generate?week_start={week_start}",
            name="/api/timesheets/generate [designer]"
        )
    
    @task(1)
    def view_documents(self):
        """View project documents."""
        if not self.project_ids:
            return
        project_id = random.choice(self.project_ids)
        self.client.get(
            f"/api/projects/{project_id}/documents",
            name="/api/projects/{id}/documents (list) [designer]"
        )


class ViewerUser(AuthenticatedUser):
    """Viewer - Read-only access.
    
    Typical Viewer workflow:
    1. Check dashboards
    2. Browse project/client lists
    3. View details (no writes)
    """
    weight = 2  # 20% of users are Viewers
    
    test_email = "pm@swa.local"  # Reuse PM for now
    test_password = "pm123!"
    
    @task(15)
    def check_executive_dashboard(self):
        """Check executive dashboard."""
        self.client.get(
            "/api/dashboard/executive",
            name="/api/dashboard/executive [viewer]"
        )
    
    @task(10)
    def list_projects(self):
        """List projects."""
        page = random.randint(1, 3)
        self.client.get(
            f"/api/projects?page={page}&page_size=20",
            name="/api/projects (list) [viewer]"
        )
    
    @task(8)
    def get_project_detail(self):
        """View project detail."""
        if not self.project_ids:
            return
        project_id = random.choice(self.project_ids)
        self.client.get(
            f"/api/projects/{project_id}",
            name="/api/projects/{id} (detail) [viewer]"
        )
    
    @task(6)
    def list_clients(self):
        """List clients."""
        page = random.randint(1, 2)
        self.client.get(
            f"/api/clients?page={page}&page_size=20",
            name="/api/clients (list) [viewer]"
        )
    
    @task(5)
    def get_client_detail(self):
        """View client detail."""
        if not self.client_ids:
            return
        client_id = random.choice(self.client_ids)
        self.client.get(
            f"/api/clients/{client_id}",
            name="/api/clients/{id} (detail) [viewer]"
        )
    
    @task(4)
    def check_utilization_report(self):
        """Check utilization report."""
        self.client.get(
            "/api/reports/utilization",
            name="/api/reports/utilization [viewer]"
        )
    
    @task(3)
    def check_revenue_report(self):
        """Check revenue report."""
        self.client.get(
            "/api/reports/revenue",
            name="/api/reports/revenue [viewer]"
        )


# Event hooks for test lifecycle
@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """Called when Locust starts."""
    print(f"Locust initialized. Target host: {environment.host}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when a new test starts."""
    print("Load test starting...")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when a test stops."""
    print("Load test stopped.")