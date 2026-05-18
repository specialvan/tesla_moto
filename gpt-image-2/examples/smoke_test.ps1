#requires -version 5.1
<#
gpt-image-2 烟囱测试：验证端点 / key / 模型联通。
执行方式（在仓库根目录或 gpt-image-2/ 目录下都能跑）：

    .\gpt-image-2\examples\smoke_test.ps1
#>

$ErrorActionPreference = "Stop"
$pkgRoot = Split-Path -Parent $PSScriptRoot

Write-Host "[smoke] pkg root = $pkgRoot"
Write-Host "[smoke] installing requirements (one-time)"
python -m pip install -r (Join-Path $pkgRoot "requirements.txt") | Out-Null

Write-Host "[smoke] launching python -m gpt_image2.generate --smoke"
$env:PYTHONPATH = $pkgRoot + [IO.Path]::PathSeparator + $env:PYTHONPATH
python -m gpt_image2.generate --smoke

if ($LASTEXITCODE -ne 0) {
    Write-Error "[smoke] FAILED with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}

Write-Host "[smoke] OK. Inspect outputs\_smoke\smoke-r00.png to confirm."
