#!/usr/bin/env python3
"""
Braintrust Prompt Management CLI

A CLI for managing Braintrust prompts via REST API and SDK.
Supports create, update, list, diff, invoke, test (A/B), and code generation.

Usage:
    python3 bt_cli.py list [--project "Project Name"]
    python3 bt_cli.py get --slug "my-prompt"
    python3 bt_cli.py invoke --slug "my-prompt" --input '{"key": "value"}'
    python3 bt_cli.py test --slug "my-prompt" --input '{"key": "value"}' [--system "new prompt"]
    python3 bt_cli.py create --slug "my-prompt" --system "..." --user "..."
    python3 bt_cli.py diff --slug "my-prompt" --system "..."
    python3 bt_cli.py update --slug "my-prompt" --system "..."
    python3 bt_cli.py promote --from "slug-v2" --to "slug"
    python3 bt_cli.py generate --slug "my-prompt"
    python3 bt_cli.py delete --slug "my-prompt"

Environment Variables:
    BRAINTRUST_API_KEY: Required - Your Braintrust API key
    BRAINTRUST_PROJECT_NAME: Optional default project name
"""

import argparse
import json
import os
import sys
import time
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


# ============================================================
# CORE UTILITIES
# ============================================================

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


def parse_input(args: argparse.Namespace) -> Dict:
    """Parse input from --input or --input-file."""
    if hasattr(args, 'input_file') and args.input_file:
        with open(args.input_file) as f:
            return json.load(f)
    elif hasattr(args, 'input') and args.input:
        try:
            return json.loads(args.input)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
            sys.exit(1)
    return {}


def extract_template_variables(template: str) -> List[str]:
    """Extract Handlebars-style template variables from text."""
    import re
    pattern = r'\{\{(?!#|/)([a-zA-Z_][a-zA-Z0-9_]*)\}\}'
    matches = re.findall(pattern, template)
    seen = set()
    return [v for v in matches if not (v in seen or seen.add(v))]


# ============================================================
# INVOKE HELPERS
# ============================================================

def invoke_prompt(project: str, slug: str, input_data: Dict, verbose: bool = False) -> Dict:
    """Invoke a prompt and return result."""
    try:
        return invoke_with_sdk(project, slug, input_data, verbose)
    except ImportError:
        print("⚠️  Braintrust SDK not installed. Install with: pip install braintrust", file=sys.stderr)
        print("SDK is required for invoke/test commands (provides tracing).", file=sys.stderr)
        sys.exit(1)


def invoke_with_sdk(project_name: str, slug: str, input_data: Dict, verbose: bool = False) -> Dict:
    """Invoke using Braintrust SDK (has tracing)."""
    from braintrust import invoke, init_logger

    # Initialize logger for tracing
    init_logger(
        project_name=project_name,
        api_key=get_api_key(),
    )

    if verbose:
        print(f"Invoking '{slug}' in project '{project_name}'...")
        print(f"Input: {json.dumps(input_data, indent=2)}\n")

    start_time = time.time()
    raw_result = invoke(
        project_name=project_name,
        slug=slug,
        input=input_data,
    )
    duration_ms = int((time.time() - start_time) * 1000)

    output = extract_output(raw_result)

    return {
        "output": output,
        "duration_ms": duration_ms,
        "raw": raw_result,
    }


def extract_output(raw_result: Any) -> Any:
    """Extract output from various Braintrust response formats."""
    if isinstance(raw_result, str):
        return raw_result.strip()

    if isinstance(raw_result, list) and raw_result:
        first = raw_result[0]
        if isinstance(first, dict):
            # OpenAI format
            if first.get("message", {}).get("content"):
                return first["message"]["content"].strip()
            # Anthropic format
            if isinstance(first.get("content"), list):
                for block in first["content"]:
                    if block.get("type") == "text":
                        return block.get("text", "").strip()
            if isinstance(first.get("content"), str):
                return first["content"].strip()

    if isinstance(raw_result, dict):
        for key in ["content", "text", "output"]:
            if isinstance(raw_result.get(key), str):
                return raw_result[key].strip()
        if isinstance(raw_result.get("content"), list):
            for block in raw_result["content"]:
                if block.get("type") == "text":
                    return block.get("text", "").strip()

    return raw_result


def display_result(result: Dict) -> None:
    """Display full result with metadata."""
    print("=== Output ===")
    display_output(result)
    print("\n=== Metadata ===")
    if result.get("duration_ms"):
        print(f"Duration: {result['duration_ms']}ms")


def display_output(result: Dict) -> None:
    """Display just the output."""
    output = result.get("output")
    if isinstance(output, str):
        print(output)
    else:
        print(json.dumps(output, indent=2))


# ============================================================
# A/B TEST HELPERS
# ============================================================

def create_v2_prompt(project: str, original_slug: str, v2_slug: str, args: argparse.Namespace) -> None:
    """Create a v2 copy of a prompt with proposed changes."""
    original = get_prompt(original_slug, project)
    if not original:
        raise ValueError(f"Original prompt '{original_slug}' not found")

    project_id = get_project_id(project)
    current_system, current_user = format_prompt_messages(original)

    new_system = args.system if args.system else current_system
    new_user = args.user if args.user else current_user

    messages = []
    if new_system:
        messages.append({"role": "system", "content": new_system})
    if new_user:
        messages.append({"role": "user", "content": new_user})

    data = {
        "name": f"{original.get('name', original_slug)} (v2)",
        "slug": v2_slug,
        "description": f"Test version of {original_slug}",
        "project_id": project_id,
        "prompt_data": {
            "prompt": {
                "type": "chat",
                "messages": messages,
            },
            "options": original.get("prompt_data", {}).get("options", {}),
        },
    }

    api_request("POST", "/prompt", data)


def promote_v2(project: str, original_slug: str, v2_slug: str) -> None:
    """Copy v2 content to original prompt."""
    v2 = get_prompt(v2_slug, project)
    if not v2:
        raise ValueError(f"V2 prompt '{v2_slug}' not found")

    original = get_prompt(original_slug, project)
    if not original:
        raise ValueError(f"Original prompt '{original_slug}' not found")

    v2_system, v2_user = format_prompt_messages(v2)

    messages = []
    if v2_system:
        messages.append({"role": "system", "content": v2_system})
    if v2_user:
        messages.append({"role": "user", "content": v2_user})

    update_data = {
        "prompt_data": {
            **original.get("prompt_data", {}),
            "prompt": {
                **original.get("prompt_data", {}).get("prompt", {}),
                "messages": messages,
            },
        },
    }

    api_request("PATCH", f"/prompt/{original['id']}", update_data)


def delete_prompt_by_slug(project: str, slug: str) -> None:
    """Delete a prompt by slug."""
    prompt = get_prompt(slug, project)
    if prompt:
        api_request("DELETE", f"/prompt/{prompt['id']}")


def run_ab_test(project: str, slug: str, input_data: Dict, args: argparse.Namespace) -> None:
    """Run A/B test comparing original prompt with proposed changes."""
    v2_slug = f"{slug}-v2"

    print(f"🔬 A/B Test: {slug} vs {v2_slug}")
    print("=" * 50)

    existing_v2 = get_prompt(v2_slug, project)
    if existing_v2:
        print(f"\nNote: {v2_slug} already exists. Using existing version.")
        print("Delete it first if you want to test new changes.\n")
    else:
        print(f"\n📝 Creating {v2_slug} with proposed changes...")
        create_v2_prompt(project, slug, v2_slug, args)
        print(f"✓ Created {v2_slug}\n")

    print("Running both prompts with same input...")
    print("-" * 50)

    print(f"\n🅰️  ORIGINAL ({slug}):")
    print("-" * 30)
    result_a = invoke_prompt(project, slug, input_data, verbose=False)
    display_output(result_a)

    print(f"\n🅱️  V2 ({v2_slug}):")
    print("-" * 30)
    result_b = invoke_prompt(project, v2_slug, input_data, verbose=False)
    display_output(result_b)

    print("\n" + "=" * 50)
    print("📊 Comparison:")
    print(f"  Original: {result_a.get('duration_ms', 'N/A')}ms")
    print(f"  V2:       {result_b.get('duration_ms', 'N/A')}ms")

    print("\n" + "-" * 50)
    promote = input(f"Promote {v2_slug} → {slug}? [y/N]: ").strip().lower()

    if promote == 'y':
        promote_v2(project, slug, v2_slug)
        print(f"\n✓ Promoted {v2_slug} to {slug}")

        cleanup = input(f"Delete {v2_slug}? [Y/n]: ").strip().lower()
        if cleanup != 'n':
            delete_prompt_by_slug(project, v2_slug)
            print(f"✓ Deleted {v2_slug}")
    else:
        print(f"\nKept both versions. {v2_slug} available for further testing.")
        print(f"To promote later: python3 bt_cli.py promote --from {v2_slug} --to {slug}")
        print(f"To delete v2:     python3 bt_cli.py delete --slug {v2_slug}")


# ============================================================
# COMMANDS
# ============================================================

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


def cmd_invoke(args: argparse.Namespace) -> None:
    """Invoke a prompt and display the result with tracing."""
    project = args.project or get_default_project()
    if not project:
        print("Error: Project name required (--project or BRAINTRUST_PROJECT_NAME)", file=sys.stderr)
        sys.exit(1)

    prompt = get_prompt(args.slug, project)
    if not prompt:
        print(f"Error: Prompt '{args.slug}' not found", file=sys.stderr)
        sys.exit(1)

    input_data = parse_input(args)
    result = invoke_prompt(project, args.slug, input_data, verbose=args.verbose)
    display_result(result)


def cmd_test(args: argparse.Namespace) -> None:
    """Test a prompt - simple run or A/B comparison with changes."""
    project = args.project or get_default_project()
    if not project:
        print("Error: Project name required (--project or BRAINTRUST_PROJECT_NAME)", file=sys.stderr)
        sys.exit(1)

    prompt = get_prompt(args.slug, project)
    if not prompt:
        print(f"Error: Prompt '{args.slug}' not found", file=sys.stderr)
        sys.exit(1)

    input_data = parse_input(args)

    if args.system or args.user:
        run_ab_test(project, args.slug, input_data, args)
    else:
        print(f"Testing prompt: {args.slug}\n")
        result = invoke_prompt(project, args.slug, input_data, verbose=args.verbose)
        display_result(result)


def cmd_promote(args: argparse.Namespace) -> None:
    """Promote changes from one prompt to another."""
    project = args.project or get_default_project()
    if not project:
        print("Error: Project name required", file=sys.stderr)
        sys.exit(1)

    from_slug = args.from_slug
    to_slug = args.to_slug

    print(f"Promoting {from_slug} → {to_slug}")

    from_prompt = get_prompt(from_slug, project)
    to_prompt = get_prompt(to_slug, project)

    if not from_prompt:
        print(f"Error: Source prompt '{from_slug}' not found", file=sys.stderr)
        sys.exit(1)
    if not to_prompt:
        print(f"Error: Target prompt '{to_slug}' not found", file=sys.stderr)
        sys.exit(1)

    from_system, from_user = format_prompt_messages(from_prompt)
    to_system, to_user = format_prompt_messages(to_prompt)

    print("\n=== System Message Diff ===")
    diff = unified_diff(
        to_system.splitlines(keepends=True),
        from_system.splitlines(keepends=True),
        fromfile="current",
        tofile="proposed",
    )
    diff_text = "".join(diff)
    print(diff_text if diff_text else "(no changes)")

    print("\n=== User Message Diff ===")
    diff = unified_diff(
        to_user.splitlines(keepends=True),
        from_user.splitlines(keepends=True),
        fromfile="current",
        tofile="proposed",
    )
    diff_text = "".join(diff)
    print(diff_text if diff_text else "(no changes)")

    if not args.force:
        confirm = input(f"\nApply these changes to {to_slug}? [y/N]: ").strip().lower()
        if confirm != 'y':
            print("Cancelled.")
            return

    promote_v2(project, to_slug, from_slug)
    print(f"\n✓ Promoted {from_slug} → {to_slug}")

    if not args.keep:
        cleanup = input(f"Delete {from_slug}? [Y/n]: ").strip().lower()
        if cleanup != 'n':
            delete_prompt_by_slug(project, from_slug)
            print(f"✓ Deleted {from_slug}")


def cmd_create(args: argparse.Namespace) -> None:
    """Create a new prompt."""
    project = args.project or get_default_project()
    if not project:
        print("Error: Project name required (--project or BRAINTRUST_PROJECT_NAME)", file=sys.stderr)
        sys.exit(1)

    project_id = get_project_id(project)

    existing = get_prompt(args.slug, project)
    if existing:
        print(f"Error: Prompt '{args.slug}' already exists. Use 'update' instead.", file=sys.stderr)
        sys.exit(1)

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
    print(f"✓ Created prompt: {result.get('slug')}")
    print(f"  ID: {result.get('id')}")


def cmd_update(args: argparse.Namespace) -> None:
    """Update an existing prompt."""
    project = args.project or get_default_project()
    prompt = get_prompt(args.slug, project)

    if not prompt:
        print(f"Error: Prompt '{args.slug}' not found", file=sys.stderr)
        sys.exit(1)

    prompt_id = prompt["id"]
    update_data: Dict[str, Any] = {}

    if args.name:
        update_data["name"] = args.name
    if args.description:
        update_data["description"] = args.description

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
    print(f"✓ Updated prompt: {result.get('slug')}")


def cmd_diff(args: argparse.Namespace) -> None:
    """Show diff between current prompt and proposed changes."""
    project = args.project or get_default_project()
    prompt = get_prompt(args.slug, project)

    if not prompt:
        print(f"Error: Prompt '{args.slug}' not found", file=sys.stderr)
        sys.exit(1)

    current_system, current_user = format_prompt_messages(prompt)

    if args.system:
        print("=== System Message Diff ===")
        diff = unified_diff(
            current_system.splitlines(keepends=True),
            args.system.splitlines(keepends=True),
            fromfile="current",
            tofile="proposed",
        )
        diff_text = "".join(diff)
        print(diff_text if diff_text else "(no changes)")
        print()

    if args.user:
        print("=== User Message Diff ===")
        diff = unified_diff(
            current_user.splitlines(keepends=True),
            args.user.splitlines(keepends=True),
            fromfile="current",
            tofile="proposed",
        )
        diff_text = "".join(diff)
        print(diff_text if diff_text else "(no changes)")
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

    api_request("DELETE", f"/prompt/{prompt_id}")
    print(f"✓ Deleted prompt: {slug}")


def cmd_generate(args: argparse.Namespace) -> None:
    """Generate TypeScript usage code for a prompt."""
    project = args.project or get_default_project()
    prompt = get_prompt(args.slug, project)

    if not prompt:
        print(f"Error: Prompt '{args.slug}' not found", file=sys.stderr)
        sys.exit(1)

    slug = prompt.get("slug")
    name = prompt.get("name", slug)

    _, user_msg = format_prompt_messages(prompt)
    variables = extract_template_variables(user_msg)

    func_name = slug.replace("-", "_").replace(" ", "_")
    func_name = "".join(word.capitalize() for word in func_name.split("_"))
    func_name = func_name[0].lower() + func_name[1:] if func_name else "invokePrompt"

    input_obj = ", ".join(f"{v}: input.{v}" for v in variables) if variables else "input: input.input"

    code = f'''// Generated by bt_cli.py for prompt: {name}
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


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Braintrust Prompt Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List prompts
  %(prog)s list

  # View prompt
  %(prog)s get --slug "my-prompt"

  # Invoke prompt (run it)
  %(prog)s invoke --slug "my-prompt" --input '{"question": "test"}'

  # A/B test with changes
  %(prog)s test --slug "my-prompt" --input '{"q": "test"}' --system "New instructions"

  # Diff and update
  %(prog)s diff --slug "my-prompt" --system "New content"
  %(prog)s update --slug "my-prompt" --system "New content"

  # Generate TypeScript
  %(prog)s generate --slug "my-prompt"

Environment Variables:
  BRAINTRUST_API_KEY       Required - Your Braintrust API key
  BRAINTRUST_PROJECT_NAME  Optional - Default project name
""",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    list_parser = subparsers.add_parser("list", help="List all prompts")
    list_parser.add_argument("--project", help="Filter by project name")

    # get
    get_parser = subparsers.add_parser("get", help="Get prompt details")
    get_parser.add_argument("--slug", required=True, help="Prompt slug")
    get_parser.add_argument("--project", help="Project name")

    # invoke
    invoke_parser = subparsers.add_parser("invoke", help="Invoke a prompt and see the result")
    invoke_parser.add_argument("--slug", required=True, help="Prompt slug")
    invoke_parser.add_argument("--input", "-i", help="JSON input (e.g., '{\"key\": \"value\"}')")
    invoke_parser.add_argument("--input-file", "-f", help="Read input from JSON file")
    invoke_parser.add_argument("--project", help="Project name")
    invoke_parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")

    # test
    test_parser = subparsers.add_parser("test", help="Test a prompt (simple or A/B comparison)")
    test_parser.add_argument("--slug", required=True, help="Prompt slug to test")
    test_parser.add_argument("--input", "-i", help="JSON input for testing")
    test_parser.add_argument("--input-file", "-f", help="Read input from JSON file")
    test_parser.add_argument("--system", help="Proposed system message (triggers A/B test)")
    test_parser.add_argument("--user", help="Proposed user message (triggers A/B test)")
    test_parser.add_argument("--project", help="Project name")
    test_parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")

    # promote
    promote_parser = subparsers.add_parser("promote", help="Promote changes from one prompt to another")
    promote_parser.add_argument("--from", dest="from_slug", required=True, help="Source prompt slug")
    promote_parser.add_argument("--to", dest="to_slug", required=True, help="Target prompt slug")
    promote_parser.add_argument("--project", help="Project name")
    promote_parser.add_argument("--force", "-f", action="store_true", help="Skip confirmation")
    promote_parser.add_argument("--keep", action="store_true", help="Keep source prompt after promotion")

    # create
    create_parser = subparsers.add_parser("create", help="Create a new prompt")
    create_parser.add_argument("--slug", required=True, help="Prompt slug (URL-safe identifier)")
    create_parser.add_argument("--name", help="Human-readable name")
    create_parser.add_argument("--description", help="Prompt description")
    create_parser.add_argument("--system", help="System message content")
    create_parser.add_argument("--user", help="User message template")
    create_parser.add_argument("--model", help="Model name (default: claude-sonnet-4-5-20250929)")
    create_parser.add_argument("--project", help="Project name")

    # update
    update_parser = subparsers.add_parser("update", help="Update an existing prompt")
    update_parser.add_argument("--slug", required=True, help="Prompt slug")
    update_parser.add_argument("--name", help="New name")
    update_parser.add_argument("--description", help="New description")
    update_parser.add_argument("--system", help="New system message")
    update_parser.add_argument("--user", help="New user message template")
    update_parser.add_argument("--model", help="New model name")
    update_parser.add_argument("--project", help="Project name")

    # diff
    diff_parser = subparsers.add_parser("diff", help="Show diff between current and proposed")
    diff_parser.add_argument("--slug", required=True, help="Prompt slug")
    diff_parser.add_argument("--system", help="Proposed system message")
    diff_parser.add_argument("--user", help="Proposed user message")
    diff_parser.add_argument("--project", help="Project name")

    # generate
    gen_parser = subparsers.add_parser("generate", help="Generate TypeScript usage code")
    gen_parser.add_argument("--slug", required=True, help="Prompt slug")
    gen_parser.add_argument("--project", help="Project name")

    # delete
    delete_parser = subparsers.add_parser("delete", help="Delete a prompt")
    delete_parser.add_argument("--slug", required=True, help="Prompt slug to delete")
    delete_parser.add_argument("--force", "-f", action="store_true", help="Skip confirmation")
    delete_parser.add_argument("--project", help="Project name")

    args = parser.parse_args()

    commands = {
        "list": cmd_list,
        "get": cmd_get,
        "invoke": cmd_invoke,
        "test": cmd_test,
        "promote": cmd_promote,
        "create": cmd_create,
        "update": cmd_update,
        "diff": cmd_diff,
        "generate": cmd_generate,
        "delete": cmd_delete,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
