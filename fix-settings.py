import os

settings = open('components/SettingsTab.tsx', 'r', encoding='utf-8').read()

# 1. Imports
settings = settings.replace('import { Database, CheckCircle2, Download, CloudOff } from "lucide-react";', 'import { Database, CheckCircle2, Download, CloudOff, Info, Share, PlusSquare } from "lucide-react";')

# 2. Add states
states = """  const [showIosInstructions, setShowIosInstructions] = useState(false);
  const [isStandalone, setIsStandalone] = useState(false);"""
settings = settings.replace('  const [pendingSync, setPendingSync] = useState(0);', '  const [pendingSync, setPendingSync] = useState(0);\n' + states)

# 3. Add to useEffect
standalone_check = """    // Check if installed
    if (window.matchMedia('(display-mode: standalone)').matches || (window.navigator as any).standalone === true) {
      setIsStandalone(true);
    }"""
settings = settings.replace('    // PWA Install Prompt', standalone_check + '\n    // PWA Install Prompt')

# 4. Update click handler
old_handler = """  const handleInstallClick = async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      if (outcome === 'accepted') {
        setDeferredPrompt(null);
      }
    }
  };"""

new_handler = """  const handleInstallClick = async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      if (outcome === 'accepted') {
        setDeferredPrompt(null);
        setIsStandalone(true);
      }
    } else {
      setShowIosInstructions(true);
    }
  };"""
settings = settings.replace(old_handler, new_handler)

# 5. Update UI rendering
old_ui = """      {deferredPrompt && (
        <button 
          onClick={handleInstallClick}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-xl font-bold shadow-md flex items-center justify-center transition-colors"
        >
          <Download size={20} className="mr-2" />
          Install App on Phone
        </button>
      )}"""

new_ui = """      {!isStandalone ? (
        <button 
          onClick={handleInstallClick}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-xl font-bold shadow-md flex items-center justify-center transition-colors active:scale-95"
        >
          <Download size={20} className="mr-2" />
          Download App to Home Screen
        </button>
      ) : (
        <div className="w-full bg-green-50 text-green-700 border border-green-200 p-4 rounded-xl font-bold flex items-center justify-center">
          <CheckCircle2 size={20} className="mr-2" />
          App Successfully Installed
        </div>
      )}

      {showIosInstructions && (
        <div className="bg-blue-50 border border-blue-200 p-4 rounded-xl relative mt-4">
          <button onClick={() => setShowIosInstructions(false)} className="absolute top-2 right-2 text-blue-400 hover:text-blue-600">×</button>
          <h4 className="font-bold text-blue-900 flex items-center mb-2"><Info size={18} className="mr-2" /> Apple iOS Instructions</h4>
          <p className="text-sm text-blue-800 mb-3">To install this app on your iPhone or iPad, please follow these 2 quick steps:</p>
          <ol className="text-sm text-blue-800 space-y-2 ml-1">
            <li className="flex items-center">1. Tap the <Share size={16} className="mx-2 bg-white p-0.5 rounded shadow-sm text-blue-600" /> Share icon at the bottom of Safari.</li>
            <li className="flex items-center">2. Scroll down and tap <PlusSquare size={16} className="mx-2 text-gray-700" /> <b>Add to Home Screen</b>.</li>
          </ol>
        </div>
      )}"""

settings = settings.replace(old_ui, new_ui)

with open('components/SettingsTab.tsx', 'w', encoding='utf-8') as f:
    f.write(settings)

print("Done")
