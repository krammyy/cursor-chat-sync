# Chat Sync Across Devices (Cursor + GitHub)

This project is configured to export the latest Cursor chat transcript and push it to GitHub after each agent response.

## What is synced

- `.cursor/chat-sync/latest-chat.jsonl` - latest transcript snapshot
- `.cursor/chat-sync/latest-chat.meta.json` - export metadata

## How it works

- Hook config: `.cursor/hooks.json`
- Hook script: `.cursor/hooks/sync-chat-to-github.ps1`
- Trigger: `afterAgentResponse`

After every assistant response in this project, the hook:

1. Locates the most recent transcript in your local Cursor transcript folders.
2. Copies it into `.cursor/chat-sync/`.
3. Creates a local git commit with the updated snapshot.
4. Pushes to current remote branch.

## Setup on each device

1. Clone this repository and open it in Cursor.
2. Sign in to the same GitHub account in terminal (`git` must be able to push without prompts).
3. Ensure PowerShell scripts can run for this command (the hook already uses `-ExecutionPolicy Bypass`).
4. Make sure your branch has an upstream remote (`git push -u origin <branch>` once).
5. Send one message in chat; verify that `.cursor/chat-sync/latest-chat.jsonl` updates and a new commit appears.

## Important notes

- If `git push` fails (auth/network/protection rules), chat still continues; sync simply skips that push.
- This stores chat content in git history. Do not use this if your chat may contain sensitive data.
- On another device, run `git pull` to get the latest transcript snapshot.
