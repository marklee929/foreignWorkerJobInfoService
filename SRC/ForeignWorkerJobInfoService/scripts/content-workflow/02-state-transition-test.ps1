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
      $Body | ConvertTo-Json -Depth 30 | Set-Content -Path $tempFile -Encoding UTF8
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

function Assert-Status($ContentId, $Expected) {
  $detail = Invoke-JsonCurl 'GET' "/api/admin/content/generated/$ContentId" $null
  if ($detail.status -ne $Expected) {
    throw "Content #$ContentId status mismatch. expected=$Expected actual=$($detail.status)"
  }
  return $detail
}

Require-Command 'curl.exe'

$suffix = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()
$collectPayload = @{
  domain = 'EMPLOYMENT'
  sourcePlatform = 'manual'
  category = 'employment'
  dryRun = $false
  items = @(
    @{
      sourceDomain = 'EMPLOYMENT'
      sourcePlatform = 'manual'
      sourceName = 'Local Curl State Test'
      sourceUrl = "https://local.workconnect/state-test/approve-$suffix"
      canonicalUrl = "https://local.workconnect/state-test/approve-$suffix"
      publishableLinkUrl = "https://local.workconnect/state-test/approve-$suffix"
      title = "Approve path sample $suffix"
      bodyText = 'Local curl test source for GENERATED to SENT_TO_TELEGRAM to APPROVED transition.'
      summaryText = 'Approve path local source.'
      language = 'en'
      countryCode = 'KR'
      category = 'employment'
      subcategory = 'curl_approve'
      rawPayload = '{"script":"02-state-transition-test","path":"approve"}'
      sourceRiskLevel = 'LOW'
      accessRestriction = 'PUBLIC'
      copyrightRiskLevel = 'LOW'
      piiCheckedYn = $true
      usableForContentYn = $true
    },
    @{
      sourceDomain = 'EMPLOYMENT'
      sourcePlatform = 'manual'
      sourceName = 'Local Curl State Test'
      sourceUrl = "https://local.workconnect/state-test/reject-$suffix"
      canonicalUrl = "https://local.workconnect/state-test/reject-$suffix"
      publishableLinkUrl = "https://local.workconnect/state-test/reject-$suffix"
      title = "Reject path sample $suffix"
      bodyText = 'Local curl test source for GENERATED to SENT_TO_TELEGRAM to REJECTED transition.'
      summaryText = 'Reject path local source.'
      language = 'en'
      countryCode = 'KR'
      category = 'employment'
      subcategory = 'curl_reject'
      rawPayload = '{"script":"02-state-transition-test","path":"reject"}'
      sourceRiskLevel = 'LOW'
      accessRestriction = 'PUBLIC'
      copyrightRiskLevel = 'LOW'
      piiCheckedYn = $true
      usableForContentYn = $true
    }
  )
}

$collected = Invoke-JsonCurl 'POST' '/api/admin/sources/collect' $collectPayload
$sourceIds = @($collected.items | ForEach-Object { $_.id })
if ($sourceIds.Count -ne 2) {
  throw "Expected 2 source items, got $($sourceIds.Count)."
}

$generated = Invoke-JsonCurl 'POST' '/api/admin/content/generate' @{
  sourceItemIds = $sourceIds
  language = 'en'
  targetPersona = 'foreign workers and residents in Korea'
  sendToTelegram = $false
  telegramDryRun = $true
}
$generatedRows = @($generated)
if ($generatedRows.Count -ne 2) {
  throw "Expected 2 generated content rows, got $($generatedRows.Count)."
}

$approveContentId = $generatedRows[0].id
$rejectContentId = $generatedRows[1].id

Assert-Status $approveContentId 'GENERATED' | Out-Null
Assert-Status $rejectContentId 'GENERATED' | Out-Null

Invoke-JsonCurl 'POST' "/api/admin/content/$approveContentId/send-telegram" @{
  dryRun = $true
  comment = 'curl state transition dry-run send for approve path'
} | Out-Null
Invoke-JsonCurl 'POST' "/api/admin/content/$rejectContentId/send-telegram" @{
  dryRun = $true
  comment = 'curl state transition dry-run send for reject path'
} | Out-Null

Assert-Status $approveContentId 'SENT_TO_TELEGRAM' | Out-Null
Assert-Status $rejectContentId 'SENT_TO_TELEGRAM' | Out-Null

$approved = Invoke-JsonCurl 'POST' "/api/admin/content/$approveContentId/approve" @{
  reviewerId = 'curl-local'
  reviewerName = 'Curl Local'
  comment = 'Approved by local curl state transition test.'
}
$rejected = Invoke-JsonCurl 'POST' "/api/admin/content/$rejectContentId/reject" @{
  reviewerId = 'curl-local'
  reviewerName = 'Curl Local'
  comment = 'Rejected by local curl state transition test.'
}

if ($approved.status -ne 'APPROVED') {
  throw "Approve path failed. actual=$($approved.status)"
}
if ($rejected.status -ne 'REJECTED') {
  throw "Reject path failed. actual=$($rejected.status)"
}

[PSCustomObject]@{
  ok = $true
  source_item_ids = $sourceIds
  approved_content_id = $approveContentId
  rejected_content_id = $rejectContentId
  approved_status = $approved.status
  rejected_status = $rejected.status
} | ConvertTo-Json -Depth 10
