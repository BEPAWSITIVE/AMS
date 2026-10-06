import os

with open('components/ScannerTab.tsx', 'r', encoding='utf-8') as f:
    scanner = f.read()

# Fix pause/resume issues
scanner = scanner.replace("""      if (scannerRef.current) {
        scannerRef.current.pause();
      }""", """      if (scannerRef.current) {
        try { scannerRef.current.pause(); } catch(e) {}
      }""")

scanner = scanner.replace("""    } catch (err) {
      if (scannerRef.current) scannerRef.current.resume();
    }""", """    } catch (err) {
      console.error(err);
      if (scannerRef.current) {
        try { scannerRef.current.resume(); } catch(e) {}
      }
    }""")

scanner = scanner.replace("""      setTimeout(() => {
        setScanResult(null);
        if (scannerRef.current) scannerRef.current.resume();
      }, 2500);""", """      setTimeout(() => {
        setScanResult(null);
        if (scannerRef.current) {
          try { scannerRef.current.resume(); } catch(e) {}
        }
      }, 2500);""")

scanner = scanner.replace("""    setTimeout(() => {
      setScanResult(null);
      if (scannerRef.current) scannerRef.current.resume();
    }, 3000);""", """    setTimeout(() => {
      setScanResult(null);
      if (scannerRef.current) {
        try { scannerRef.current.resume(); } catch(e) {}
      }
    }, 3000);""")

scanner = scanner.replace('if (scannerRef.current) scannerRef.current.resume();', 'if (scannerRef.current) { try { scannerRef.current.resume(); } catch(e) {} }')
scanner = scanner.replace('if (scannerRef.current) scannerRef.current.pause();', 'if (scannerRef.current) { try { scannerRef.current.pause(); } catch(e) {} }')

# Fix live search logic
old_search_logic = """  const handleManualSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSearching(true);
    setSearchResults([]);
    
    const cleanPhone = searchPhone.trim().replace('+91 ', '');
    if (!cleanPhone) {
      setIsSearching(false);
      return;
    }
    
    let results: Employee[] = [];
    
    if (navigator.onLine) {
      const { data } = await supabase.from('employees').select('*').ilike('phone', `%${cleanPhone}%`);
      if (data) results = data;
    } else {
      const cached = localStorage.getItem('cached_employees');
      if (cached) {
        const emps: Employee[] = JSON.parse(cached);
        results = emps.filter(e => e.phone && e.phone.includes(cleanPhone));
      }
    }
    
    setSearchResults(results);
    setIsSearching(false);
  };"""

new_search_logic = """  useEffect(() => {
    const cleanPhone = searchPhone.trim().replace('+91 ', '');
    if (cleanPhone.length < 2) {
      setSearchResults([]);
      return;
    }
    
    setIsSearching(true);
    const timer = setTimeout(async () => {
      let results: Employee[] = [];
      if (navigator.onLine) {
        const { data } = await supabase.from('employees').select('*').ilike('phone', `%${cleanPhone}%`).limit(10);
        if (data) results = data;
      } else {
        const cached = localStorage.getItem('cached_employees');
        if (cached) {
          const emps: Employee[] = JSON.parse(cached);
          results = emps.filter(e => e.phone && e.phone.includes(cleanPhone)).slice(0, 10);
        }
      }
      setSearchResults(results);
      setIsSearching(false);
    }, 300);
    
    return () => clearTimeout(timer);
  }, [searchPhone, navigator.onLine]);

  const handleManualSearch = (e: React.FormEvent) => { e.preventDefault(); };"""
scanner = scanner.replace(old_search_logic, new_search_logic)

# Remove the "No profiles found" message when typing hasn't started deeply
scanner = scanner.replace("""            {!isSearching && searchResults.length === 0 && searchPhone !== "+91 " && (
              <div className="text-center text-sm text-gray-400 py-4">No profiles found for this number.</div>
            )}""", """            {!isSearching && searchResults.length === 0 && searchPhone.trim().replace('+91 ', '').length >= 2 && (
              <div className="text-center text-sm text-gray-400 py-4">No profiles found for this number.</div>
            )}""")


with open('components/ScannerTab.tsx', 'w', encoding='utf-8') as f:
    f.write(scanner)

print("Done")
