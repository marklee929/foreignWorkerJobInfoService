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

function Invoke-JsonCurl($Method, $Path, $Body) {
  $headers = @(
    '-H', 'Accept: application/json',
    '-H', 'Content-Type: application/json',
    '-H', "X-Device-Id: $DeviceId"
  )
  $cookieArgs = @()
  if ($Cookie) {
    $cookieArgs = @('-b', $Cookie)
  }

  $url = "$ApiBase$Path"
  $tempFile = $null
  try {
    if ($null -ne $Body) {
      $tempFile = New-TemporaryFile
      $Body | ConvertTo-Json -Depth 20 | Set-Content -Path $tempFile -Encoding UTF8
      $raw = & curl.exe -sS -X $Method @headers @cookieArgs --data-binary "@$tempFile" $url
    } else {
      $raw = & curl.exe -sS -X $Method @headers @cookieArgs $url
    }
    if ($LASTEXITCODE -ne 0) {
      throw "curl failed: $Method $Path"
    }
    if (-not $raw) {
      throw "empty response: $Method $Path"
    }
    return $raw | ConvertFrom-Json
  } finally {
    if ($tempFile -and (Test-Path $tempFile)) {
      Remove-Item -LiteralPath $tempFile -Force
    }
  }
}

Require-Command 'curl.exe'

$result = Invoke-JsonCurl 'POST' '/api/admin/content/e2e-dry-run' @{}

if (-not $result.sourceItemId -or -not $result.generatedContentId) {
  throw 'E2E dry-run did not return sourceItemId/generatedContentId.'
}

if ($result.status -ne 'SENT_TO_TELEGRAM') {
  throw "Expected SENT_TO_TELEGRAM, got $($result.status)."
}

$detail = Invoke-JsonCurl 'GET' "/api/admin/content/generated/$($result.generatedContentId)" $null

if ($detail.status -ne 'SENT_TO_TELEGRAM') {
  throw "Detail status mismatch. Expected SENT_TO_TELEGRAM, got $($detail.status)."
}

if (-not $detail.reviewLogs -or @($detail.reviewLogs).Count -lt 1) {
  throw 'Review log was not saved for Telegram dry-run.'
}

[PSCustomObject]@{
  ok = $true
  source_item_id = $result.sourceItemId
  generated_content_id = $result.generatedContentId
  status = $result.status
  review_log_id = $result.reviewLogId
  telegram_dry_run_result = $result.telegramDryRunResult
} | ConvertTo-Json -Depth 10
