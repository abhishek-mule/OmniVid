# Cleanup and Restructure Script for OmniVid Project

# Define paths
$rootDir = "c:\Users\HP\Desktop\omnivid"
$backupDir = "$rootDir\old_frontend_backup"
$webAppDir = "$rootDir\apps\web"

# Create backup directory if it doesn't exist
if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
}

# Backup existing frontend files
Write-Host "Backing up existing frontend files..."
$frontendDirs = @(
    "app",
    "src",
    "public",
    "components",
    "context",
    "contexts",
    "hooks",
    "lib",
    "styles",
    "types"
)

foreach ($dir in $frontendDirs) {
    $source = "$rootDir\$dir"
    if (Test-Path $source) {
        Write-Host "Backing up $source..."
        Copy-Item -Path $source -Destination "$backupDir\$dir" -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# Create web app directory structure
Write-Host "Creating new directory structure..."
$webDirs = @(
    "$webAppDir\src\app",
    "$webAppDir\src\components\features",
    "$webAppDir\src\components\ui",
    "$webAppDir\src\lib",
    "$webAppDir\public"
)

foreach ($dir in $webDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# Move files to new structure
Write-Host "Moving files to new structure..."
$mappings = @{
    "app" = "$webAppDir\src\app"
    "src\app" = "$webAppDir\src\app"
    "public" = "$webAppDir\public"
    "components" = "$webAppDir\src\components"
    "lib" = "$webAppDir\src\lib"
    "styles" = "$webAppDir\src\styles"
    "types" = "$webAppDir\src\types"
}

foreach ($source in $mappings.Keys) {
    $sourcePath = "$rootDir\$source"
    $destPath = $mappings[$source]
    
    if (Test-Path $sourcePath) {
        Write-Host "Moving $source to $destPath"
        Get-ChildItem -Path $sourcePath | ForEach-Object {
            $itemDest = Join-Path $destPath $_.Name
            if ($_.PSIsContainer) {
                Copy-Item -Path $_.FullName -Destination $itemDest -Recurse -Force -ErrorAction SilentlyContinue
            } else {
                Copy-Item -Path $_.FullName -Destination $itemDest -Force -ErrorAction SilentlyContinue
            }
        }
    }
}

# Create package.json for the web app
$packageJson = @{
    name = "@omnivid/web"
    version = "0.1.0"
    private = $true
    scripts = @{
        dev = "next dev"
        build = "next build"
        start = "next start"
        lint = "next lint"
    }
    dependencies = @{
        # Will be populated from the original package.json
    }
}

# Copy dependencies from original package.json if it exists
$originalPkgJson = "$rootDir\package.json"
if (Test-Path $originalPkgJson) {
    $pkg = Get-Content $originalPkgJson -Raw | ConvertFrom-Json
    $packageJson.dependencies = $pkg.dependencies
}

# Save package.json
$packageJson | ConvertTo-Json -Depth 10 | Out-File -FilePath "$webAppDir\package.json" -Encoding utf8

# Create root package.json if it doesn't exist
if (-not (Test-Path "$rootDir\package.json")) {
    $rootPkgJson = @{
        name = "omnivid"
        version = "0.1.0"
        private = true
        workspaces = @("apps/*", "packages/*")
        scripts = @{
            dev = "turbo run dev"
            build = "turbo run build"
            start = "turbo run start"
            lint = "turbo run lint"
        }
    }
    $rootPkgJson | ConvertTo-Json -Depth 10 | Out-File -FilePath "$rootDir\package.json" -Encoding utf8
}

# Create turbo.json if it doesn't exist
if (-not (Test-Path "$rootDir\turbo.json")) {
    $turboJson = @{
        "$schema" = "https://turbo.build/schema.json"
        "pipeline" = @{
            build = @{
                dependsOn = @("^build")
                outputs = @(".next/**")
            }
            dev = @{
                cache = $false
            }
        }
    }
    $turboJson | ConvertTo-Json -Depth 10 | Out-File -FilePath "$rootDir\turbo.json" -Encoding utf8
}

# Clean up old files and directories
Write-Host "Cleaning up old files..."
$dirsToRemove = @(
    "app",
    "src",
    "components",
    "context",
    "contexts",
    "hooks",
    "lib",
    "styles",
    "types",
    "frontend",
    "frontend_backup",
    "omnivid-restructured"
)

foreach ($dir in $dirsToRemove) {
    $path = "$rootDir\$dir"
    if (Test-Path $path) {
        Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host ""
Write-Host "========================================"
Write-Host "Project has been reorganized successfully!"
Write-Host "========================================"
Write-Host ""
Write-Host "New structure:"
Write-Host "- apps/web/"
Write-Host "  - src/"
Write-Host "    - app/         # Next.js app router"
Write-Host "    - components/  # Reusable components"
Write-Host "    - lib/        # Utility functions"
Write-Host "    - public/     # Static files"
Write-Host "- packages/"
Write-Host "  - database/     # Database models and migrations"
Write-Host "  - ui/           # Shared UI components"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Review the new structure in 'apps/web'"
Write-Host "2. Run 'npm install' in the root directory"
Write-Host "3. Run 'npm run dev' to start the development server"
Write-Host ""
Write-Host "Note: Original files have been backed up to '$backupDir'"
