# escape=`

FROM mcr.microsoft.com/windows/servercore/iis
COPY Hydrus-1D\* Hydrus-1D\
COPY model.txt Hydrus-1D\
COPY Chojnice_vg_sand\* Chojnice_vg_sand\
COPY Chojnice_vg_sand.h1d Chojnice_vg_sand.h1d
RUN powershell Remove-Item c:/inetpub/wwwroot/iisstart.htm -force
RUN powershell Remove-Item c:/inetpub/wwwroot/iisstart.png -force
RUN powershell Import-Module WebAdministration
RUN powershell New-WebAppPool -Name 'TestPool'

ENTRYPOINT "Hydrus-1D\H1D_CALC.EXE Chojnice_vg_sand"