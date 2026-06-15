param(
  [string]$ApiBase = $(if ($env:CONTENT_API_BASE_URL) { $env:CONTENT_API_BASE_URL } else { 'http://localhost:5100' }),
  [string]$DbUrl = $env:CONTENT_DB_URL,
  [string]$DbUser = $env:CONTENT_DB_USER,
  [string]$DbPassword = $env:CONTENT_DB_PASSWORD,
  [switch]$ApplyMigration,
  [switch]$LoadSampleData,
  [switch]$SkipDb
)

$ErrorActionPreference = 'Stop'

if (-not $SkipDb) {
  $dbArgs = @()
  if ($DbUrl) { $dbArgs += @('-DbUrl', $DbUrl) }
  if ($DbUser) { $dbArgs += @('-DbUser', $DbUser) }
  if ($DbPassword) { $dbArgs += @('-DbPassword', $DbPassword) }
  if ($ApplyMigration) { $dbArgs += '-ApplyMigration' }
  if ($LoadSampleData) { $dbArgs += '-LoadSampleData' }
  & (Join-Path $PSScriptRoot '00-verify-migration.ps1') @dbArgs
}

& (Join-Path $PSScriptRoot '01-e2e-dry-run.ps1') -ApiBase $ApiBase
& (Join-Path $PSScriptRoot '02-state-transition-test.ps1') -ApiBase $ApiBase
& (Join-Path $PSScriptRoot '03-admin-ui-api-smoke.ps1') -ApiBase $ApiBase

[PSCustomObject]@{
  ok = $true
  api_base = $ApiBase
  db_checked = -not $SkipDb
  migration_apply_requested = [bool]$ApplyMigration
  sample_data_load_requested = [bool]$LoadSampleData
} | ConvertTo-Json -Depth 10
