$Env:CONDA_EXE = "/Users/vanessadungl/Desktop/AI-Energy-Dashboard/exit/bin/conda"
$Env:_CE_M = $null
$Env:_CE_CONDA = $null
$Env:_CONDA_ROOT = "/Users/vanessadungl/Desktop/AI-Energy-Dashboard/exit"
$Env:_CONDA_EXE = "/Users/vanessadungl/Desktop/AI-Energy-Dashboard/exit/bin/conda"
$CondaModuleArgs = @{ChangePs1 = $True}
Import-Module "$Env:_CONDA_ROOT\shell\condabin\Conda.psm1" -ArgumentList $CondaModuleArgs

Remove-Variable CondaModuleArgs