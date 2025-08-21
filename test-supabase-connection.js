// Test script to diagnose Supabase connection and authentication issues
const { createClient } = require('./frontend/node_modules/@supabase/supabase-js');
require('./frontend/node_modules/dotenv').config({ path: './frontend/.env.local' });

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

console.log('🔍 Testing Supabase Connection...');
console.log('URL:', supabaseUrl ? '✅ Set' : '❌ Missing');
console.log('Key:', supabaseKey ? '✅ Set' : '❌ Missing');

if (!supabaseUrl || !supabaseKey) {
  console.error('❌ Missing Supabase environment variables');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

async function testConnection() {
  try {
    console.log('\n🔗 Testing basic connection...');
    
    // Test basic connection
    const { data, error } = await supabase.from('profiles').select('count').limit(1);
    
    if (error) {
      console.log('❌ Connection test failed:', error.message);
      
      // Check if it's a table not found error (expected for new projects)
      if (error.message.includes('relation "profiles" does not exist')) {
        console.log('ℹ️  Profiles table not found - this might be expected for a new project');
        
        // Try to test auth instead
        console.log('\n🔐 Testing auth service...');
        const { data: authData, error: authError } = await supabase.auth.getSession();
        
        if (authError) {
          console.log('❌ Auth service error:', authError.message);
        } else {
          console.log('✅ Auth service is accessible');
          console.log('Current session:', authData.session ? 'Active' : 'None');
        }
      }
    } else {
      console.log('✅ Basic connection successful');
    }
    
    // Test auth signup (with a test email)
    console.log('\n🧪 Testing auth signup capability...');
    const testEmail = 'test@example.com';
    const testPassword = 'testpassword123';
    
    const { data: signUpData, error: signUpError } = await supabase.auth.signUp({
      email: testEmail,
      password: testPassword,
    });
    
    if (signUpError) {
      console.log('❌ Signup test failed:', signUpError.message);
      
      // Check for common issues
      if (signUpError.message.includes('Email rate limit exceeded')) {
        console.log('ℹ️  Rate limit - this is normal for testing');
      } else if (signUpError.message.includes('User already registered')) {
        console.log('ℹ️  User exists - signup functionality is working');
      } else if (signUpError.message.includes('Invalid API key')) {
        console.log('❌ Invalid API key - check your SUPABASE_ANON_KEY');
      }
    } else {
      console.log('✅ Signup test successful');
      console.log('User created:', signUpData.user ? 'Yes' : 'No');
      console.log('Email confirmation required:', !signUpData.session);
    }
    
  } catch (error) {
    console.error('❌ Unexpected error:', error.message);
  }
}

testConnection();