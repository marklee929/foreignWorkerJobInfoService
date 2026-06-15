param(
  [string]$ApiBase = $(if ($env:CONTENT_API_BASE_URL) { $env:CONTENT_API_BASE_URL } else { 'http://localhost:5100' }),
  [string]$DeviceId = $(if ($env:CONTENT_ADMIN_DEVICE_ID) { $env:CONTENT_ADMIN_DEVICE_ID } else { 'local-dev' }),
  [string]$Cookie = $env:CONTENT_ADMIN_COOKIE
)

$ErrorActionPreference = 'Stop'

function Require-Command($Name) {
  $command = Get-Command $Name -ErrorAction SilentlyContinue
  if (-not $command) {
    throw "$Name is required in PATH."
  }
}

function Invoke-JsonCurl($Path) {
  $headers = @('-H', 'Accept: application/json', '-H', "X-Device-Id: $DeviceId")
  $cookieArgs = @()
  if ($Cookie) {
    $cookieArgs = @('-b', $Cookie)
  }
  $raw = & curl.exe -sS -X GET @headers @cookieArgs "$ApiBase$Path"
  if ($LASTEXITCODE -ne 0) {
    throw "curl failed: GET $Path"
  }
  if (-not $raw) {
    throw "empty response: GET $Path"
  }
  return $raw | ConvertFrom-Json
}

Require-Command 'curl.exe'

$checks = @(
  @{ name = 'dashboard'; path = '/api/admin/content-review/dashboard'; kind = 'object' },
  @{ name = 'sourceCatalog'; path = '/api/admin/source-catalog'; kind = 'array' },
  @{ name = 'generated'; path = '/api/admin/content/generated?status=GENERATED&limit=20'; kind = 'array' },
  @{ name = 'sentToTelegram'; path = '/api/admin/content/generated?status=SENT_TO_TELEGRAM&limit=20'; kind = 'array' },
  @{ name = 'approved'; path = '/api/admin/content/generated?status=APPROVED&limit=20'; kind = 'array' },
  @{ name = 'rejected'; path = '/api/admin/content/generated?status=REJECTED&limit=20'; kind = 'array' },
  @{ name = 'sourceItems'; path = '/api/admin/source-items?limit=20'; kind = 'array' },
  @{ name = 'reviewLogs'; path = '/api/admin/review-logs?limit=20'; kind = 'array' },
  @{ name = 'publishTargets'; path = '/api/admin/content/publish-targets?limit=20'; kind = 'array' },
  @{ name = 'communitySignals'; path = '/api/admin/community-signals?limit=20'; kind = 'array' }
)

$results = @()
foreach ($check in $checks) {
  $payload = Invoke-JsonCurl $check.path
  $count = if ($check.kind -eq 'array') { @($payload).Count } else { 1 }
  if ($check.kind -eq 'array' -and $null -eq $payload) {
    throw "$($check.name) did not return an array-compatible payload."
  }
  $results += [PSCustomObject]@{
    name = $check.name
    path = $check.path
    count = $count
    ok = $true
  }
}

[PSCustomObject]@{
  ok = $true
  api_base = $ApiBase
  checks = $results
} | ConvertTo-Json -Depth 10
