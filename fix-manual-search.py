import os

scanner = open('components/ScannerTab.tsx', 'r', encoding='utf-8').read()

# 1. Change state init
scanner = scanner.replace('useState("+91 ");', 'useState("");')
scanner = scanner.replace('setSearchPhone("+91 ");', 'setSearchPhone("");')

# 2. Update useEffect query logic
old_search_logic = """  useEffect(() => {
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
  }, [searchPhone, navigator.onLine]);"""

new_search_logic = """  useEffect(() => {
    const query = searchPhone.trim();
    if (query.length < 2) {
      setSearchResults([]);
      return;
    }
    
    setIsSearching(true);
    const timer = setTimeout(async () => {
      let results: Employee[] = [];
      if (navigator.onLine) {
        const { data } = await supabase.from('employees').select('*').or(`phone.ilike.%${query}%,name.ilike.%${query}%`).limit(15);
        if (data) results = data;
      } else {
        const cached = localStorage.getItem('cached_employees');
        if (cached) {
          const emps: Employee[] = JSON.parse(cached);
          const lowerQuery = query.toLowerCase();
          results = emps.filter(e => 
            (e.phone && e.phone.includes(query)) || 
            (e.name && e.name.toLowerCase().includes(lowerQuery))
          ).slice(0, 15);
        }
      }
      setSearchResults(results);
      setIsSearching(false);
    }, 300);
    
    return () => clearTimeout(timer);
  }, [searchPhone, navigator.onLine]);"""
scanner = scanner.replace(old_search_logic, new_search_logic)

# 3. Fix the "No profiles found" check
old_no_profiles = """            {!isSearching && searchResults.length === 0 && searchPhone.trim().replace('+91 ', '').length >= 2 && (
              <div className="text-center text-sm text-gray-400 py-4">No profiles found for this number.</div>
            )}"""
new_no_profiles = """            {!isSearching && searchResults.length === 0 && searchPhone.trim().length >= 2 && (
              <div className="text-center text-sm text-gray-400 py-4">No profiles found.</div>
            )}"""
scanner = scanner.replace(old_no_profiles, new_no_profiles)

# 4. Fix placeholder & Button text
scanner = scanner.replace('placeholder="+91 Phone Number"', 'placeholder="Name or Phone Number"')
scanner = scanner.replace('Search by Phone Number', 'Search Name or Phone')

# 5. Fix modal position (move it upward)
old_modal_div = """      {/* Manual Search Modal */}
      {manualModalOpen && (
        <div className="fixed inset-0 z-[120] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 animate-fade-in">"""
new_modal_div = """      {/* Manual Search Modal */}
      {manualModalOpen && (
        <div className="fixed inset-0 z-[120] bg-black/80 backdrop-blur-sm flex items-start pt-[10vh] justify-center p-4 animate-fade-in">"""
scanner = scanner.replace(old_modal_div, new_modal_div)


with open('components/ScannerTab.tsx', 'w', encoding='utf-8') as f:
    f.write(scanner)

print("Done")
