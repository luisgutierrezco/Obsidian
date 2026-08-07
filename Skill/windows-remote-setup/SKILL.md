---
name: windows-remote-setup
description: Administra equipos Windows remotos via WinRM (renombrar PC, crear usuarios, ubicaciones de red, credenciales, accesos directos)
tags:
  - Agentes
  - Administracion
  - DesarrolloTech
---

# Windows Remote Setup

Skill para administrar equipos Windows remotos vía WinRM. Automatiza tareas comunes de configuración inicial.

## Variables de entorno

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `$WR_HOST` | IP del equipo remoto | `192.168.89.99` |
| `$WR_USER` | Usuario admin remoto | `soporteti` |
| `$WR_PASS` | Contraseña admin remoto | `123456` |
| `$WR_TARGET` | IP del servidor de destino (NAS/file server) | `192.168.90.63` |
| `$WR_TARGET_USER` | Usuario para el recurso de red | `B214` |
| `$WR_TARGET_PASS` | Contraseña del recurso de red | `B214` |

## Conexión WinRM

### Probar conectividad
```powershell
Test-NetConnection -ComputerName $WR_HOST -Port 5985 -WarningAction SilentlyContinue
Test-WSMan -ComputerName $WR_HOST
```

### Crear credencial y conectar
```powershell
$secpass = ConvertTo-SecureString $WR_PASS -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential($WR_USER, $secpass)
Invoke-Command -ComputerName $WR_HOST -Credential $cred -Authentication Default -ScriptBlock {
    # comandos aqui
}
```

### Script remoto con base64 (evita problemas de quoting)
```powershell
$script = @'
# tu script aqui
'@
$encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($script))
Invoke-Command -ComputerName $WR_HOST -Credential $cred -ScriptBlock {
    Invoke-Expression $([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String($args[0])))
} -ArgumentList $encoded
```

## Operaciones

### 1. Renombrar equipo

Requiere reinicio. El nombre no debe tener espacios ni caracteres especiales.

```powershell
# Método 1: PowerShell cmdlet
Invoke-Command -ComputerName $WR_HOST -Credential $cred -ScriptBlock {
    Rename-Computer -NewName "NUEVO_NOMBRE" -Force
    Write-Output "Renombrado. Reiniciando..."
    Restart-Computer -Force
}

# Método 2: Registry (fallback si Rename-Computer falla)
Invoke-Command -ComputerName $WR_HOST -Credential $cred -ScriptBlock {
    $reg = [Microsoft.Win32.Registry]::LocalMachine.OpenSubKey(
        'SYSTEM\CurrentControlSet\Control\ComputerName\ComputerName', $true)
    $reg.SetValue('ComputerName', 'NUEVO_NOMBRE')
    $reg.Close()
    $reg2 = [Microsoft.Win32.Registry]::LocalMachine.OpenSubKey(
        'SYSTEM\CurrentControlSet\Control\ComputerName\ActiveComputerName', $true)
    if ($reg2) { $reg2.SetValue('ComputerName', 'NUEVO_NOMBRE'); $reg2.Close() }
    Restart-Computer -Force
}
```

### 2. Crear usuario local con privilegios admin

```powershell
Invoke-Command -ComputerName $WR_HOST -Credential $cred -ScriptBlock {
    net user NOMBRE_USER CONTRASENA /add
    net localgroup Administradores NOMBRE_USER /add
}
```

> ⚠ En español el grupo admin es `Administradores`, no `Administrators`.
> ⚠ El nombre de usuario no puede ser igual al nombre del equipo.

### 3. Credenciales de red (Windows Credential Manager)

No se pueden guardar desde sesión WinRM directamente (restringido por seguridad de Windows).
La solución es ejecutar via tarea programada:

```powershell
$script = @'
Add-Type @"
using System; using System.Runtime.InteropServices;
public class CM {
    [DllImport("advapi32.dll", CharSet=CharSet.Unicode)]
    public static extern bool CredWriteW(ref CREDENTIALW c, uint f);
    [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)]
    public struct CREDENTIALW {
        public uint Flags; public uint Type; public string TargetName;
        public string Comment; public long LastWritten;
        public uint CredentialBlobSize; public IntPtr CredentialBlob;
        public uint Persist; public uint AttributeCount; public IntPtr Attributes;
        public string TargetAlias; public string UserName;
    }
    public static int Save(string t, string u, string p) {
        var c = new CREDENTIALW();
        c.TargetName = t; c.UserName = u; c.Type = 1; c.Persist = 2;
        c.CredentialBlob = Marshal.StringToCoTaskMemUni(p);
        c.CredentialBlobSize = (uint)(p.Length * 2);
        bool ok = CredWriteW(ref c, 0);
        Marshal.FreeCoTaskMem(c.CredentialBlob);
        return ok ? 1 : 0;
    }
}
"@
[CM]::Save($args[0], $args[1], $args[2])
'@
# Guardar script y ejecutar como el usuario destino via tarea programada
$encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($script))
Invoke-Command -ComputerName $WR_HOST -Credential $cred -ScriptBlock {
    $b64 = $args[0]; $targetServer = $args[1]; $targetUser = $args[2]; $targetPass = $args[3]
    $content = [Text.Encoding]::Unicode.GetString([Convert]::FromBase64String($b64))
    $content += "`r`n[CM]::Save('$targetServer', '$targetUser', '$targetPass')"
    $ps1 = "C:\Windows\Temp\savecred.ps1"
    Set-Content -Path $ps1 -Value $content -Force
    $a = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File $ps1"
    $t = New-ScheduledTaskTrigger -Once -At (Get-Date).AddSeconds(5)
    $s = New-ScheduledTaskSettingsSet -Hidden -StartWhenAvailable
    Register-ScheduledTask -TaskName "SaveCredTemp" -Action $a -Trigger $t -Settings $s -User $targetUser -Password $targetPass -RunLevel Highest -Force
    Start-Sleep -Seconds 3; Start-ScheduledTask -TaskName "SaveCredTemp"
    Start-Sleep -Seconds 20; Unregister-ScheduledTask -TaskName "SaveCredTemp" -Confirm:$false
    Remove-Item $ps1 -Force -ErrorAction SilentlyContinue
    Write-Output "Credencial guardada para $targetUser"
} -ArgumentList $encoded, $WR_TARGET, $WR_TARGET_USER, $WR_TARGET_PASS
```

### 4. Mapear unidades de red (persistentes)

```powershell
# Con letra de unidad (aparece en "Dispositivos y unidades")
Invoke-Command -ComputerName $WR_HOST -Credential $cred -ScriptBlock {
    net use X: \\$WR_TARGET\share /user:$WR_TARGET_USER $WR_TARGET_PASS /persistent:yes
}

# Sin letra (aparece en "Ubicaciones de red")
Invoke-Command -ComputerName $WR_HOST -Credential $cred -ScriptBlock {
    net use \\$WR_TARGET\share /user:$WR_TARGET_USER $WR_TARGET_PASS /persistent:yes
}

# Eliminar unidad
Invoke-Command -ComputerName $WR_HOST -Credential $cred -ScriptBlock {
    net use X: /delete
}
```

### 5. Ubicación de red (Network Shortcuts + desktop.ini + target.lnk)

```powershell
$script = @'
$base = "$env:APPDATA\Microsoft\Windows\Network Shortcuts"
$folder = "$base\NOMBRE"
if (-not (Test-Path $folder)) { New-Item -ItemType Directory -Path $folder -Force | Out-Null }
$ini = "[.ShellClassInfo]`r`nCLSID2={0AFACED1-E828-11D1-9187-B532F1E9575D}`r`nFlags=2"
Set-Content -Path "$folder\desktop.ini" -Value $ini -Force
Set-ItemProperty -Path "$folder\desktop.ini" -Name Attributes -Value "Hidden, System" -Force
$sh = New-Object -ComObject WScript.Shell
$lnk = $sh.CreateShortcut("$folder\target.lnk")
$lnk.TargetPath = "\\192.168.90.63\share"
$lnk.Save()
cmd /c "attrib +R +S `"$folder`" /D /L"
'@
```

### 6. Ubicación de red en el escritorio (misma estructura)

```powershell
$script = @'
$destinos = @("$env:PUBLIC\Desktop", "C:\Users\USUARIO\Desktop")
$ini = "[.ShellClassInfo]`r`nCLSID2={0AFACED1-E828-11D1-9187-B532F1E9575D}`r`nFlags=2"
foreach ($dest in $destinos) {
    if (-not (Test-Path $dest)) { continue }
    $folder = "$dest\NOMBRE"
    if (-not (Test-Path $folder)) { New-Item -ItemType Directory -Path $folder -Force | Out-Null }
    Set-Content -Path "$folder\desktop.ini" -Value $ini -Force
    Set-ItemProperty -Path "$folder\desktop.ini" -Name Attributes -Value "Hidden, System" -Force
    $sh = New-Object -ComObject WScript.Shell
    $lnk = $sh.CreateShortcut("$folder\target.lnk")
    $lnk.TargetPath = "\\192.168.90.63\share"
    $lnk.Save()
    cmd /c "attrib +R +S `"$folder`" /D /L"
}
'@
```

### 7. Acceso directo en escritorio (a ubicación de red existente)

```powershell
$script = @'
$shell = New-Object -ComObject WScript.Shell
$l = $shell.CreateShortcut("$env:PUBLIC\Desktop\NOMBRE.lnk")
$l.TargetPath = "$env:APPDATA\Microsoft\Windows\Network Shortcuts\NOMBRE"
$l.Save()
'@
```

### 8. Persistencia vía tarea programada (al iniciar sesión)

```powershell
Invoke-Command -ComputerName $WR_HOST -Credential $cred -ScriptBlock {
    $a = New-ScheduledTaskAction -Execute "net.exe" -Argument "use \\$WR_TARGET\share /user:$WR_TARGET_USER $WR_TARGET_PASS /persistent:yes"
    $t = New-ScheduledTaskTrigger -AtLogOn -User "USUARIO_DESTINO"
    $s = New-ScheduledTaskSettingsSet -Hidden -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    Register-ScheduledTask -TaskName "MapShare" -Action $a -Trigger $t -Settings $s -RunLevel Highest -Force
}
```

### 9. Ejecutar script inmediato como otro usuario

```powershell
Invoke-Command -ComputerName $WR_HOST -Credential $cred -ScriptBlock {
    $a = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -File C:\ruta\script.ps1"
    $t = New-ScheduledTaskTrigger -Once -At (Get-Date).AddSeconds(5)
    $s = New-ScheduledTaskSettingsSet -Hidden -StartWhenAvailable
    Register-ScheduledTask -TaskName "TempTask" -Action $a -Trigger $t -Settings $s -User "USUARIO" -Password "PASS" -RunLevel Highest -Force
    Start-Sleep -Seconds 2; Start-ScheduledTask -TaskName "TempTask"
    Start-Sleep -Seconds 20; Unregister-ScheduledTask -TaskName "TempTask" -Confirm:$false
}
```

### 10. Registry Run para usuario específico

```powershell
Invoke-Command -ComputerName $WR_HOST -Credential $cred -ScriptBlock {
    $sid = (Get-CimInstance Win32_UserAccount -Filter "Name='USUARIO'").SID
    $reg = [Microsoft.Win32.Registry]::Users
    $hk = $reg.OpenSubKey("$sid\Software\Microsoft\Windows\CurrentVersion\Run", $true)
    if (-not $hk) { $hk = $reg.CreateSubKey("$sid\Software\Microsoft\Windows\CurrentVersion\Run") }
    $hk.SetValue("NombreTarea", "comando")
    $hk.Close()
}
```

## Workflows comunes

### Workflow: Setup completo de PC nuevo

```powershell
$WR_HOST = "IP_PC"
$WR_USER = "soporteti"
$WR_PASS = "123456"
$WR_TARGET = "192.168.90.63"
$WR_TARGET_USER = "B214"
$WR_TARGET_PASS = "B214"
$NUEVO_NOMBRE = "CAJAXXXX"
$USUARIO_LOCAL = "B214"
$PASS_LOCAL = "123"

$secpass = ConvertTo-SecureString $WR_PASS -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential($WR_USER, $secpass)

# 1. Renombrar
Invoke-Command -ComputerName $WR_HOST -Credential $cred -ScriptBlock {
    Rename-Computer -NewName $args[0] -Force
} -ArgumentList $NUEVO_NOMBRE

# 2. Crear usuario
Invoke-Command -ComputerName $WR_HOST -Credential $cred -ScriptBlock {
    net user $args[0] $args[1] /add
    net localgroup Administradores $args[0] /add
} -ArgumentList $USUARIO_LOCAL, $PASS_LOCAL

# 3. Mapear unidades
Invoke-Command -ComputerName $WR_HOST -Credential $cred -ScriptBlock {
    net use \\$args[0]\listas /user:$args[1] $args[2] /persistent:yes
    net use \\$args[0]\b214 /user:$args[1] $args[2] /persistent:yes
} -ArgumentList $WR_TARGET, $WR_TARGET_USER, $WR_TARGET_PASS

# 4. Ubicaciones de red en escritorio (para B214)
# (usar script de la seccion 6)

# 5. Persistencia logon
# (usar script de la seccion 8)

# 6. Reiniciar
Invoke-Command -ComputerName $WR_HOST -Credential $cred -ScriptBlock { Restart-Computer -Force }
```

### Workflow: Agregar ubicación de red + escritorio

```powershell
Param(
    [string]$HostPC,
    [string]$UserAdmin,
    [string]$PassAdmin,
    [string]$TargetServer = "192.168.90.63",
    [string]$TargetUser = "B214",
    [string]$TargetPass = "B214",
    [string]$ShareName,       # "listas" o "b214"
    [string]$DisplayName       # "LISTAS" o "B214"
)

$secpass = ConvertTo-SecureString $PassAdmin -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential($UserAdmin, $secpass)

$script = @'
param($tserver, $tuser, $tpass, $share, $dname)
$ini = "[.ShellClassInfo]`r`nCLSID2={0AFACED1-E828-11D1-9187-B532F1E9575D}`r`nFlags=2"
$destinos = @("$env:PUBLIC\Desktop", "C:\Users\$tuser\Desktop",
    "$env:APPDATA\Microsoft\Windows\Network Shortcuts")
foreach ($dest in $destinos) {
    if (-not (Test-Path $dest)) { continue }
    $folder = "$dest\$dname"
    if (-not (Test-Path $folder)) { New-Item -ItemType Directory -Path $folder -Force | Out-Null }
    Set-Content -Path "$folder\desktop.ini" -Value $ini -Force
    Set-ItemProperty -Path "$folder\desktop.ini" -Name Attributes -Value "Hidden, System" -Force
    $sh = New-Object -ComObject WScript.Shell
    $lnk = $sh.CreateShortcut("$folder\target.lnk")
    $lnk.TargetPath = "\\$tserver\$share"
    $lnk.Save()
    cmd /c "attrib +R +S `"$folder`" /D /L"
}
'@
$encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($script))
Invoke-Command -ComputerName $HostPC -Credential $cred -ScriptBlock {
    Invoke-Expression $([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String($args[0])))
} -ArgumentList $encoded
```

## Errores conocidos y soluciones

| Error | Causa | Solución |
|-------|-------|----------|
| `WinRM no puede completar la operación` | Host inalcanzable o firewall | Verificar `Test-NetConnection -Port 5985`, revisar firewall |
| `No se encuentra ningún parámetro de posición que acepte el argumento 'True'` | PS versión antigua | Usar `net user` en vez de `New-LocalUser` |
| `El nombre de usuario no puede ser igual que el del equipo` | Username = computer name | Cambiar nombre del equipo o usar otro username |
| El grupo local especificado no existe | Locale | `Administradores` (es) vs `Administrators` (en) |
| `no se pueden guardar credenciales desde esta sesión de inicio` | WinRM = network logon | Usar tarea programada como el usuario destino |
| `Acceso denegado` al modificar TrustedHosts | Sin privilegios admin | Ejecutar PowerShell como administrador |
| Ternary operator `? :` no funciona | PS 5.1 | Usar `if/else` o `@($cond,$alt)[!$cond]` |

## Notas importantes

1. **PowerShell 5.1** en equipos Windows Server 2016/2019, Windows 10/11 - no soporta `? :` ternary
2. **Sesiones WinRM** son tipo "Network Logon" - NO pueden interactuar con el Credential Manager
3. **Tareas programadas** ejecutan en sesión diferente - ideales para persistencia
4. **Base64** es la forma más confiable de pasar scripts complejos a `Invoke-Command`
5. **Locale español**: grupos `Administradores`, mensajes en español
6. **SID de usuario**: necesario para modificar registry Run de otro usuario


## Enlaces relacionados

- [[AGENTESOPENCODE/README|Agentes-Indice]] - indice de agentes y skills
- [[Soluciones/SolucionesChrystal/README|Soluciones Chrystal]]

