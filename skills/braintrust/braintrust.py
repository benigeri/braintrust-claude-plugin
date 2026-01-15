#!/usr/bin/env python3
"""
Braintrust Prompt Management CLI

A simple CLI for managing Braintrust prompts via REST API.
Supports create, update, list, diff, and code generation.

Usage:
    python3 braintrust.py create --slug "my-prompt" --name "My Prompt" --system "..." --user "..."
    python3 braintrust.py update --slug "my-prompt" --system "..." --user "..."
    python3 braintrust.py list [--project "Project Name"]
    python3 braintrust.py get --slug "my-prompt"
    python3 braintrust.py diff --slug "my-prompt" --system "..." --user "..."
    python3 braintrust.py generate --slug "my-prompt"

Environment Variables:
    BRAINTRUST_API_KEY: Required - Your Braintrust API key
    BRAINTRUST_PROJECT_NAME: Optional default project name
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from difflib import unified_diff

# Load .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, rely on environment

API_BASE = "https://api.braintrust.dev/v1"


def get_api_key() -> str:
    """Get API key from environment."""
    key = os.environ.get("BRAINTRUST_API_KEY")
    if not key:
        print("⚠️  BRAINTRUST_API_KEY not set", file=sys.stderr)
        print("", file=sys.stderr)
        print("Add to your .env file:", file=sys.stderr)
        print("  BRAINTRUST_API_KEY=sk-your-api-key", file=sys.stderr)
        print("", file=sys.stderr)
        print("Get your API key from: https://www.braintrust.dev/app/settings/api-keys", file=sys.stderr)
        sys.exit(1)
    return key


def get_default_project() -> Optional[str]:
    """Get default project name from environment."""
    return os.environ.get("BRAINTRUST_PROJECT_NAME")


def api_request(method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
    """Make an API request to Braintrust."""
    url = f"{API_BASE}{endpoint}"
    headers = {
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type": "application/json",
    }

    body = json.dumps(data).encode() if data else None
    req = Request(url, data=body, headers=headers, method=method)

    try:
        with urlopen(req) as response:
            return json.loads(response.read().decode())
    except HTTPError as e:
        error_body = e.read().decode()
        print(f"API Error ({e.code}): {error_body}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"Network Error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def get_project_id(project_name: str) -> str:
    """Get project ID from project name."""
    # List projects and find by name
    result = api_request("GET", "/project")
    projects = result.get("objects", [])

    for project in projects:
        if project.get("name") == project_name:
            return project["id"]

    print(f"Error: Project '{project_name}' not found", file=sys.stderr)
    print("Available projects:", file=sys.stderr)
    for p in projects:
        print(f"  - {p.get('name')}", file=sys.stderr)
    sys.exit(1)


def list_prompts(project_name: Optional[str] = None) -> List[Dict]:
    """List all prompts, optionally filtered by project."""
    result = api_request("GET", "/prompt")
    prompts = result.get("objects", [])

    if project_name:
        project_id = get_project_id(project_name)
        prompts = [p for p in prompts if p.get("project_id") == project_id]

    return prompts


def get_prompt(slug: str, project_name: Optional[str] = None) -> Optional[Dict]:
    """Get a prompt by slug."""
    prompts = list_prompts(project_name)
    for prompt in prompts:
        if prompt.get("slug") == slug:
            return prompt
    return None


def format_prompt_messages(prompt: Dict) -> tuple:
    """Extract system and user messages from prompt data."""
    prompt_data = prompt.get("prompt_data", {})
    messages = prompt_data.get("prompt", {}).get("messages", [])

    system_msg = ""
    user_msg = ""

    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role == "system":
            system_msg = content
        elif role == "user":
            user_msg = content

    return system_msg, user_msg


def cmd_list(args: argparse.Namespace) -> None:
    """List all prompts."""
    project = args.project or get_default_project()
    prompts = list_prompts(project)

    if not prompts:
        print("No prompts found.")
        return

    print(f"Found {len(prompts)} prompt(s):\n")
    for prompt in prompts:
        slug = prompt.get("slug", "N/A")
        name = prompt.get("name", "N/A")
        desc = (prompt.get("description") or "")[:50]
        print(f"  {slug}")
        print(f"    Name: {name}")
        if desc:
            print(f"    Desc: {desc}...")
        print()


def cmd_get(args: argparse.Namespace) -> None:
    """Get details of a specific prompt."""
    project = args.project or get_default_project()
    prompt = get_prompt(args.slug, project)

    if not prompt:
        print(f"Error: Prompt '{args.slug}' not found", file=sys.stderr)
        sys.exit(1)

    system_msg, user_msg = format_prompt_messages(prompt)

    print(f"Slug: {prompt.get('slug')}")
    print(f"Name: {prompt.get('name')}")
    print(f"Description: {prompt.get('description', 'N/A')}")
    print(f"Model: {prompt.get('prompt_data', {}).get('options', {}).get('model', 'N/A')}")
    print()
    print("=== System Message ===")
    print(system_msg)
    print()
    print("=== User Message ===")
    print(user_msg)


def cmd_create(args: argparse.Namespace) -> None:
    """Create a new prompt."""
    project = args.project or get_default_project()
    if not project:
        print("Error: Project name required (--project or BRAINTRUST_PROJECT_NAME)", file=sys.stderr)
        sys.exit(1)

    project_id = get_project_id(project)

    # Check if prompt already exists
    existing = get_prompt(args.slug, project)
    if existing:
        print(f"Error: Prompt '{args.slug}' already exists. Use 'update' instead.", file=sys.stderr)
        sys.exit(1)

    # Build prompt data
    messages = []
    if args.system:
        messages.append({"role": "system", "content": args.system})
    if args.user:
        messages.append({"role": "user", "content": args.user})

    data = {
        "name": args.name or args.slug,
        "slug": args.slug,
        "description": args.description or "",
        "project_id": project_id,
        "prompt_data": {
            "prompt": {
                "type": "chat",
                "messages": messages,
            },
            "options": {
                "model": args.model or "claude-sonnet-4-5-20250929",
            },
        },
    }

    result = api_request("POST", "/prompt", data)
    print(f"Created prompt: {result.get('slug')}")
    print(f"ID: {result.get('id')}")


def cmd_update(args: argparse.Namespace) -> None:
    """Update an existing prompt."""
    project = args.project or get_default_project()
    prompt = get_prompt(args.slug, project)

    if not prompt:
        print(f"Error: Prompt '{args.slug}' not found", file=sys.stderr)
        sys.exit(1)

    prompt_id = prompt["id"]

    # Build update data
    update_data: Dict[str, Any] = {}

    if args.name:
        update_data["name"] = args.name
    if args.description:
        update_data["description"] = args.description

    # Update messages if provided
    if args.system or args.user:
        current_prompt_data = prompt.get("prompt_data", {})
        current_messages = current_prompt_data.get("prompt", {}).get("messages", [])

        new_messages = []
        for msg in current_messages:
            role = msg.get("role", "")
            if role == "system" and args.system:
                new_messages.append({"role": "system", "content": args.system})
            elif role == "user" and args.user:
                new_messages.append({"role": "user", "content": args.user})
            else:
                new_messages.append(msg)

        # Add new messages if they didn't exist before
        roles_present = {m.get("role") for m in new_messages}
        if args.system and "system" not in roles_present:
            new_messages.insert(0, {"role": "system", "content": args.system})
        if args.user and "user" not in roles_present:
            new_messages.append({"role": "user", "content": args.user})

        update_data["prompt_data"] = {
            **current_prompt_data,
            "prompt": {
                **current_prompt_data.get("prompt", {}),
                "messages": new_messages,
            },
        }

        if args.model:
            update_data["prompt_data"]["options"] = {
                **current_prompt_data.get("options", {}),
                "model": args.model,
            }

    if not update_data:
        print("No updates specified.")
        return

    result = api_request("PATCH", f"/prompt/{prompt_id}", update_data)
    print(f"Updated prompt: {result.get('slug')}")


def cmd_diff(args: argparse.Namespace) -> None:
    """Show diff between current prompt and proposed changes."""
    project = args.project or get_default_project()
    prompt = get_prompt(args.slug, project)

    if not prompt:
        print(f"Error: Prompt '{args.slug}' not found", file=sys.stderr)
        sys.exit(1)

    current_system, current_user = format_prompt_messages(prompt)

    # Compare system message
    if args.system:
        print("=== System Message Diff ===")
        diff = unified_diff(
            current_system.splitlines(keepends=True),
            args.system.splitlines(keepends=True),
            fromfile="current",
            tofile="proposed",
        )
        diff_text = "".join(diff)
        if diff_text:
            print(diff_text)
        else:
            print("(no changes)")
        print()

    # Compare user message
    if args.user:
        print("=== User Message Diff ===")
        diff = unified_diff(
            current_user.splitlines(keepends=True),
            args.user.splitlines(keepends=True),
            fromfile="current",
            tofile="proposed",
        )
        diff_text = "".join(diff)
        if diff_text:
            print(diff_text)
        else:
            print("(no changes)")
        print()

    if not args.system and not args.user:
        print("Specify --system or --user to compare")


def cmd_delete(args: argparse.Namespace) -> None:
    """Delete a prompt by slug."""
    project = args.project or get_default_project()
    prompt = get_prompt(args.slug, project)

    if not prompt:
        print(f"Error: Prompt '{args.slug}' not found", file=sys.stderr)
        sys.exit(1)

    prompt_id = prompt["id"]
    slug = prompt.get("slug")

    if not args.force:
        confirm = input(f"Delete prompt '{slug}'? [y/N]: ")
        if confirm.lower() != 'y':
            print("Cancelled.")
            return

    result = api_request("DELETE", f"/prompt/{prompt_id}")
    print(f"Deleted prompt: {slug}")


def cmd_generate(args: argparse.Namespace) -> None:
    """Generate TypeScript usage code for a prompt."""
    project = args.project or get_default_project()
    prompt = get_prompt(args.slug, project)

    if not prompt:
        print(f"Error: Prompt '{args.slug}' not found", file=sys.stderr)
        sys.exit(1)

    slug = prompt.get("slug")
    name = prompt.get("name", slug)

    # Extract template variables from user message
    _, user_msg = format_prompt_messages(prompt)
    variables = extract_template_variables(user_msg)

    # Generate function name from slug
    func_name = slug.replace("-", "_").replace(" ", "_")
    func_name = "".join(word.capitalize() for word in func_name.split("_"))
    func_name = func_name[0].lower() + func_name[1:] if func_name else "invokePrompt"

    # Generate input type
    input_fields = ", ".join(f"{v}: string" for v in variables) if variables else "input: string"
    input_obj = ", ".join(f"{v}: input.{v}" for v in variables) if variables else "input: input.input"

    code = f'''// Generated by braintrust.py for prompt: {name}
import {{ invoke, wrapTraced, initLogger }} from 'braintrust';

// Initialize logger for tracing (call once at app startup)
const logger = initLogger({{
  projectName: process.env.BRAINTRUST_PROJECT_NAME!,
  apiKey: process.env.BRAINTRUST_API_KEY,
  asyncFlush: false, // CRITICAL for serverless (Vercel)
}});

// Input type based on prompt template variables
interface {func_name.capitalize()}Input {{
  {"; ".join(f"{v}: string" for v in variables) if variables else "input: string"};
}}

// Wrapped function with tracing
export const {func_name} = wrapTraced(async function {func_name}(
  input: {func_name.capitalize()}Input
) {{
  const projectName = process.env.BRAINTRUST_PROJECT_NAME;
  const slug = '{slug}';

  if (!projectName) {{
    throw new Error('Missing BRAINTRUST_PROJECT_NAME');
  }}

  const startTime = Date.now();

  const result = await invoke({{
    projectName,
    slug,
    input: {{ {input_obj} }},
  }});

  const duration = Date.now() - startTime;
  console.log(`{func_name} completed in ${{duration}}ms`);

  return result;
}});

// Example usage:
// const result = await {func_name}({{ {", ".join(f'{v}: "..."' for v in variables) if variables else 'input: "..."'} }});
'''

    print(code)


def extract_template_variables(template: str) -> List[str]:
    """Extract Handlebars-style template variables from text."""
    import re
    # Match {{variable}} but not {{#each}} or {{/each}}
    pattern = r'\{\{(?!#|/)([a-zA-Z_][a-zA-Z0-9_]*)\}\}'
    matches = re.findall(pattern, template)
    # Remove duplicates while preserving order
    seen = set()
    return [v for v in matches if not (v in seen or seen.add(v))]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Braintrust Prompt Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all prompts
  %(prog)s list

  # Get prompt details
  %(prog)s get --slug "email-draft"

  # Create a new prompt
  %(prog)s create --slug "my-prompt" --name "My Prompt" \\
    --system "You are helpful." --user "Question: {{question}}"

  # Diff before updating
  %(prog)s diff --slug "my-prompt" --system "Updated system message"

  # Update a prompt
  %(prog)s update --slug "my-prompt" --system "Updated system message"

  # Generate TypeScript code
  %(prog)s generate --slug "my-prompt"

Environment Variables:
  BRAINTRUST_API_KEY       Required - Your Braintrust API key
  BRAINTRUST_PROJECT_NAME  Optional - Default project name
""",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # list command
    list_parser = subparsers.add_parser("list", help="List all prompts")
    list_parser.add_argument("--project", help="Filter by project name")

    # get command
    get_parser = subparsers.add_parser("get", help="Get prompt details")
    get_parser.add_argument("--slug", required=True, help="Prompt slug")
    get_parser.add_argument("--project", help="Project name")

    # create command
    create_parser = subparsers.add_parser("create", help="Create a new prompt")
    create_parser.add_argument("--slug", required=True, help="Prompt slug (URL-safe identifier)")
    create_parser.add_argument("--name", help="Human-readable name")
    create_parser.add_argument("--description", help="Prompt description")
    create_parser.add_argument("--system", help="System message content")
    create_parser.add_argument("--user", help="User message template")
    create_parser.add_argument("--model", help="Model name (default: claude-sonnet-4-5-20250929)")
    create_parser.add_argument("--project", help="Project name")

    # update command
    update_parser = subparsers.add_parser("update", help="Update an existing prompt")
    update_parser.add_argument("--slug", required=True, help="Prompt slug")
    update_parser.add_argument("--name", help="New name")
    update_parser.add_argument("--description", help="New description")
    update_parser.add_argument("--system", help="New system message")
    update_parser.add_argument("--user", help="New user message template")
    update_parser.add_argument("--model", help="New model name")
    update_parser.add_argument("--project", help="Project name")

    # diff command
    diff_parser = subparsers.add_parser("diff", help="Show diff between current and proposed")
    diff_parser.add_argument("--slug", required=True, help="Prompt slug")
    diff_parser.add_argument("--system", help="Proposed system message")
    diff_parser.add_argument("--user", help="Proposed user message")
    diff_parser.add_argument("--project", help="Project name")

    # generate command
    gen_parser = subparsers.add_parser("generate", help="Generate TypeScript usage code")
    gen_parser.add_argument("--slug", required=True, help="Prompt slug")
    gen_parser.add_argument("--project", help="Project name")

    # delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a prompt")
    delete_parser.add_argument("--slug", required=True, help="Prompt slug to delete")
    delete_parser.add_argument("--force", "-f", action="store_true", help="Skip confirmation")
    delete_parser.add_argument("--project", help="Project name")

    args = parser.parse_args()

    commands = {
        "list": cmd_list,
        "get": cmd_get,
        "create": cmd_create,
        "update": cmd_update,
        "diff": cmd_diff,
        "generate": cmd_generate,
        "delete": cmd_delete,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
