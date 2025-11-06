@echo off
REM Run CICFlowMeter using Python (installed with pip install --user cicflowmeter)
REM Ensure tcpdump.exe is in PATH (C:\Tools)

echo Checking tcpdump availability...
where tcpdump >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: tcpdump not found in PATH
    echo Please ensure C:\Tools is in your system PATH and contains tcpdump.exe
    exit /b 1
)

echo tcpdump found: OK
echo.
echo Running CICFlowMeter on attack_traffic.pcap...
python run_cicflowmeter_py.py --pcap attack_traffic.pcap --out cic_features_output.csv

if %errorlevel% equ 0 (
    echo.
    echo SUCCESS: CIC features saved to cic_features_output.csv
    echo.
    echo Filtering to top-20 features...
    python filter_top20_from_cic.py --cic_csv cic_features_output.csv --output_csv top20_features_for_model.csv
    
    if %errorlevel% equ 0 (
        echo.
        echo SUCCESS: Top-20 features saved to top20_features_for_model.csv
        echo You can now use this file with your model!
    )
) else (
    echo.
    echo FAILED: Check error messages above
    echo.
    echo Troubleshooting:
    echo 1. Ensure: pip install --user cicflowmeter
    echo 2. Ensure tcpdump.exe is in C:\Tools and PATH includes C:\Tools
    echo 3. Ensure attack_traffic.pcap exists and is a valid PCAP file
)

pause
