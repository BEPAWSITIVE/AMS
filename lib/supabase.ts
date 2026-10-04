import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://rcsjwdtatnqodekwqpur.supabase.co';
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'sb_publishable_oczVf9MN6xKzfYNcIy37uQ_4V0Y4mE0';

export const supabase = createClient(supabaseUrl, supabaseKey);

// Define types for our tables
export interface Employee {
  empId: string;
  name: string;
  department: string;
  phone?: string;
  createdAt: string;
}

export interface AttendanceRecord {
  recordId: string;
  empId: string;
  empName: string;
  department: string;
  date: string;
  inTime: string;
  inTimestamp: number;
  outTime?: string;
  outTimestamp?: number;
  totalHours?: string;
  status: string; // 'IN' or 'OUT'
  isSynced: number;
  updatedAt: string;
}
