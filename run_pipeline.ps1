$ErrorActionPreference = "Stop"

$projectRoot = $PSScriptRoot
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $python -PathType Leaf)) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($null -eq $pythonCommand) {
        throw "Python was not found. Install Python or create the project virtual environment."
    }
    $python = $pythonCommand.Source
}

Push-Location $projectRoot
try {
    Write-Host "=== Starting Weather Logistics ETL Pipeline ==="
    Write-Host "Started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

    $steps = @(
        @{ Name = "Extracting weather data"; Script = "extract.py" },
        @{ Name = "Transforming data"; Script = "transform.py" },
        @{ Name = "Loading data into PostgreSQL"; Script = "load.py" }
    )

    for ($i = 0; $i -lt $steps.Count; $i++) {
        $step = $steps[$i]
        Write-Host "Step $($i + 1)/$($steps.Count): $($step.Name)..."
        & $python (Join-Path $projectRoot $step.Script)
        if ($LASTEXITCODE -ne 0) {
            throw "$($step.Script) failed with exit code $LASTEXITCODE. Pipeline stopped."
        }
    }

    Write-Host "=== Pipeline completed successfully ==="
}
finally {
    Pop-Location
}
