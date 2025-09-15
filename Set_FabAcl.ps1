# Ask for input
$variable1 = Read-Host "Enter the value for variable1 (e.g., workspace name)"
$variable2 = Read-Host "Enter the value for variable2 (e.g., object ID or user/group)"

# Run the commands
Write-Host "Logging into Fabric..."
fab auth login

Write-Host "Setting ACL for Project-portfolio.$variable1 with ID $variable2..."
fab acl set "Project-portfolio.$variable1" -I $variable2 -R contributor -f

Write-Host "Done!"
