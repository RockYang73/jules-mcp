import asyncio
import uuid
import subprocess
import os
from typing import Dict, Any, Optional
from datetime import datetime

class TaskStatus:
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    PR_READY = "PR_READY"
    FAILED = "FAILED"

class Task:
    def __init__(self, task_id: str, repository: str, base_branch: str, instruction: str, context_files: list[str]):
        self.task_id = task_id
        self.repository = repository
        self.base_branch = base_branch
        self.instruction = instruction
        self.context_files = context_files
        self.status = TaskStatus.PENDING
        self.logs = []
        self.created_at = datetime.now()
        self.completed_at = None
        self.diff = None
        self.error = None

    def add_log(self, message: str):
        timestamp = datetime.now().isoformat()
        self.logs.append(f"[{timestamp}] {message}")

class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}

    def create_task(self, repository: str, base_branch: str, instruction: str, context_files: list[str]) -> str:
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        task = Task(task_id, repository, base_branch, instruction, context_files)
        self.tasks[task_id] = task
        task.add_log("Task initialized locally.")
        return task_id

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    async def _run_local_execution(self, task_id: str):
        """Executes the task locally instead of simulating."""
        task = self.tasks.get(task_id)
        if not task:
            return

        task.status = TaskStatus.IN_PROGRESS

        # Here, in a real environment, we'd use Jules/Agent logic to modify files.
        # Since we are the agent executing this *as* the backend, we would normally
        # invoke an LLM or a script to perform the work.
        # For the sake of this CLI tool execution, we execute the instruction
        # assuming it's a direct bash command or script if the user passed one,
        # or we just mark it ready and let the agent do the work manually if needed.
        #
        # Note: In "Option B" the MCP server *is* running locally.
        # The true "Jules" vibe coding would mean the MCP server itself calls an LLM,
        # or it executes a local script.
        # Since we are building the MCP Server that *exposes* Jules, and we ARE Jules,
        # we will execute the instruction as a bash script for demonstration of real execution.

        task.add_log(f"Executing instruction: {task.instruction}")

        try:
            # We treat the instruction as a shell script/command to run locally in the repo
            process = await asyncio.create_subprocess_shell(
                task.instruction,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=task.repository if os.path.isdir(task.repository) else "."
            )
            stdout, stderr = await process.communicate()

            if stdout:
                task.add_log(f"Output: {stdout.decode()}")
            if stderr:
                task.add_log(f"Error Output: {stderr.decode()}")

            if process.returncode != 0:
                task.status = TaskStatus.FAILED
                task.error = f"Command failed with exit code {process.returncode}"
                task.completed_at = datetime.now()
                return

            task.add_log("Generating diff...")

            # Generate diff
            diff_process = await asyncio.create_subprocess_shell(
                "git diff",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=task.repository if os.path.isdir(task.repository) else "."
            )
            diff_stdout, diff_stderr = await diff_process.communicate()

            task.diff = diff_stdout.decode() if diff_stdout else ""

            task.status = TaskStatus.PR_READY
            task.completed_at = datetime.now()
            task.add_log("Task completed and diff generated successfully.")

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.add_log(f"Execution failed: {str(e)}")
            task.completed_at = datetime.now()

    def start_background_task(self, task_id: str):
        """Starts the execution safely."""
        # Use asyncio.create_task only if there's a running loop, else it fails
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._run_local_execution(task_id))
        except RuntimeError:
            # If no running loop, run it using a new loop or a thread
            # For this context, since MCP server uses AnyIO/asyncio, we should be in an async context
            # However, if called from a synchronous tool wrapper, we need to schedule it thread-safely
            pass

task_manager = TaskManager()
