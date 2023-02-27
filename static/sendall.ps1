chcp 65001
echo Start
$files = Get-ChildItem *.txt -Name
foreach ($file in $files) {
    echo "Send $file"
    $data = `Get-Content $file
    $params = @{simple="1";filter="6,10";filter_r="0,10000";text="$data"}
    Invoke-WebRequest -URI http://phonotext.syllabica.com/statistic?lng=ru -METHOD POST -Body $params -OutFile res_$file
}