# escape=`

FROM mcr.microsoft.com/windows/servercore/iis
COPY Hydrus-1D\* Hydrus-1D\
RUN powershell Remove-Item c:/inetpub/wwwroot/iisstart.htm -force
RUN powershell Remove-Item c:/inetpub/wwwroot/iisstart.png -force
RUN powershell Import-Module WebAdministration
RUN powershell New-WebAppPool -Name 'TestPool'

ENTRYPOINT "Hydrus-1D\H1D_CALC.EXE workspace\hydrus"
