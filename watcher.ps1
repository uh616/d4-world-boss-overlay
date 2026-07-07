
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);
}
"@

$sb = New-Object System.Text.StringBuilder 256
while ($true) {
    $hwnd = [Win32]::GetForegroundWindow()
    if ([Win32]::GetWindowText($hwnd, $sb, 256) -gt 0) {
        [Console]::WriteLine($sb.ToString())
    } else {
        [Console]::WriteLine("UNKNOWN")
    }
    Start-Sleep -Seconds 1
}
