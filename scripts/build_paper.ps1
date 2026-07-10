param(
    [switch]$UseBibTeX
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

if ($UseBibTeX) {
    pdflatex main.tex
    bibtex main
    pdflatex main.tex
    pdflatex main.tex
} else {
    pdflatex main.tex
    pdflatex main.tex
}
