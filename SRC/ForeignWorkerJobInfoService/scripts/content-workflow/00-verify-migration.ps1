param(
  [string]$DbUrl = $env:CONTENT_DB_URL,
  [string]$DbUser = $env:CONTENT_DB_USER,
  [string]$DbPassword = $env:CONTENT_DB_PASSWORD,
  [switch]$ApplyMigration,
  [switch]$LoadSampleData
)

$ErrorActionPreference = 'Stop'

function Require-Command($Name) {
  $command = Get-Command $Name -ErrorAction SilentlyContinue
  if (-not $command) {
    throw "$Name is required in PATH."
  }
}

function Invoke-PsqlFile($FilePath, $Label) {
  if (-not (Test-Path $FilePath)) {
    throw "SQL file not found: $FilePath"
  }

  Write-Host ""
  Write-Host "== $Label =="

  if ($DbPassword) {
    $env:PGPASSWORD = $DbPassword
  }

  if ($DbUrl) {
    if ($DbUser) {
      & psql $DbUrl -U $DbUser -v ON_ERROR_STOP=1 -f $FilePath
    } else {
      & psql $DbUrl -v ON_ERROR_STOP=1 -f $FilePath
    }
  } else {
    & psql -v ON_ERROR_STOP=1 -f $FilePath
  }

  if ($LASTEXITCODE -ne 0) {
    throw "psql failed: $Label"
  }
}

Require-Command 'psql'

$Root = Resolve-Path (Join-Path $PSScriptRoot '..\..')
$MigrationSql = Join-Path $Root 'src\main\resources\db\migration\2026_06_14_content_approval_workflow.sql'
$SampleSql = Join-Path $Root 'src\main\resources\db\sample\content_workflow_local_sample_data.sql'
$CheckSql = Join-Path $PSScriptRoot 'content_workflow_migration_check.sql'

Invoke-PsqlFile $CheckSql 'migration check before optional apply'

if ($ApplyMigration) {
  Invoke-PsqlFile $MigrationSql 'apply content workflow migration'
}

if ($LoadSampleData) {
  Invoke-PsqlFile $SampleSql 'load local sample data'
}

Invoke-PsqlFile $CheckSql 'migration check after optional apply'
