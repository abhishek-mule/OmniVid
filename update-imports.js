const fs = require('fs');
const path = require('path');

// Define the import mappings
const importMappings = {
  '@/components/auth/': '@/components/features/auth/',
  '@/components/dashboard/': '@/components/features/dashboard/',
  '@/components/editor/': '@/components/features/editor/',
  '@/components/templates/': '@/components/features/templates/',
  '@/components/LayoutClient': '@/components/layout/LayoutClient',
};

// Function to update imports in a file
function updateImports(filePath) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    let updated = false;

    for (const [oldPath, newPath] of Object.entries(importMappings)) {
      if (content.includes(oldPath)) {
        content = content.replace(new RegExp(oldPath.replace(/\//g, '\\/'), 'g'), newPath);
        updated = true;
      }
    }

    if (updated) {
      fs.writeFileSync(filePath, content, 'utf8');
      console.log(`Updated imports in ${filePath}`);
    }
  } catch (error) {
    console.error(`Error processing ${filePath}:`, error);
  }
}

// Function to process all files in a directory
function processDirectory(directory) {
  const files = fs.readdirSync(directory);
  
  files.forEach(file => {
    const fullPath = path.join(directory, file);
    const stat = fs.statSync(fullPath);
    
    if (stat.isDirectory()) {
      processDirectory(fullPath);
    } else if (file.endsWith('.tsx') || file.endsWith('.ts') || file.endsWith('.js') || file.endsWith('.jsx')) {
      updateImports(fullPath);
    }
  });
}

// Start processing from the src directory
const srcDir = path.join(__dirname, 'frontend', 'src');
if (fs.existsSync(srcDir)) {
  console.log('Updating imports in:', srcDir);
  processDirectory(srcDir);
} else {
  console.error('Source directory not found:', srcDir);
}
