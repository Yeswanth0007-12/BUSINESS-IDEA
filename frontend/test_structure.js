/**
 * Test script to verify Phase 1 frontend structure
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function testStructure() {
    console.log('Testing Phase 1 Frontend Structure...');
    console.log('='.repeat(50));
    
    const requiredFiles = [
        'package.json',
        'vite.config.ts',
        'tsconfig.json',
        'tsconfig.node.json',
        'tailwind.config.js',
        'postcss.config.js',
        'index.html',
        '.env.example',
        'src/main.tsx',
        'src/App.tsx',
        'src/index.css',
        'src/services/api.ts',
    ];
    
    const requiredDirs = [
        'src',
        'src/pages',
        'src/components',
        'src/layout',
        'src/services',
        'src/contexts',
        'src/types',
        'public',
    ];
    
    // Test directories
    console.log('\n✓ Testing Directories:');
    let allDirsExist = true;
    for (const dir of requiredDirs) {
        const exists = fs.existsSync(dir) && fs.statSync(dir).isDirectory();
        const status = exists ? '✓' : '✗';
        console.log(`  ${status} ${dir}`);
        if (!exists) allDirsExist = false;
    }
    
    // Test files
    console.log('\n✓ Testing Files:');
    let allFilesExist = true;
    for (const file of requiredFiles) {
        const exists = fs.existsSync(file) && fs.statSync(file).isFile();
        const status = exists ? '✓' : '✗';
        console.log(`  ${status} ${file}`);
        if (!exists) allFilesExist = false;
    }
    
    // Summary
    console.log('\n' + '='.repeat(50));
    if (allDirsExist && allFilesExist) {
        console.log('✅ Phase 1 Frontend Structure: PASSED');
        console.log('All required files and directories exist!');
        return true;
    } else {
        console.log('❌ Phase 1 Frontend Structure: FAILED');
        console.log('Some files or directories are missing!');
        return false;
    }
}

const success = testStructure();
process.exit(success ? 0 : 1);
