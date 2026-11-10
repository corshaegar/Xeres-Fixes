# Baut Bau\Xeres_Fixes.vdf aus Quelltext\ (Pfade im VDF = Pfade unter Quelltext\, also SYSTEM\AUTORUN\...).
# Aufruf:  powershell -ExecutionPolicy Bypass -File Werkzeuge\bauen.ps1 [-Test -Spiel "<Xeres-Ordner>"]
# -Test laesst vorher Test\zeiger_test.py und Test\blut_test.py am echten Skript der Mod laufen (braucht Python 3).
# Der VDF-Schreiber stammt aus dem Teleport-Fix vom 17.10.2026 (build_vdf.ps1).
param(
    [string]$Src = (Join-Path (Split-Path -Parent $PSScriptRoot) 'Quelltext'),
    [string]$Out = (Join-Path (Split-Path -Parent $PSScriptRoot) 'Bau\Xeres_Fixes.vdf'),
    [string]$Comment = "Xeres-Fixes 1.1.0 - Zeiger-Pruefungen ueber 2 GB, Blutspritzer-Schleife (zParserExtender, 2026-11-10)",
    [switch]$Test,
    [string]$Spiel = ''
)
$ErrorActionPreference = 'Stop'

if ($Test) {
    if (-not $Spiel) { throw '-Test braucht -Spiel <Xeres-Ordner>' }
    foreach ($t in @('zeiger_test.py', 'blut_test.py')) {
        & python -I (Join-Path (Split-Path -Parent $PSScriptRoot) "Test\$t") --spiel $Spiel
        if ($LASTEXITCODE -ne 0) { throw "Test $t fehlgeschlagen - nichts gebaut" }
    }
}

$code = @"
using System;
using System.IO;
using System.Text;
using System.Collections.Generic;

public static class XrfVdfWriter {
    class Node { public string Name; public bool Dir; public string Path; public List<Node> Kids = new List<Node>(); public int Index; }

    static Node Scan(string path, string name) {
        var n = new Node { Name = name.ToUpperInvariant(), Dir = true, Path = path };
        foreach (var d in Directory.GetDirectories(path)) n.Kids.Add(Scan(d, System.IO.Path.GetFileName(d)));
        foreach (var f in Directory.GetFiles(path)) n.Kids.Add(new Node { Name = System.IO.Path.GetFileName(f).ToUpperInvariant(), Dir = false, Path = f });
        n.Kids.Sort((a, b) => string.CompareOrdinal(a.Name, b.Name));
        return n;
    }

    // Katalog: Eintraege eines Ordners liegen zusammen, ein Ordner-Eintrag zeigt auf den Index seines ersten Kindes
    static void Layout(Node dir, List<Node> flat) {
        int first = flat.Count;
        foreach (var k in dir.Kids) flat.Add(k);
        dir.Index = first;
        foreach (var k in dir.Kids) if (k.Dir) Layout(k, flat);
    }

    public static string Build(string src, string outFile, string comment, uint dosTime) {
        var root = Scan(src, "");
        var flat = new List<Node>();
        Layout(root, flat);
        int numFiles = 0; long dataSize = 0;
        foreach (var n in flat) if (!n.Dir) { numFiles++; dataSize += new FileInfo(n.Path).Length; }

        var enc = Encoding.GetEncoding(1252);
        using (var fs = new FileStream(outFile, FileMode.Create, FileAccess.Write))
        using (var bw = new BinaryWriter(fs)) {
            var c = new byte[256];
            for (int i = 0; i < c.Length; i++) c[i] = 0x1A;
            var cb = enc.GetBytes(comment);
            Array.Copy(cb, c, Math.Min(cb.Length, 255));
            bw.Write(c);
            bw.Write(Encoding.ASCII.GetBytes("PSVDSC_V2.00\n\r\n\r"));
            bw.Write((uint)flat.Count); bw.Write((uint)numFiles); bw.Write(dosTime); bw.Write((uint)dataSize);
            bw.Write((uint)296); bw.Write((uint)80);

            long dataPos = 296 + 80L * flat.Count;
            var dataOffsets = new Dictionary<Node, long>();
            foreach (var n in flat) if (!n.Dir) { dataOffsets[n] = dataPos; dataPos += new FileInfo(n.Path).Length; }

            var lastOf = new HashSet<Node>();
            Action<Node> markLast = null;
            markLast = d => { if (d.Kids.Count > 0) lastOf.Add(d.Kids[d.Kids.Count - 1]); foreach (var k in d.Kids) if (k.Dir) markLast(k); };
            markLast(root);

            foreach (var n in flat) {
                var nb = new byte[64];
                for (int i = 0; i < 64; i++) nb[i] = 0x20;
                var nm = enc.GetBytes(n.Name);
                if (nm.Length > 64) throw new Exception("Name zu lang: " + n.Name);
                Array.Copy(nm, nb, nm.Length);
                bw.Write(nb);
                uint type = (n.Dir ? 0x80000000u : 0u) | (lastOf.Contains(n) ? 0x40000000u : 0u);
                bw.Write(n.Dir ? (uint)n.Index : (uint)dataOffsets[n]);
                bw.Write(n.Dir ? 0u : (uint)new FileInfo(n.Path).Length);
                bw.Write(type);
                bw.Write(n.Dir ? 0u : 0x20u);
            }
            foreach (var n in flat) if (!n.Dir) bw.Write(File.ReadAllBytes(n.Path));
        }
        return flat.Count + " Eintraege, " + numFiles + " Dateien";
    }
}
"@
if (-not ([System.Management.Automation.PSTypeName]'XrfVdfWriter').Type) { Add-Type -TypeDefinition $code -Language CSharp }

New-Item -ItemType Directory -Force (Split-Path -Parent $Out) | Out-Null
$now = Get-Date
$dos = [uint32]((($now.Year - 1980) -shl 25) -bor ($now.Month -shl 21) -bor ($now.Day -shl 16) -bor ($now.Hour -shl 11) -bor ($now.Minute -shl 5) -bor [int]($now.Second / 2))
$res = [XrfVdfWriter]::Build((Resolve-Path $Src).Path, $Out, $Comment, $dos)
"Gebaut: $Out ($res), SHA-256 $((Get-FileHash $Out -Algorithm SHA256).Hash)"
