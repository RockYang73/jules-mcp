---
name: jules-mcp-assistant
description: Orchestrates cloud-based vibe coding and codebase refactoring via Google Jules MCP Server. Use this skill whenever the user requests complex code changes, bug fixes, or new features to be developed asynchronously using the Jules Sandbox, and when those changes need to be seamlessly applied locally.
license: Apache-2.0
metadata:
  author: gemini-cli-admin
  version: "1.0"
---

# Jules MCP Assistant Skill

This skill defines the standardized workflow for operating the Jules MCP Server. When activated, you act as the orchestrator between the user's local codebase and the Google Jules cloud sandbox.

## When to use this skill
- A user asks to "implement a new feature", "refactor this module", or "fix the bug in the backend" and relies on the Jules agent to do the heavy lifting.
- You need to track a long-running code generation task and eventually sync the diffs back to the local repository.

## The Vibe Coding Workflow

Follow these steps exactly to ensure the context window is preserved and changes are safely applied:

### Step 1: Create the Task
When you receive a coding instruction from the user, you must trigger the remote Jules agent.
Use the `jules_create_task` tool.
- Pass the local absolute path as `repository`.
- Extract the core `instruction` from the user's prompt.
- **Important:** If the user points out specific files, include them in the `context_files` array to give Jules better scope.
- **Save the returned `task_id`.**

### Step 2: Monitor Status
The Jules task runs asynchronously in the cloud sandbox.
Use the `jules_check_status` tool periodically (e.g., every 5-10 seconds) passing the `task_id`.
- If the status is `PENDING` or `IN_PROGRESS`, inform the user that Jules is working and optionally show them the `logs` returned by the tool.
- Wait until the status becomes `PR_READY` or `FAILED`.

### Step 3: Handle Failures (Graceful Degradation)
If `jules_check_status` returns `FAILED`:
- Do NOT proceed to get results or apply patches.
- Read the `error_code` and `suggested_action` returned by the tool.
- Proactively suggest a solution to the user or adjust the instruction and retry creating the task if appropriate.

### Step 4: Retrieve Results with Context Window Protection
Once the status is `PR_READY`:
- Use the `jules_get_result` tool to fetch the changes.
- **Do not ask for the full diff at once if it's massive.** The tool implements pagination via the `page` argument.
- Look at the `file_tree` to understand what files were touched.
- Review the `diff_preview`. If `has_more` is true, you may call the tool again with `page=2` if you specifically need to verify deeper changes, but usually, seeing page 1 is enough to confirm Jules succeeded.

### Step 5: Apply the Patch Locally
The 20% "missing gap" in cloud vibe coding is local synchronization.
- Use the `jules_apply_patch` tool.
- Pass the `task_id` and the local `target_dir` (defaults to current directory).
- This tool automatically extracts the generated `.patch` file and runs `git apply` locally.
- If it returns `PATCH_FAILED`, analyze the `details` (which will contain git merge conflict info) and assist the user in resolving them locally using standard bash tools.

## Best Practices
- **Do not attempt to write massive code blocks yourself** if this skill is activated. Your job is to delegate the heavy lifting to `jules_create_task` and then manage the lifecycle.
- **Provide Updates:** Keep the user engaged. When checking status, stream back Jules' logs so the user knows what the sandbox is currently doing.
- **Verify after Patching:** After `jules_apply_patch` succeeds, you can optionally run a quick local command (like `pytest` or `npm test` if known) using native bash skills to prove the vibe coding worked perfectly!
