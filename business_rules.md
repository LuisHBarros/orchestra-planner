Project Name: Orchestra Planner 
Scope: Core Business Logic & Functional Requirements

1. Domain Glossary & Definitions
1.1 Actors
User: Any registered individual in the system.

Manager: The creator of a specific Project. Holds administrative rights.

Employee: A User invited to a Project who has been assigned a specific Role.

System/LLM: The automated actor responsible for calculations, estimations, and notifications.

1.2 Entities
Project: A collaborative workspace containing Tasks and Members.

Role: A job title defined within a Project (e.g., "Backend Developer", "Designer").

Level: The seniority of an Employee within a Role (Junior, Mid, Senior, Specialist, Lead).

Task: A unit of work with a difficulty score and status.

Workload: A calculated ratio representing how busy an Employee is based on their active tasks and seniority.

2. Business Rules (BR)
BR-AUTH: Authentication & Identity
BR-AUTH-001: Users must authenticate via Magic Link (email-based token). Passwords are not used.

BR-AUTH-002: A Magic Link is valid for one-time use and expires after 15 minutes.

BR-AUTH-003: Email addresses are unique identifiers and are case-insensitive.

BR-PROJ: Project Governance
BR-PROJ-001: The User who creates a Project is automatically assigned as the Manager.

BR-PROJ-002: A Manager cannot be assigned Tasks. Their role is strictly administrative (planning, inviting, unblocking).

BR-PROJ-003: A Project's "Expected End Date" is dynamic. It is calculated based on the critical path of tasks within the project.

BR-PROJ-004: Only the Manager can edit Project settings (name, description, LLM configuration).

BR-ROLE: Roles & Seniority
BR-ROLE-001: Roles are created by the Manager.

BR-ROLE-002: Every Employee must have exactly one Role per Project.

BR-ROLE-003: Every Employee must have a Seniority Level.

BR-ROLE-004: Seniority Levels dictate Capacity Multipliers:

Junior: 0.6x Base Capacity

Mid: 1.0x Base Capacity

Senior: 1.3x Base Capacity

Specialist: 1.2x Base Capacity

Lead: 1.1x Base Capacity

BR-INV: Invitations
BR-INV-001: Only Managers can generate invite links.

BR-INV-002: An invite link is tied to a specific Project and a specific Role.

BR-INV-003: Invite links are public tokens; anyone with the link can attempt to join (unless revoked/expired).

BR-INV-004: An invite has three states: Pending, Accepted, Expired.

BR-INV-005: A User cannot accept an invite if they are already a member of that Project.

BR-TASK: Task Lifecycle
BR-TASK-001: Only the Manager can create, edit, or delete Tasks.

BR-TASK-002: A Task must have a numeric Difficulty (Story Points). This can be set manually or estimated by LLM.

BR-TASK-003: Task Status Transitions are strict:

Todo → Doing (User selects task)

Todo → Blocked (Dependency issue)

Todo → Cancelled (Manager decision)

Doing → Done (Completion)

Doing → Blocked

Doing → Todo (Abandonment)

Blocked → Todo (Unblocked)

BR-TASK-004: A Task cannot be selected (Doing) if its Difficulty is not set.

BR-DEP: Dependencies
BR-DEP-001: Dependencies are strict "Finish-to-Start". Task B cannot start until Task A is Done.

BR-DEP-002: Circular dependencies are strictly prohibited. The system must validate this upon creation.

BR-DEP-003: If a parent task is not Done, the child task status is automatically Blocked.

BR-ASSIGN: Assignment & Selection
BR-ASSIGN-001: Managers cannot assign tasks to Employees.

BR-ASSIGN-002: Employees must Self-Select (pick) tasks from the Todo list.

BR-ASSIGN-003: An Employee cannot select a task if it pushes their Workload Status to "Impossible".

BR-ASSIGN-004: An Employee cannot select a task if they are currently assigned to another task in a Doing state (Single-task focus), UNLESS the system configuration explicitly allows multi-tasking (Default: No).

BR-ASSIGN-005: All assignments and un-assignments are logged in history for auditing.

BR-WORK: Workload Calculation
BR-WORK-001: Workload Score = Sum of Difficulty of all tasks currently in Doing status for that user.

BR-WORK-002: Workload Ratio = Workload Score / (Base Capacity * Level Multiplier).

BR-WORK-003: Workload Status Thresholds:

Idle: Ratio ≤ 0.3

Relaxed: 0.3 < Ratio ≤ 0.7

Healthy: 0.7 < Ratio ≤ 1.2

Tight: 1.2 < Ratio ≤ 1.5

Impossible: Ratio > 1.5

BR-ABANDON: Task Abandonment
BR-ABANDON-001: If an Employee stops a task without finishing it, it is classified as Abandonment.

BR-ABANDON-002: The user must provide a reason for abandonment.

BR-ABANDON-003: The task returns to Todo status immediately.

BR-SCHED: Scheduling & Time
BR-SCHED-001: A task is considered Delayed if Current Date > Expected End Date.

BR-SCHED-002: Schedule propagation flows downstream. If Task A is delayed by 2 days, dependent Task B's start date shifts by 2 days.

BR-SCHED-003: A task's Expected Start Date cannot be earlier than the Max(Actual End Date) of all its dependencies.

BR-SCHED-005: If a task has already started, changing the schedule only affects the End Date, not the Start Date.

BR-SCHED-006: The Project's Expected End Date is the latest End Date of all tasks in the project.

BR-LLM: AI Integration
BR-LLM-001: LLM features are optional and per-project.

BR-LLM-002: API Keys must be stored encrypted.

BR-LLM-003: LLM can be used to:

Estimate Task Difficulty based on description.

Calculate % progress based on textual reports.

BR-NOTIF: Notifications
BR-NOTIF-001: Managers receive a Daily Report summarizing progress and blockers.

BR-NOTIF-002: Alerts are sent to Managers if an Employee's workload becomes Impossible (via manual override or difficulty change).

BR-NOTIF-003: "Toasts" (New Task Alerts) are sent to Employees when a task matching their role is added.

Appendix A: Functional Use Cases (UC)
Group 1: Authentication
UC-001: Register/Login

Actor: Guest

Input: Email, Name (if registration)

Outcome: System sends a Magic Link email.

UC-002: Verify Magic Link

Actor: Guest

Input: Token from email

Outcome: User receives an Access Token (JWT) and is logged in.

Group 2: Project Management
UC-010: Create Project

Actor: User

Input: Project Name, Description

Outcome: Project created. Actor becomes Manager.

UC-011: Configure Project LLM

Actor: Manager

Input: Provider, API Key

Outcome: Project is flagged as AI-enabled.

UC-012: Create Role

Actor: Manager

Input: Role Name (e.g., "Frontend Dev")

Outcome: Role added to project.

UC-013: Get Project Details

Actor: Member

Outcome: Returns dashboard data (tasks, members, status).

Group 3: Invitations
UC-020: Create Project Invite

Actor: Manager

Input: Role ID

Outcome: Returns a unique URL.

UC-021: View Invite

Actor: User

Input: Token

Outcome: Displays Project Name and Role offering.

UC-022: Accept Invite

Actor: User

Input: Token, Self-Assessed Seniority Level

Outcome: User becomes an Employee.

Group 4: Task Management (Manager Only)
UC-030: Create Task

Actor: Manager

Input: Title, Description, Role Required (optional)

Outcome: Task created in Todo.

UC-031: Set Difficulty (Manual)

Actor: Manager

Input: Task ID, Points

Outcome: Task difficulty updated. Workloads recalculated.

UC-032: Calculate Difficulty (LLM)

Actor: Manager

Input: Task ID

Precondition: Project has LLM enabled.

Outcome: System updates Task difficulty based on analysis.

UC-033: Add Dependency

Actor: Manager

Input: Task A (Blocker), Task B (Blocked)

Outcome: Link created. Cycle validation performed.

UC-034: Remove Dependency

Actor: Manager

Outcome: Link removed. Task B might unblock.

UC-035: Cancel Task

Actor: Manager

Outcome: Task moves to Cancelled.

Group 5: Task Execution (Employee Only)
UC-040: Select Task

Actor: Employee

Input: Task ID

Constraint: Cannot select if Workload would become Impossible.

Outcome: Task moves to Doing. Assigned to Actor.

UC-041: Abandon Task

Actor: Employee

Input: Task ID, Reason

Outcome: Task moves to Todo. Assignment removed.

UC-042: Add Task Report

Actor: Employee

Input: Text update (e.g., "Fixed the bug in login")

Outcome: Report saved.

UC-043: Calculate Progress (LLM)

Actor: System (triggered by UC-042)

Outcome: Task % complete updated based on report sentiment/content.

UC-044: Update Progress (Manual)

Actor: Employee

Input: Percentage (0-100)

Outcome: Task progress updated.

UC-045: Complete Task

Actor: Employee

Outcome: Task moves to Done. Downstream dependencies unblocked.

Group 6: Employee Management
UC-050: Remove from Task (Force)

Actor: Manager

Input: Task ID

Outcome: Task returns to Todo. Considered "Fired from Task".

UC-051: Fire Employee

Actor: Manager

Input: Employee ID

Outcome: Employee removed from Project. All their active tasks return to Todo.

UC-052: Resign from Project

Actor: Employee

Outcome: Employee removed. Active tasks return to Todo.

UC-053: List Team

Actor: Member

Outcome: List of members, roles, and current status.

UC-054: Get Employee Workload

Actor: Manager

Outcome: Returns calculation details (Score, Capacity, Status).

Group 7: Schedule & Visibility
UC-060: Detect Delay

Actor: System (Cron/Background)

Outcome: Flags tasks where Actual Date > Expected Date.

UC-061: Propagate Schedule

Actor: System

Outcome: Updates Expected Start/End dates of downstream tasks recursively.

UC-062: Update Project Date

Actor: System

Outcome: Updates Project global deadline based on tasks.

UC-063: View Schedule History

Actor: Manager

Outcome: Audit log of date changes.

UC-064: Manual Date Override

Actor: Manager

Input: Task ID, New Date

Outcome: Task date fixed. Propagation triggers (UC-061).

Group 8: Notifications
UC-080: Send Manager Daily Report

Trigger: Schedule (e.g., 8:00 AM)

Outcome: Email with project health summary.

UC-081: Send Workload Alert

Trigger: Workload Status becomes Impossible.

Outcome: Alert to Manager.

UC-082: Send New Task Toast

Trigger: Task created.

Outcome: In-app notification to relevant Roles.

UC-083: Send Employee Daily Email

Trigger: Schedule.

Outcome: Summary of assigned tasks and deadlines.

UC-084: Send Deadline Warning

Trigger: Task is 24h from deadline and not Done.

Outcome: Email to Assignee.
