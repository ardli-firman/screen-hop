@echo off
echo Sedang mengatur antrian, Mohon Tunggu Sebentar.

:: Hapus file sementara jika ada
if exist monitors.xml del monitors.xml

:: Ambil daftar monitor dalam format XML
monitor.exe /sxml monitors.xml
timeout /t 2 >nul

:: Panggil PowerShell untuk membaca XML dan mendapatkan nomor monitor eksternal
for /f "delims=" %%A in ('powershell -ExecutionPolicy Bypass -NoProfile -File "%~dp0get_external_monitor.ps1"') do (
    set "monitor_number=%%A"
)

:: Jika tidak menemukan monitor eksternal, keluar
if "%monitor_number%"=="" (
    echo Monitor eksternal tidak terdeteksi! Pastikan monitor diluar tersambung dan aktif
    pause
    exit
)

echo Monitor eksternal terdeteksi: DISPLAY%monitor_number%

:: Jalankan Firefox dalam mode kiosk
run.exe exec show "C:\Program Files\Mozilla Firefox\firefox.exe" --new-window --kiosk="http://172.16.61.60:1999/antrian-poli"

:: Tunggu beberapa detik agar Firefox terbuka
timeout /t 3 >nul

:: Pindahkan Firefox ke monitor eksternal secara dinamis
monitor.exe /MoveWindow %monitor_number% Process "firefox.exe"
