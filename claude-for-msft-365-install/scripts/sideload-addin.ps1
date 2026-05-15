<#
.SYNOPSIS
  Sideload an Office add-in manifest for local debugging on Windows.

.DESCRIPTION
  Registers the manifest as a developer add-in via a registry value under
  HKCU:\SOFTWARE\Microsoft\Office\16.0\Wef\Developer whose NAME is the
  add-in <Id> and whose DATA is the absolute manifest path. Naming the
  value by <Id> means clear-addin-cache.ps1 -Id <GUID> removes it cleanly.

  This writes the registry value directly — it does NOT use
  office-addin-dev-settings.

.EXAMPLE
  sideload-addin.ps1 C:\path\to\manifest.xml          # dry-run: show what would happen
  sideload-addin.ps1 C:\path\to\manifest.xml -Apply   # actually install
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true, Position = 0)][string]$Manifest,
  [switch]$Apply
)

$ErrorActionPreference = 'Stop'
$devKey = 'HKCU:\SOFTWARE\Microsoft\Office\16.0\Wef\Developer'

if (-not (Test-Path $Manifest)) { throw "manifest not found: $Manifest" }
$manifestPath = (Resolve-Path $Manifest).Path
$addinId = ([xml](Get-Content $manifestPath)).OfficeApp.Id
if (-not $addinId) { throw "could not read <Id> from manifest" }

if ($Apply) { Write-Host "Sideloading add-in $addinId" }
else        { Write-Host "DRY RUN — would sideload (re-run with -Apply to install):" }

if ($Apply) {
  if (-not (Test-Path $devKey)) { New-Item -Path $devKey -Force | Out-Null }
  New-ItemProperty -Path $devKey -Name $addinId -Value $manifestPath `
    -PropertyType String -Force | Out-Null
  Write-Host "  registered $devKey\$addinId -> $manifestPath"
} else {
  Write-Host "  would set $devKey value '$addinId' = $manifestPath"
}

Write-Host "Quit and reopen Excel/Word/PowerPoint. The add-in appears under"
Write-Host "Insert -> My Add-ins. Remove later with:"
Write-Host "  .\clear-addin-cache.ps1 -Id $addinId -Apply"
