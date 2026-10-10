$unityPath = "C:\Program Files\Unity\Hub\Editor\6000.5.3f1\Editor\Unity.exe"
$projectPath = "D:\Unity\Projects\STRANDED"
$logPath = "D:\Unity\Projects\STRANDED\unity_sim.log"

Write-Host "Running STRANDED Island Simulation & In-Game Camera Captures..."
$proc = Start-Process -FilePath $unityPath -ArgumentList "-projectpath `"$projectPath`" -batchmode -quit -executeMethod IslandPlayModeSimulator.RunSimulation -logFile `"$logPath`"" -Wait -PassThru

Write-Host "Unity exited with code: $($proc.ExitCode)"
if (Test-Path $logPath) {
    Write-Host "Log file exists! Size: $((Get-Item $logPath).Length) bytes"
    Get-Content $logPath -Tail 40
} else {
    Write-Host "Log file does not exist at $logPath"
}
