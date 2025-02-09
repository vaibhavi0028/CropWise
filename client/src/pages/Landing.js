import React, { useState } from "react";
import { Sprout, Lightbulb, Tractor } from "lucide-react";
import bg from "../assets/landingbg.png";
import { NavLink } from "react-router-dom";

const Landing = () => {
  const [activeTab, setActiveTab] = useState("home");

  const tabs = [
    { id: "home", label: "HOME" },
    { id: "services", label: "SERVICES" },
    { id: "about", label: "ABOUT US" },
    { id: "contact", label: "CONTACT" },
    { id: "login", label: "LOGIN" },
  ];
  return (
    <div className="relative min-h-screen overflow font-orbitron">
      <div
        className="fixed inset-0 w-full h-screen bg-cover bg-center bg-fixed z-0"
        style={{ backgroundImage: `url(${bg})` }}
      ></div>
      <nav className="relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-center h-16">
            <div className="flex space-x-8">
              {tabs.map((tab) => (
                <NavLink
                  key={tab.id}
                  to={tab.id === "login" ? "/login" : "#"}
                  className={`px-4 py-2 rounded-lg transition-all duration-300 font-bold ${
                    activeTab === tab.id
                      ? "bg-gradient-to-r from-green-500 to-green-700 text-white"
                      : "text-gray-300 hover:text-white"
                  }`}
                  onClick={() => setActiveTab(tab.id)}
                >
                  {tab.label}
                </NavLink>
              ))}
            </div>
          </div>
        </div>
      </nav>

      <main className="relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
          <h1 className="text-6xl mb-[40px] md:text-7xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-300 tracking-wider mb-8 drop-shadow-[0_0_10px_rgba(255,255,255,0.3)]">
            THE FUTURE OF FARMING
          </h1>

          <div className="flex justify-center gap-4 mb-20">
            <NavLink to="/dashboard">
              <button className="px-8 py-3 rounded-lg bg-gradient-to-r from-[#7ED473] to-[#2F7240] text-white font-semibold hover:opacity-90 transition-opacity">
                Get Started
              </button>
            </NavLink>
            <button className="px-8 py-3 rounded-lg bg-white/10 backdrop-blur-sm text-white font-semibold hover:bg-white/20 transition-all">
              Learn More
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-12">
            {[
              {
                icon: <Sprout className="w-12 h-12 text-green-400" />,
                title: "Sustainable Growth",
              },
              {
                icon: <Lightbulb className="w-12 h-12 text-green-400" />,
                title: "Smart Solutions",
              },
              {
                icon: <Tractor className="w-12 h-12 text-green-400" />,
                title: "Modern Equipment",
              },
            ].map((card, index) => (
              <div
                key={index}
                className="p-8 rounded-2xl bg-white/10 backdrop-blur-md hover:bg-white/15 transition-all duration-300 group"
              >
                <div className="flex flex-col items-center gap-4">
                  {card.icon}
                  <h3 className="text-xl font-semibold text-white">
                    {card.title}
                  </h3>
                  <p className="text-gray-300 text-sm">
                    NeuroVerse helps to ease the process the crop rotation and
                    optimize it
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
};

export default Landing;
