echo off
chcp 65001
echo Start
$files = Get-ChildItem *.txt -Name
foreach ($file in $files) {
    echo "Send $file"
    echo "Choise"
    Write-Host "1: " -noNewLine; Get-Content -encoding UTF8 $file | select -first 1
    Write-Host "2: " -noNewLine; Get-Content $file | select -first 1
    $options = [System.Management.Automation.Host.ChoiceDescription[]] @("&1", "&2", "&Quit")
    $opt = $host.UI.PromptForChoice("" , "" , $Options, 1)
    switch($opt)
    {
        0 { $data = `Get-Content -encoding UTF8 $file }
        1 { $data = `Get-Content $file }
        2 { exit; }
    }
    
    $params = @{simple="1";filter="6,10";filter_r="0,10000";text="$data"}
    Invoke-WebRequest -URI http://phonotext.syllabica.com/statistic?lng=ru -METHOD POST -Body $params -OutFile res_$file
    Invoke-WebRequest -URI http://phonotext.syllabica.com/svg?lng=ru -METHOD POST -Body $params -OutFile res_$file.html
}