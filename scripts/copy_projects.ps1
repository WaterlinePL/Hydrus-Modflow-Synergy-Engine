# Scripts is meant to be used inside water_modeling_agh or water_modeling_agh/scripts
$pwd = Get-Location
if ( $pwd -like "*\scripts") {
    md ..\tests
    Copy-Item ..\sample\* -Destination ..\tests -Recurse -Force
} else {
    md .\tests
    Copy-Item .\sample\* -Destination .\tests -Recurse -Force
}