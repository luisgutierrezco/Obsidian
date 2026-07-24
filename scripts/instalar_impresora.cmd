@echo off
cscript %WINDIR%\System32\Printing_Admin_Scripts\en-US\prnport.vbs -a -r "IPP_PORT" -h 192.168.92.21 -o raw -n 631
cscript %WINDIR%\System32\Printing_Admin_Scripts\en-US\prnmngr.vbs -a -p "AUDITORIA EPSON" -m "EPSON L3250 Series" -r "http://192.168.92.21:631/printers/AUDITORIA_EPSON"
echo Listo.
