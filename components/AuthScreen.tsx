"use client";
import { useState, useEffect } from "react";
import { supabase } from "@/lib/supabase";
import { Lock, Mail, ArrowRight, Eye, EyeOff, Loader2 } from "lucide-react";
import Image from "next/image";

export default function AuthScreen() {
  const [view, setView] = useState<'login' | 'signup' | 'forgot' | 'update'>('login');
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    // Check if we just clicked a password reset link
    const checkHash = () => {
      const hash = window.location.hash;
      if (hash && hash.includes("type=recovery")) {
        setView("update");
      }
    };
    checkHash();
    
    const { data: authListener } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (event === "PASSWORD_RECOVERY") {
        setView("update");
      }
    });
    
    return () => {
      authListener.subscription.unsubscribe();
    };
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setError(""); setSuccess("");
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) setError(error.message);
    setLoading(false);
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setError(""); setSuccess("");
    const { error } = await supabase.auth.signUp({ email, password });
    if (error) setError(error.message);
    else setSuccess("Check your email for a confirmation link!");
    setLoading(false);
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setError(""); setSuccess("");
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: window.location.origin,
    });
    if (error) setError(error.message);
    else setSuccess("Password reset email sent! Check your inbox.");
    setLoading(false);
  };

  const handleUpdatePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setError(""); setSuccess("");
    const { error } = await supabase.auth.updateUser({ password });
    if (error) {
      setError(error.message);
    } else {
      setSuccess("Password updated successfully!");
      setTimeout(() => setView('login'), 2000);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-[#F4F9FF] flex flex-col justify-center px-6 py-12 relative overflow-hidden">
      {/* Decorative Blobs */}
      <div className="absolute top-20 -left-10 w-48 h-48 bg-blue-100 rounded-full opacity-50 z-0"></div>
      <div className="absolute top-40 -right-10 w-56 h-56 bg-green-100 rounded-full opacity-50 z-0"></div>

      <div className="relative z-10 w-full max-w-sm mx-auto">
        <div className="text-center mb-10">
          <div className="w-20 h-20 bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden mx-auto mb-4 flex items-center justify-center">
            <Image src="/logo.jpg" alt="Logo" width={80} height={80} className="object-cover" priority />
          </div>
          <h1 className="text-2xl font-extrabold text-[#1E293B] tracking-tight">Attendance Manager</h1>
          <p className="text-sm font-bold text-gray-400 tracking-wider mt-1">Secure Access Panel</p>
        </div>

        <div className="bg-white p-6 rounded-3xl shadow-xl border border-blue-50/50">
          <h2 className="text-xl font-bold text-gray-800 mb-6 text-center">
            {view === 'login' && 'Welcome Back'}
            {view === 'signup' && 'Create Account'}
            {view === 'forgot' && 'Reset Password'}
            {view === 'update' && 'Set New Password'}
          </h2>

          {error && <div className="bg-red-50 text-red-600 p-3 rounded-xl text-sm font-medium mb-4 text-center">{error}</div>}
          {success && <div className="bg-green-50 text-green-600 p-3 rounded-xl text-sm font-medium mb-4 text-center">{success}</div>}

          <form onSubmit={
            view === 'login' ? handleLogin :
            view === 'signup' ? handleSignup :
            view === 'forgot' ? handleResetPassword :
            handleUpdatePassword
          } className="space-y-4">

            {view !== 'update' && (
              <div>
                <label className="block text-xs font-bold text-gray-500 mb-1 ml-1">Email Address</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-400">
                    <Mail size={18} />
                  </div>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-gray-50 border border-gray-200 pl-11 p-3.5 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 text-sm font-medium transition-all"
                    placeholder="admin@example.com"
                    required
                  />
                </div>
              </div>
            )}

            {view !== 'forgot' && (
              <div>
                <label className="block text-xs font-bold text-gray-500 mb-1 ml-1">Password</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-400">
                    <Lock size={18} />
                  </div>
                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full bg-gray-50 border border-gray-200 pl-11 p-3.5 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 text-sm font-medium transition-all"
                    placeholder="••••••••"
                    required
                    minLength={6}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </div>
            )}

            {view === 'login' && (
              <div className="flex justify-end">
                <button type="button" onClick={() => { setView('forgot'); setError(""); setSuccess(""); }} className="text-xs font-bold text-blue-600 hover:text-blue-800">
                  Forgot Password?
                </button>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-xl font-bold shadow-md flex items-center justify-center transition-colors disabled:opacity-70 mt-2"
            >
              {loading ? <Loader2 size={20} className="animate-spin" /> : (
                <>
                  {view === 'login' ? 'Sign In' : view === 'signup' ? 'Create Account' : view === 'forgot' ? 'Send Reset Link' : 'Save Password'}
                  <ArrowRight size={18} className="ml-2" />
                </>
              )}
            </button>
          </form>

          {view !== 'update' && (
            <div className="mt-6 text-center space-y-2">
              {view === 'login' ? (
                <p className="text-xs text-gray-500 font-medium">
                  Don't have an account? <button onClick={() => { setView('signup'); setError(""); setSuccess(""); }} className="text-blue-600 font-bold hover:underline">Sign up</button>
                </p>
              ) : (
                <p className="text-xs text-gray-500 font-medium">
                  Already have an account? <button onClick={() => { setView('login'); setError(""); setSuccess(""); }} className="text-blue-600 font-bold hover:underline">Sign in</button>
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
