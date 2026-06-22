const { rcedit } = require('rcedit');
const path = require('path');

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

exports.default = async function(context) {
  const { appOutDir, packager } = context;
  const exePath = path.join(appOutDir, `${packager.appInfo.productFilename}.exe`);
  const iconPath = path.join(context.packager.projectDir, 'public', 'tray_icon.ico');
  
  console.log(`[AfterPack] Setting icon for ${exePath}...`);
  
  const maxRetries = 5;
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      await rcedit(exePath, {
        icon: iconPath,
        'version-string': {
          'ProductName': 'VESPERA',
          'CompanyName': 'VESPERA OS',
          'FileDescription': 'VESPERA Cognitive Core',
          'InternalName': 'vespera-dashboard',
          'OriginalFilename': 'VESPERA.exe'
        }
      });
      console.log('[AfterPack] Successfully set executable icon!');
      return;
    } catch (err) {
      console.warn(`[AfterPack] Attempt ${attempt} failed to set icon: ${err.message}`);
      if (attempt < maxRetries) {
        console.log(`[AfterPack] Retrying in 1.5 seconds...`);
        await sleep(1500);
      } else {
        console.error('[AfterPack] All attempts to set executable icon failed.');
      }
    }
  }
};
