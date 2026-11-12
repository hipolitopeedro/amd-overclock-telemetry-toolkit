<#
.SYNOPSIS
    Audits AMD Ryzen & Radeon hardware configuration, memory OC speed, and hunts WHEA-Logger
    Event ID 18/19/46 errors in Windows Event Viewer to identify unstable Curve Optimizer cores.

.DESCRIPTION
    EN: Queries WMI/CIM for CPU, Motherboard/BIOS, RAM speed (verifying 3200 MT/s OC), and GPU details.
        Scans the System Event Log for Microsoft-Windows-WHEA-Logger events, extracts the Processor
        APIC ID from the event XML, and maps it to the physical AMD Ryzen core (Core 0..7) so you know
        which core needs less negative Curve Optimizer offset in BIOS.
    PT: Consulta WMI/CIM para CPU, Placa-mãe/BIOS, velocidade da RAM (validando o OC de 3200 MT/s) e GPU.
        Varre o Event Viewer buscando eventos do Microsoft-Windows-WHEA-Logger, extrai o APIC ID do XML
        e indica qual núcleo físico do Ryzen (Core 0..7) causou reinício ou erro no Curve Optimizer.
#>

[CmdletBinding()]
param (
    [Parameter(Mandatory = $false)]
    [int]$DaysBack = 14
)

Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host "   AMD RYZEN & RADEON HARDWARE / OVERCLOCKING DIAGNOSTICS (WHEA HUNTER)" -ForegroundColor Cyan
Write-Host "==========================================================================" -ForegroundColor Cyan

# 1. CPU, Motherboard & BIOS Overview
$CPU   = Get-CimInstance -ClassName Win32_Processor | Select-Object -First 1
$Board = Get-CimInstance -ClassName Win32_BaseBoard | Select-Object -First 1
$BIOS  = Get-CimInstance -ClassName Win32_BIOS | Select-Object -First 1
$GPU   = Get-CimInstance -ClassName Win32_VideoController | Where-Object { $_.Name -notmatch "Basic|Remote" } | Select-Object -First 1

Write-Host "`n[1] HARDWARE & BIOS SUMMARY" -ForegroundColor Yellow
Write-Host "    CPU         : $($CPU.Name.Trim()) ($($CPU.NumberOfCores) Cores / $($CPU.NumberOfLogicalProcessors) Threads)"
Write-Host "    Motherboard : $($Board.Manufacturer) $($Board.Product)"
Write-Host "    BIOS Version: $($BIOS.SMBIOSBIOSVersion) (Release: $($BIOS.ReleaseDate.ToString('yyyy-MM-dd')))"
if ($GPU) {
    Write-Host "    GPU         : $($GPU.Name) (Driver: $($GPU.DriverVersion))"
}

# 2. Memory Overclocking & Channel Verification
Write-Host "`n[2] MEMORY (RAM) FREQUENCY & OVERCLOCK STATUS" -ForegroundColor Yellow
$Dimms = Get-CimInstance -ClassName Win32_PhysicalMemory
foreach ($Dimm in $Dimms) {
    $CapGB = [math]::Round($Dimm.Capacity / 1GB, 0)
    Write-Host "    Slot [$($Dimm.DeviceLocator)] : $CapGB GB $($Dimm.Manufacturer) ($($Dimm.PartNumber.Trim())) | Configured Clock: $($Dimm.ConfiguredClockSpeed) MT/s" -ForegroundColor Green
}

# 3. WHEA-Logger Core Crash / Instability Hunter
Write-Host "`n[3] WHEA-LOGGER HARDWARE ERROR AUDIT (LAST $DaysBack DAYS)" -ForegroundColor Yellow
$StartTime = (Get-Date).AddDays(-$DaysBack)
$WheaEvents = Get-WinEvent -FilterHashtable @{
    LogName      = 'System'
    ProviderName = 'Microsoft-Windows-WHEA-Logger'
    StartTime    = $StartTime
} -ErrorAction SilentlyContinue

if (-not $WheaEvents) {
    Write-Host "    [OK] Zero WHEA-Logger events found in the last $DaysBack days! CPU Curve Optimizer & RAM OC are stable." -ForegroundColor Green
} else {
    Write-Host "    [ALERT] Found $($WheaEvents.Count) WHEA-Logger event(s)! Inspecting APIC IDs..." -ForegroundColor Red
    foreach ($Evt in $WheaEvents) {
        [xml]$Xml = $Evt.ToXml()
        $ApicIdNode = $Xml.Event.EventData.Data | Where-Object { $_.Name -eq 'ProcessorApicId' }
        $ErrorType  = ($Xml.Event.EventData.Data | Where-Object { $_.Name -eq 'ErrorSource' }).'#text'
        if ($null -ne $ApicIdNode) {
            $ApicId = [int]$ApicIdNode.'#text'
            # With SMT enabled on Zen 3, Physical Core = floor(APIC_ID / 2)
            $PhysicalCore = [math]::Floor($ApicId / 2)
            Write-Host ("    -> [{0}] Event ID {1} | APIC ID: {2} (Physical Core #{3}) | Source: {4}" -f `
                $Evt.TimeCreated.ToString('yyyy-MM-dd HH:mm:ss'), $Evt.Id, $ApicId, $PhysicalCore, $ErrorType) -ForegroundColor Red
            Write-Host "       Action: Reduce negative Curve Optimizer magnitude on Core #$PhysicalCore in BIOS (e.g., from -25 to -20)." -ForegroundColor Yellow
        } else {
            Write-Host ("    -> [{0}] Event ID {1}: {2}" -f $Evt.TimeCreated.ToString('yyyy-MM-dd HH:mm:ss'), $Evt.Id, $Evt.Message) -ForegroundColor Red
        }
    }
}
Write-Host "==========================================================================" -ForegroundColor Cyan
