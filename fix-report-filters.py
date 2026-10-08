import os

with open('components/ReportsTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add selectedCategory state
old_states = """  const [loading, setLoading] = useState(true);
  const [selectedMonth, setSelectedMonth] = useState("");"""

new_states = """  const [loading, setLoading] = useState(true);
  const [selectedMonth, setSelectedMonth] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("Staff");"""
code = code.replace(old_states, new_states)

# 2. Filter logs by category and month
old_filter = """  const filteredLogs = logs.filter(l => l.date.startsWith(selectedMonth));"""
new_filter = """  const filteredLogs = logs.filter(l => {
    if (!l.date.startsWith(selectedMonth)) return false;
    if (l.category === 'Parcel') return false;
    
    const cat = l.category || 'Staff';
    if (selectedCategory === 'All') return true;
    return cat === selectedCategory;
  });"""
code = code.replace(old_filter, new_filter)

# 3. Remove hardcoded Vehicle ignore
old_reduce = """  const employeeStats = filteredLogs.reduce((acc: any, log: AttendanceRecord) => {
    if (log.category === 'Vehicle' || log.category === 'Parcel') return acc;
    
    if (!acc[log.empId]) {"""
new_reduce = """  const employeeStats = filteredLogs.reduce((acc: any, log: AttendanceRecord) => {
    if (!acc[log.empId]) {"""
code = code.replace(old_reduce, new_reduce)

# 4. Add Category selector UI
old_ui = """        <div className="relative">
          <select 
            value={selectedMonth}
            onChange={(e) => setSelectedMonth(e.target.value)}
            className="appearance-none bg-blue-50 text-blue-700 font-bold py-2 pl-3 pr-8 rounded-xl border border-blue-100 outline-none focus:ring-2 focus:ring-blue-500 text-sm cursor-pointer"
          >
            {availableMonths.map(m => (
              <option key={m} value={m}>{formatMonthName(m)}</option>
            ))}
          </select>
          <ChevronDown size={14} className="absolute right-3 top-3 text-blue-500 pointer-events-none" />
        </div>
      </div>

      {loading ?"""

new_ui = """        <div className="relative">
          <select 
            value={selectedMonth}
            onChange={(e) => setSelectedMonth(e.target.value)}
            className="appearance-none bg-blue-50 text-blue-700 font-bold py-2 pl-3 pr-8 rounded-xl border border-blue-100 outline-none focus:ring-2 focus:ring-blue-500 text-sm cursor-pointer"
          >
            {availableMonths.map(m => (
              <option key={m} value={m}>{formatMonthName(m)}</option>
            ))}
          </select>
          <ChevronDown size={14} className="absolute right-3 top-3 text-blue-500 pointer-events-none" />
        </div>
      </div>

      <div className="flex space-x-2 overflow-x-auto pb-2 scrollbar-hide">
        {['Staff', 'Volunteer', 'Workexchange', 'Vehicle', 'Visitor', 'All'].map(cat => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`whitespace-nowrap px-4 py-1.5 rounded-full text-xs font-bold transition-colors ${
              selectedCategory === cat 
                ? 'bg-gray-800 text-white' 
                : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {loading ?"""
code = code.replace(old_ui, new_ui)


with open('components/ReportsTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
