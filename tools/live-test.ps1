<#
.SYNOPSIS
  Smoke-test SDP V3 connector operations against a live instance and capture
  request/response evidence.

.DESCRIPTION
  Exercises the Service Desk connector's core operations (List / Get / Create
  Request) the same way Power Platform will: authtoken header, Accept header,
  and every parameter wrapped in the single input_data envelope. Writes each
  response to docs/test-evidence/.

  READS are safe against the shared public demo. Only run -IncludeCreate against
  a disposable instance you own — never the demo.

.EXAMPLE
  # Read-only smoke test against the public demo (reads only; see README for key scoping)
  ./tools/live-test.ps1 -HostName demo.servicedeskplus.com -ApiKey <your-api-key>

.EXAMPLE
  # Full test incl. create, against a local disposable instance
  ./tools/live-test.ps1 -HostName localhost:8080 -ApiKey <key> -IncludeCreate -SkipCertCheck
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory)][string]$HostName,
  [Parameter(Mandatory)][string]$ApiKey,
  [switch]$IncludeCreate,
  [switch]$SkipCertCheck,
  [string]$EvidenceDir = (Join-Path $PSScriptRoot '..\docs\test-evidence')
)

$ErrorActionPreference = 'Stop'
$accept = 'application/vnd.manageengine.sdp.v3+json'
$base = "https://$HostName/api/v3"
$headers = @{ authtoken = $ApiKey; Accept = $accept }
New-Item -ItemType Directory -Force $EvidenceDir | Out-Null
if ($SkipCertCheck) { $PSDefaultParameterValues['Invoke-WebRequest:SkipCertificateCheck'] = $true }

function Save-Evidence($name, $reqLine, $resp) {
  $path = Join-Path $EvidenceDir "$name.txt"
  @("# $name", "## Request", $reqLine, "", "## Response (HTTP $($resp.StatusCode))", $resp.Content) |
    Set-Content -Encoding utf8 $path
  Write-Host "  saved -> $path"
}

# --- List Requests ---
$li = '{"list_info":{"row_count":2,"start_index":1,"get_total_count":true}}'
$uri = "$base/requests?input_data=$([uri]::EscapeDataString($li))"
$r = Invoke-WebRequest -Uri $uri -Headers $headers -Method GET
Write-Host "ListRequests -> HTTP $($r.StatusCode)"
Save-Evidence 'listrequests' "GET $uri" $r
$firstId = ($r.Content | ConvertFrom-Json).requests[0].id

# --- Get Request ---
if ($firstId) {
  $uri = "$base/requests/$firstId"
  $r = Invoke-WebRequest -Uri $uri -Headers $headers -Method GET
  Write-Host "GetRequest($firstId) -> HTTP $($r.StatusCode)"
  Save-Evidence 'getrequest' "GET $uri" $r
}

# --- Create Request (write — disposable instances only) ---
if ($IncludeCreate) {
  $payload = '{"request":{"subject":"Connector smoke test","description":"Created by live-test.ps1","request_type":{"name":"Incident"}}}'
  $body = "input_data=$([uri]::EscapeDataString($payload))"
  $r = Invoke-WebRequest -Uri "$base/requests" -Headers $headers -Method POST `
        -ContentType 'application/x-www-form-urlencoded' -Body $body
  Write-Host "CreateRequest -> HTTP $($r.StatusCode)"
  Save-Evidence 'createrequest' "POST $base/requests  (body: $body)" $r
}
