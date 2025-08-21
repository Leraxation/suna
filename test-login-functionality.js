// Test script to specifically test login functionality
const { createClient } = require('./frontend/node_modules/@supabase/supabase-js');
require('./frontend/node_modules/dotenv').config({ path: './frontend/.env.local' });

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

console.log('🔐 Testing Login Functionality...');

const supabase = createClient(supabaseUrl, supabaseKey);

async function testLoginFlow() {
  try {
    // Test 1: Check if auth service is accessible
    console.log('\n1️⃣ Testing auth service accessibility...');
    const { data: sessionData, error: sessionError } = await supabase.auth.getSession();
    
    if (sessionError) {
      console.log('❌ Auth service error:', sessionError.message);
      return;
    } else {
      console.log('✅ Auth service is accessible');
      console.log('Current session:', sessionData.session ? 'Active' : 'None');
    }
    
    // Test 2: Try to sign up with a valid email format
    console.log('\n2️⃣ Testing signup with valid email...');
    const testEmail = 'testuser@gmail.com';
    const testPassword = 'testpassword123';
    
    const { data: signUpData, error: signUpError } = await supabase.auth.signUp({
      email: testEmail,
      password: testPassword,
    });
    
    if (signUpError) {
      console.log('❌ Signup failed:', signUpError.message);
      
      // Check for specific error types
      if (signUpError.message.includes('User already registered')) {
        console.log('ℹ️  User already exists - trying login instead...');
        
        // Test 3: Try login with existing user
        console.log('\n3️⃣ Testing login with existing credentials...');
        const { data: signInData, error: signInError } = await supabase.auth.signInWithPassword({
          email: testEmail,
          password: testPassword,
        });
        
        if (signInError) {
          console.log('❌ Login failed:', signInError.message);
          
          // Check for common login issues
          if (signInError.message.includes('Invalid login credentials')) {
            console.log('ℹ️  Invalid credentials - this is expected for test data');
          } else if (signInError.message.includes('Email not confirmed')) {
            console.log('ℹ️  Email not confirmed - check email verification');
          } else if (signInError.message.includes('Too many requests')) {
            console.log('ℹ️  Rate limited - try again later');
          }
        } else {
          console.log('✅ Login successful!');
          console.log('User ID:', signInData.user?.id);
          console.log('Email:', signInData.user?.email);
          console.log('Email confirmed:', signInData.user?.email_confirmed_at ? 'Yes' : 'No');
          
          // Test 4: Sign out
          console.log('\n4️⃣ Testing sign out...');
          const { error: signOutError } = await supabase.auth.signOut();
          
          if (signOutError) {
            console.log('❌ Sign out failed:', signOutError.message);
          } else {
            console.log('✅ Sign out successful');
          }
        }
      } else if (signUpError.message.includes('Signup is disabled')) {
        console.log('❌ Signup is disabled in Supabase project settings');
      } else if (signUpError.message.includes('Invalid API key')) {
        console.log('❌ Invalid API key - check SUPABASE_ANON_KEY');
      }
    } else {
      console.log('✅ Signup successful!');
      console.log('User created:', signUpData.user ? 'Yes' : 'No');
      console.log('Session created:', signUpData.session ? 'Yes' : 'No');
      console.log('Email confirmation required:', !signUpData.session);
    }
    
    // Test 5: Check project settings
    console.log('\n5️⃣ Checking project configuration...');
    
    // Try to access a protected resource to test RLS
    const { data: protectedData, error: protectedError } = await supabase
      .from('profiles')
      .select('*')
      .limit(1);
    
    if (protectedError) {
      if (protectedError.message.includes('relation "profiles" does not exist')) {
        console.log('ℹ️  Profiles table does not exist - this might be expected');
      } else if (protectedError.message.includes('permission denied')) {
        console.log('ℹ️  RLS is enabled and working (permission denied without auth)');
      } else {
        console.log('❌ Database error:', protectedError.message);
      }
    } else {
      console.log('✅ Database accessible');
    }
    
  } catch (error) {
    console.error('❌ Unexpected error:', error.message);
  }
}

// Test 6: Check environment variables
console.log('\n6️⃣ Environment Variables Check:');
console.log('NEXT_PUBLIC_SUPABASE_URL:', supabaseUrl ? '✅ Set' : '❌ Missing');
console.log('NEXT_PUBLIC_SUPABASE_ANON_KEY:', supabaseKey ? '✅ Set' : '❌ Missing');
console.log('NEXT_PUBLIC_BACKEND_URL:', process.env.NEXT_PUBLIC_BACKEND_URL || '❌ Missing');
console.log('NEXT_PUBLIC_URL:', process.env.NEXT_PUBLIC_URL || '❌ Missing');

testLoginFlow();