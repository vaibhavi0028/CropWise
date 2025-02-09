import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import bg from "../assets/landingbg.png";

const Login = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    // Add your authentication logic here
    // For now, we'll just navigate to dashboard
    navigate("/dashboard");
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const tabs = [
    { id: "home", label: "HOME" },
    { id: "services", label: "SERVICES" },
    { id: "about", label: "ABOUT US" },
    { id: "contact", label: "CONTACT" },
    { id: "login", label: "LOGIN" },
  ];

  return (
    <div className="relative min-h-screen font-orbitron">
      <div className="fixed inset-0 w-full h-screen bg-cover bg-center bg-fixed z-0" style={{ backgroundImage: `url(${bg})` }}></div>
      
      <nav className="relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-center h-16">
            <div className="flex space-x-8">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  className={`px-4 py-2 rounded-lg transition-all duration-300 font-bold ${
                    tab.id === "login"
                      ? "bg-gradient-to-r from-green-500 to-green-700 text-white"
                      : "text-gray-300 hover:text-white"
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </nav>

      <main className="relative z-10 flex items-center justify-center min-h-[calc(100vh-4rem)]">
        <div className="w-full max-w-md p-8 rounded-2xl bg-white/10 backdrop-blur-md">
          <h2 className="text-3xl font-bold text-center mb-8 text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-300">
            Welcome Back
          </h2>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-gray-300 mb-2" htmlFor="email">
                Email
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white focus:outline-none focus:border-green-500 backdrop-blur-md"
                required
              />
            </div>
            <div>
              <label className="block text-gray-300 mb-2" htmlFor="password">
                Password
              </label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white focus:outline-none focus:border-green-500 backdrop-blur-md"
                required
              />
            </div>
            <button
              type="submit"
              className="w-full px-8 py-3 rounded-lg bg-gradient-to-r from-[#7ED473] to-[#2F7240] text-white font-semibold hover:opacity-90 transition-opacity"
            >
              Sign In
            </button>
          </form>
        </div>
      </main>
    </div>
  );
};

export default Login;