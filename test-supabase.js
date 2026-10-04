const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://rcsjwdtatnqodekwqpur.supabase.co';
const supabaseKey = 'sb_publishable_oczVf9MN6xKzfYNcIy37uQ_4V0Y4mE0';

const supabase = createClient(supabaseUrl, supabaseKey);

async function test() {
  const { data, error } = await supabase.from('employees').select('*').limit(1);
  if (error) {
    console.error("Error:", error);
  } else {
    console.log("Success! Data:", data);
  }
}

test();
