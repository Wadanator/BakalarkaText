
#requires -version 5.0
# Tento skript stačí spustiť dvojklikom (alebo RUN v Prieskumníku)
# Automaticky rekompiluje všetky Mermaid diagramy v tejto zložke a podzložkách

$ErrorActionPreference = 'Stop'
Set-Location "$PSScriptRoot"

try {
    Get-ChildItem -Recurse -Filter *.mmd | ForEach-Object {
        $mmd = $_.FullName
        $base = $mmd -replace '\.mmd$',''
        Write-Host "Kompilujem $mmd ..."
        npx.cmd -y @mermaid-js/mermaid-cli -i "$mmd" -o "$base.png" -w 5000 -s 3
        npx.cmd -y @mermaid-js/mermaid-cli -i "$mmd" -o "$base.svg"
        npx.cmd -y @mermaid-js/mermaid-cli -i "$mmd" -o "$base.pdf"
        Write-Host "Hotovo: $base.[png|svg|pdf]"
    }
    Write-Host "Všetky diagramy boli úspešne vygenerované."
    Start-Sleep -Seconds 3
} catch {
    Write-Host "Chyba: $_"
    Start-Sleep -Seconds 10
}
