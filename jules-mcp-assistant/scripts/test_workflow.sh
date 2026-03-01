#!/bin/bash
# test_workflow.sh
#
# This is a sample reference script for an agent to understand how the tools
# correlate in an actual sequence, mimicking the JSON-RPC tool calls.

echo "1. Client calls jules_create_task(repository='.', base_branch='main', instruction='Fix the memory leak in auth module')"
# Assume returned task_id is: task_123abc

echo "2. Client polls jules_check_status('task_123abc')"
# Returns: {"status": "IN_PROGRESS", "logs": ["[Timestamp] Executing LLM instruction over codebase..."]}

echo "3. Client polls jules_check_status('task_123abc') again after waiting"
# Returns: {"status": "PR_READY", "logs": [...]}

echo "4. Client calls jules_get_result('task_123abc', page=1)"
# Returns: {"file_tree": [...], "diff_preview": "...", "has_more": false}

echo "5. Client calls jules_apply_patch('task_123abc', target_dir='.')"
# Returns: {"status": "APPLIED", "message": "Successfully applied cloud changes..."}

echo "Workflow complete! The local codebase is now synced with the Cloud Sandbox."
