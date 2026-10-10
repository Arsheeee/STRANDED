$unityPath = "C:\Program Files\Unity\Hub\Editor\6000.5.3f1\Editor\Unity.exe"
$projectPath = "D:\Unity\Projects\STRANDED"
$logPath = "D:\Unity\Projects\STRANDED\unity_build.log"

Write-Host "Starting Unity batchmode build..."
$proc = Start-Process -FilePath $unityPath -ArgumentList "-projectpath `"$projectPath`" -batchmode -quit -executeMethod IslandTilemapBuilder.BuildIslandAndCamera -logFile `"$logPath`"" -Wait -PassThru

Write-Host "Unity exited with code: $($proc.ExitCode)"
if (Test-Path $logPath) {
    Write-Host "Log file exists! Size: $((Get-Item $logPath).Length) bytes"
    Get-Content $logPath -Tail 25
} else {
    Write-Host "Log file does not exist at $logPath"
}
