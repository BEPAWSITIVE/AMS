import os

with open('components/ReportsTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add Search state and Employee state
old_states = """  const [loading, setLoading] = useState(true);
  const [selectedMonth, setSelectedMonth] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("Staff");"""
new_states = """  const [loading, setLoading] = useState(true);
  const [selectedMonth, setSelectedMonth] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("Staff");
  const [searchQuery, setSearchQuery] = useState("");
  const [employeesMap, setEmployeesMap] = useState<Record<string, any>>({});"""
code = code.replace(old_states, new_states)

# 2. Update useEffect to fetch employees
old_effect = """  useEffect(() => {
    const now = new Date();
    const yyyy = now.getFullYear();
    const mm = String(now.getMonth() + 1).padStart(2, '0');
    setSelectedMonth(`${yyyy}-${mm}`);

    if (navigator.onLine) {
      supabase.from('attendance').select('*').order('inTimestamp', { ascending: false })
        .then(({ data }) => {
          if (data) setLogs(data);
          setLoading(false);
        });
    } else {
      const cached = localStorage.getItem('cached_logs');
      if (cached) setLogs(JSON.parse(cached));
      setLoading(false);
    }
  }, []);"""

new_effect = """  useEffect(() => {
    const now = new Date();
    const yyyy = now.getFullYear();
    const mm = String(now.getMonth() + 1).padStart(2, '0');
    setSelectedMonth(`${yyyy}-${mm}`);

    const loadData = async () => {
      if (navigator.onLine) {
        // Fetch employees to get phone numbers and plates
        const { data: emps } = await supabase.from('employees').select('*');
        if (emps) {
          const eMap: Record<string, any> = {};
          emps.forEach(e => eMap[e.empId] = e);
          setEmployeesMap(eMap);
        }

        const { data } = await supabase.from('attendance').select('*').order('inTimestamp', { ascending: false });
        if (data) setLogs(data);
      } else {
        const cached = localStorage.getItem('cached_logs');
        if (cached) setLogs(JSON.parse(cached));
        const cachedE = localStorage.getItem('cached_employees');
        if (cachedE) {
          const emps = JSON.parse(cachedE);
          const eMap: Record<string, any> = {};
          emps.forEach((e: any) => eMap[e.empId] = e);
          setEmployeesMap(eMap);
        }
      }
      setLoading(false);
    };
    
    loadData();
  }, []);"""
code = code.replace(old_effect, new_effect)

# 3. Join employee data and filter by search query
old_stats_list = """  const statsList = Object.values(employeeStats).map((stat: any) => ({
    ...stat,
    workingDays: stat.daysSet.size,
    totalHoursFormatted: Math.floor(stat.totalHours) + 'h ' + Math.round((stat.totalHours % 1) * 60) + 'm'
  })).sort((a: any, b: any) => b.totalHours - a.totalHours);"""

new_stats_list = """  const statsList = Object.values(employeeStats).map((stat: any) => {
    const empData = employeesMap[stat.empId] || {};
    return {
      ...stat,
      phone: empData.phone || '',
      vehicle_plate: empData.vehicle_plate || '',
      workingDays: stat.daysSet.size,
      totalHoursFormatted: Math.floor(stat.totalHours) + 'h ' + Math.round((stat.totalHours % 1) * 60) + 'm'
    };
  })
  .filter((stat: any) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      stat.name.toLowerCase().includes(q) ||
      stat.empId.toLowerCase().includes(q) ||
      (stat.phone && stat.phone.toLowerCase().includes(q)) ||
      (stat.vehicle_plate && stat.vehicle_plate.toLowerCase().includes(q))
    );
  })
  .sort((a: any, b: any) => b.totalHours - a.totalHours);"""
code = code.replace(old_stats_list, new_stats_list)

# Fix the reduce function to actually include the empId so we can join it!
old_reduce = """    if (!acc[log.empId]) {
      acc[log.empId] = {
        name: log.empName,
        category: log.category || 'Staff',
        daysSet: new Set(),
        totalHours: 0
      };
    }"""
new_reduce = """    if (!acc[log.empId]) {
      acc[log.empId] = {
        empId: log.empId,
        name: log.empName,
        category: log.category || 'Staff',
        daysSet: new Set(),
        totalHours: 0
      };
    }"""
code = code.replace(old_reduce, new_reduce)

# 4. Add Search UI and display the extra data (phone/plate) in the cards
# And import Search icon from lucide-react
code = code.replace('from "lucide-react";', ', Search } from "lucide-react";')

old_ui = """      <div className="flex space-x-2 overflow-x-auto pb-2 scrollbar-hide">
        {['Staff', 'Volunteer', 'Workexchange', 'Vehicle', 'Visitor', 'All'].map(cat => (
          <button"""

new_ui = """      <div className="relative mb-4">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search size={18} className="text-gray-400" />
        </div>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search by Name, ID, Phone, or Plate..."
          className="w-full bg-white border border-gray-200 pl-10 p-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 text-sm shadow-sm"
        />
      </div>

      <div className="flex space-x-2 overflow-x-auto pb-2 scrollbar-hide">
        {['Staff', 'Volunteer', 'Workexchange', 'Vehicle', 'Visitor', 'All'].map(cat => (
          <button"""
code = code.replace(old_ui, new_ui)

# Update the card to show Phone / Plate
old_card = """                  <div>
                    <h4 className="font-bold text-gray-800">{stat.name}</h4>
                    <span className="text-[10px] uppercase font-bold text-blue-500 bg-blue-50 px-2 py-0.5 rounded-md">
                      {stat.category}
                    </span>
                  </div>"""

new_card = """                  <div>
                    <h4 className="font-bold text-gray-800">{stat.name}</h4>
                    <div className="flex items-center space-x-2 mt-0.5">
                      <span className="text-[10px] uppercase font-bold text-blue-500 bg-blue-50 px-2 py-0.5 rounded-md">
                        {stat.category}
                      </span>
                      {stat.phone && <span className="text-[10px] text-gray-500 font-mono">{stat.phone}</span>}
                      {stat.vehicle_plate && <span className="text-[10px] text-gray-500 font-mono">{stat.vehicle_plate}</span>}
                    </div>
                  </div>"""
code = code.replace(old_card, new_card)

with open('components/ReportsTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
