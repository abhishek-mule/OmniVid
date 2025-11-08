$ErrorActionPreference = 'Stop'
$resp = Invoke-WebRequest -Uri 'http://localhost:3000/api/auth/google?next=%2Fapp%2Feditor' -MaximumRedirection 0
Write-Output ("StatusCode: $($resp.StatusCode)")
$loc = $resp.Headers['Location']
if ($loc) {
  Write-Output ("Location: $loc")
} else {
  Write-Output 'No Location header'
}