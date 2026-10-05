import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "https://rcsjwdtatnqodekwqpur.supabase.co";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "sb_publishable_oczVf9MN6xKzfYNcIy37uQ_4V0Y4mE0";

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export interface Employee {
  empId: string;
  name: string;
  department: string;
  phone?: string;
  createdAt: string;
  category?: string;
  document_url?: string;
  vehicle_plate?: string;
  group_members?: string;
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
  status: string;
  isSynced: number;
  updatedAt: string;
  category?: string;
  driver_name?: string;
  meter_out?: number;
  meter_in?: number;
  location?: string;
}
