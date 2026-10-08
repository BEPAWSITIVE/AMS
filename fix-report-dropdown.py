import os

with open('components/ReportsTab.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

old_ui = """      <div className="flex space-x-2 overflow-x-auto pb-2 scrollbar-hide">
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
      </div>"""

new_ui = """      <div className="flex justify-end mb-4">
        <div className="relative w-1/2">
          <select 
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="appearance-none w-full bg-gray-50 text-gray-700 font-bold py-2 pl-3 pr-8 rounded-xl border border-gray-200 outline-none focus:ring-2 focus:ring-blue-500 text-sm cursor-pointer"
          >
            <option value="All">All Categories</option>
            <option value="Staff">Staff</option>
            <option value="Volunteer">Volunteer</option>
            <option value="Workexchange">Work Exchange</option>
            <option value="Vehicle">Vehicle</option>
            <option value="Visitor">Visitor</option>
          </select>
          <ChevronDown size={14} className="absolute right-3 top-3 text-gray-500 pointer-events-none" />
        </div>
      </div>"""

code = code.replace(old_ui, new_ui)

with open('components/ReportsTab.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Done")
