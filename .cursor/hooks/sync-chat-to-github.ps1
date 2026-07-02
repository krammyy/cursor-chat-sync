$ErrorActionPreference = "Stop"

function Get-LatestTranscriptFile {
    param(
        [string]$RepoName
    )

    $projectsRoot = Join-Path $env:USERPROFILE ".cursor\projects"
    if (-not (Test-Path $projectsRoot)) {
        return $null
    }

    $projectDirs = Get-ChildItem -Path $projectsRoot -Directory
    $scopedProjects = $projectDirs | Where-Object { $_.Name -like "*$RepoName*" }
    if (-not $scopedProjects) {
        $scopedProjects = $projectDirs
    }

    $transcriptDirs = @()
    foreach ($projectDir in $scopedProjects) {
        $candidate = Join-Path $projectDir.FullName "agent-transcripts"
        if (Test-Path $candidate) {
            $transcriptDirs += $candidate
        }
    }

    if (-not $transcriptDirs) {
        return $null
    }

    $latest = $null
    foreach ($dir in $transcriptDirs) {
        $current = Get-ChildItem -Path $dir -Filter "*.jsonl" -File -Recurse | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($null -eq $current) {
            continue
        }
        if ($null -eq $latest -or $current.LastWriteTime -gt $latest.LastWriteTime) {
            $latest = $current
        }
    }

    return $latest
}

try {
    $repoRoot = (Get-Location).Path
    $repoName = Split-Path -Leaf $repoRoot
    $latestTranscript = Get-LatestTranscriptFile -RepoName $repoName

    if ($null -eq $latestTranscript) {
        Write-Output '{ "status": "no_transcript_found" }'
        exit 0
    }

    $syncDir = Join-Path $repoRoot ".cursor\chat-sync"
    if (-not (Test-Path $syncDir)) {
        New-Item -Path $syncDir -ItemType Directory | Out-Null
    }

    $destinationTranscript = Join-Path $syncDir "latest-chat.jsonl"
    Copy-Item -Path $latestTranscript.FullName -Destination $destinationTranscript -Force

    $meta = [ordered]@{
        exportedAtUtc  = (Get-Date).ToUniversalTime().ToString("o")
        transcriptFile = $latestTranscript.FullName
        transcriptMtime = $latestTranscript.LastWriteTimeUtc.ToString("o")
        branch         = (git rev-parse --abbrev-ref HEAD 2>$null)
    }
    $metaJson = $meta | ConvertTo-Json -Depth 4
    Set-Content -Path (Join-Path $syncDir "latest-chat.meta.json") -Value $metaJson -Encoding UTF8

    $null = git rev-parse --is-inside-work-tree 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Output '{ "status": "not_a_git_repo" }'
        exit 0
    }

    git add -- ".cursor/chat-sync/latest-chat.jsonl" ".cursor/chat-sync/latest-chat.meta.json" | Out-Null
    $pending = git status --porcelain -- ".cursor/chat-sync"
    if (-not $pending) {
        Write-Output '{ "status": "nothing_to_commit" }'
        exit 0
    }

    $message = "chore(chat-sync): update transcript snapshot $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    git commit -m $message | Out-Null
    $env:GIT_TERMINAL_PROMPT = "0"
    git -c credential.interactive=never push | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Output '{ "status": "committed_but_push_failed" }'
        exit 0
    }

    Write-Output '{ "status": "ok" }'
    exit 0
}
catch {
    # Fail open: do not block agent flow if sync fails.
    Write-Output ('{ "status": "error", "message": "' + ($_.Exception.Message.Replace('"', "'")) + '" }')
    exit 0
}
