import psycopg2

conn_str = "postgresql://postgres:AMS@SUPABASE@db.rcsjwdtatnqodekwqpur.supabase.co:5432/postgres"

# Wait, if the password contains '@', the parsing might break. Let's encode the '@' in the password as '%40'
# However, the user provided it as [AMS@SUPABASE]. The password is AMS@SUPABASE.
encoded_conn_str = "postgresql://postgres:AMS%40SUPABASE@db.rcsjwdtatnqodekwqpur.supabase.co:5432/postgres"

sql_commands = """
-- 1. Create Employees Table
CREATE TABLE IF NOT EXISTS public.employees (
  "empId" text PRIMARY KEY,
  "name" text NOT NULL,
  "department" text,
  "phone" text,
  "createdAt" timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Create Attendance Table
CREATE TABLE IF NOT EXISTS public.attendance (
  "recordId" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "empId" text REFERENCES public.employees("empId") ON DELETE CASCADE,
  "empName" text NOT NULL,
  "department" text,
  "date" text NOT NULL,
  "inTime" text NOT NULL,
  "inTimestamp" bigint NOT NULL,
  "outTime" text,
  "outTimestamp" bigint,
  "totalHours" text,
  "status" text NOT NULL,
  "isSynced" smallint DEFAULT 1,
  "updatedAt" timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Set up Row Level Security (RLS) policies
ALTER TABLE public.employees ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.attendance ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (to avoid errors if run multiple times)
DROP POLICY IF EXISTS "Allow public all on employees" ON public.employees;
DROP POLICY IF EXISTS "Allow public all on attendance" ON public.attendance;

CREATE POLICY "Allow public all on employees" ON public.employees FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public all on attendance" ON public.attendance FOR ALL USING (true) WITH CHECK (true);
"""

try:
    conn = psycopg2.connect(encoded_conn_str)
    cur = conn.cursor()
    cur.execute(sql_commands)
    conn.commit()
    cur.close()
    conn.close()
    print("SUCCESS")
except Exception as e:
    print("ERROR:", e)
