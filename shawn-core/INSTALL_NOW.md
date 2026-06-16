# Install shawn-core into Claude Code

This file gives the shortest safe path to make the merged `shawn-core` pack usable locally.

## What is already done

- `shawn-core` is merged into this repo.
- The pack includes Claude Code skills, agents, schemas, templates, and operating docs.
- Private source evidence is intentionally not included.

## Windows PowerShell install

From the folder where you keep GitHub projects:

```powershell
git clone https://github.com/ca049060-spec/Claude-md.git
cd Claude-md\shawn-core
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills"
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\agents"
Copy-Item -Recurse ".\.claude\skills\*" "$env:USERPROFILE\.claude\skills\" -Force
Copy-Item -Recurse ".\.claude\agents\*" "$env:USERPROFILE\.claude\agents\" -Force
```

If the repo is already cloned:

```powershell
cd Claude-md
git pull
cd shawn-core
Copy-Item -Recurse ".\.claude\skills\*" "$env:USERPROFILE\.claude\skills\" -Force
Copy-Item -Recurse ".\.claude\agents\*" "$env:USERPROFILE\.claude\agents\" -Force
```

## Test prompt in Claude Code

```text
North, where are we? Use shawn-core. Give me one urgent risk, one money/work action, one health/legal action, one family action, one joy action, and one thing to stop building.
```

## First real-world test

Use `commitment-ledger` on one real deadline. If it does not create a next action with a due date and proof of completion, the install is not useful yet.
