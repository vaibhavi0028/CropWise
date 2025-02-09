import React, { useState, useEffect } from "react";
import {
  Home,
  Settings,
  Sprout,
  BarChart3,
  Languages,
  AlertTriangle,
  Leaf,
  CloudRain,
  Sun,
  Users,
  FileText,
  Droplets,
  Flame,
  Waves,
  X,
} from "lucide-react";
import onSVG from "../assets/on.png";
import offSVG from "../assets/off.png";
import bg1 from "../assets/bg1.png";
import bg2 from "../assets/bg2.png";
import axios from "axios";
import { Line } from "react-chartjs-2";
import { Chart, registerables } from "chart.js";

Chart.register(...registerables);

function Dashboard() {
  const [weatherData, setWeatherData] = useState(null);
  const [latestWeather, setLatestWeather] = useState({
    temperature: "Loading...",
    rainfall: "Loading...",
  });
  const [data, setData] = useState([]);
  const [, setError] = useState(null);
  const [states, setStates] = useState({
    nitrogen: false,
    phosphorus: false,
    potassium: false,
    waterPump: false,
  });
  const [notification, setNotification] = useState({
    show: false,
    message: "",
  });

  const translations = {
    english: {
      title: "CROPWISE",
      nav: {
        crop: "Crop",
        finance: "Finance",
        resources: "Resources",
      },
      sidebar: {
        home: "Home",
        settings: "Settings",
        crops: "Crops",
        analytics: "Analytics",
        team: "Team",
        reports: "Reports",
        alerts: "Alerts",
      },
      soilHealth: {
        title: "Current Soil Health",
        nitrogen: "Nitrogen",
        phosphorous: "Phosphorous",
        potassium: "Potassium",
        moisture: "Moisture",
        ph: "pH",
        humidity: "Humidity",
      },
      finance: {
        title: "Finance Details",
        investment: "Investment",
        marketPrice: "Current Market Price",
        expectedProfit: "Expected Profit",
        paymentDues: "Upcoming Payment Dues",
        loanStatus: "Loan Status",
      },
      yieldPrediction: {
        title: "Yield Prediction",
        predictedYield: "Predicted Yield",
        weatherImpact: "Weather Impact",
        harvestTime: "Expected Harvest Time",
        pestRisk: "Pest Risk",
        diseaseRisk: "Disease Risk",
      },
      weather: {
        title: "Weather",
        temperature: "Temperature",
        rainfall: "Rainfall",
      },
      bestCrops: {
        title: "Best Crop Predictions",
        season: "Season",
        avgPrice: "Avg. Price",
        growthPeriod: "Growth Period",
      },
      controls: {
        nitrogen: "Nitrogen",
        phosphorus: "Phosphorus",
        potassium: "Potassium",
        pump: "Pump",
      },
      best: {
        winter: "Winter",
        summer: "Summer",
        month: "Month",
        kg: "kg",
      },
    },
    hindi: {
      title: "CROPWISE",
      nav: {
        crop: "फसल",
        finance: "वित्त",
        resources: "संसाधन",
      },
      sidebar: {
        home: "होम",
        settings: "सेटिंग्स",
        crops: "फसलें",
        analytics: "विश्लेषण",
        team: "टीम",
        reports: "रिपोर्ट",
        alerts: "अलर्ट",
      },
      soilHealth: {
        title: "वर्तमान मिट्टी स्वास्थ्य",
        nitrogen: "नाइट्रोजन",
        phosphorous: "फास्फोरस",
        potassium: "पोटैशियम",
        moisture: "नमी",
        ph: "पीएच",
        humidity: "आर्द्रता",
      },
      finance: {
        title: "वित्तीय विवरण",
        investment: "निवेश",
        marketPrice: "वर्तमान बाजार मूल्य",
        expectedProfit: "अपेक्षित लाभ",
        paymentDues: "आगामी भुगतान",
        loanStatus: "ऋण स्थिति",
      },
      yieldPrediction: {
        title: "उपज पूर्वानुमान",
        predictedYield: "अनुमानित उपज",
        weatherImpact: "मौसम प्रभाव",
        harvestTime: "अपेक्षित कटाई समय",
        pestRisk: "कीट जोखिम",
        diseaseRisk: "रोग जोखिम",
      },
      weather: {
        title: "मौसम",
        temperature: "तापमान",
        rainfall: "वर्षा",
      },
      bestCrops: {
        title: "सर्वोत्तम फसल पूर्वानुमान",
        season: "मौसम",
        avgPrice: "औसत मूल्य",
        growthPeriod: "विकास अवधि",
      },
      controls: {
        nitrogen: "नाइट्रोजन",
        phosphorus: "फास्फोरस",
        potassium: "पोटैशियम",
        pump: "पंप",
      },
      best: {
        winter: "सर्दी",
        summer: "गर्मी",
        month: "महीना",
        kg: "किलो",
      },
    },
  };

  const [language, setLanguage] = useState("english");
  const t = translations[language];

  const toggleLanguage = () => {
    setLanguage((prev) => (prev === "english" ? "hindi" : "english"));
  };

  const toggleState = (key) => {
    setStates((prev) => {
      const newState = { ...prev, [key]: !prev[key] };
      if (key === "waterPump") {
        const isActive = newState[key];
        const message = isActive
          ? "Water pump has been activated"
          : "Water pump has been deactivated";
        const colorClass = isActive ? "text-emerald-700" : "text-red-700";
        const bgClass = isActive ? "bg-emerald-100 border-emerald-500 " : "bg-red-100 border-red-500 ";

        setNotification({ show: true, message, colorClass, bgClass });
        setTimeout(() => {
          setNotification({
            show: false,
            message: "",
            colorClass: "",
            bgClass: "",
          });
        }, 5000);
      }
      return newState;
    });
  };
  useEffect(() => {
    axios
      .get("http://localhost:5000/data")
      .then((response) => setData(response.data))
      .catch((error) => setError("Error fetching data"));
    navigator.geolocation.getCurrentPosition(async (position) => {
      const { latitude, longitude } = position.coords;
      const apiKey = "78c696cf35b214e2991f0c2752ea599d";
      const url = `https://api.openweathermap.org/data/2.5/forecast?lat=${latitude}&lon=${longitude}&units=metric&appid=${apiKey}`;

      try {
        const response = await fetch(url);
        const data = await response.json();
        const weatherPoints = data.list.slice(0, 5).map((item) => ({
          time: new Date(item.dt * 1000).toLocaleTimeString(),
          temp: item.main.temp,
          rain: item.rain ? item.rain["3h"] || 0 : 0,
        }));
        setWeatherData(weatherPoints);

        const latestTemp = data.list[0].main.temp;
        const latestRain = data.list[0].rain ? data.list[0].rain["3h"] || 0 : 0;
        setLatestWeather({
          temperature: `${latestTemp}°C`,
          rainfall: `${latestRain} mm`,
        });
      } catch (error) {
        console.error("Error fetching weather data:", error);
      }
    });
  }, []);

  const weatherChartData = weatherData
    ? {
        labels: weatherData.map((point) => point.time),
        datasets: [
          {
            label: t.weather.temperature,
            data: weatherData.map((point) => point.temp),
            borderColor: "#ca0b0b",
            fill: false,
          },
          {
            label: t.weather.rainfall,
            data: weatherData.map((point) => point.rain),
            borderColor: "#071a60",
            fill: false,
          },
        ],
      }
    : null;

  const dashboardData = {
    soilHealth: {
      title: t.soilHealth.title,
      data: {
        [t.soilHealth.nitrogen]: data.nitrogen + "%",
        [t.soilHealth.phosphorous]: data.phosphorus + "%",
        [t.soilHealth.potassium]: data.potassium + "%",
        [t.soilHealth.moisture]: data.soil_moisture + "%",
        [t.soilHealth.ph]: data.pH + "%",
        [t.soilHealth.humidity]: data.humidity + "%",
      },
    },
    finance: {
      title: t.finance.title,
      data: {
        [t.finance.investment]: "₹10000",
        [t.finance.marketPrice]: "₹2400/ton",
        [t.finance.expectedProfit]: "₹16000",
        [t.finance.paymentDues]: "₹4000",
        [t.finance.loanStatus]: "Pending",
      },
    },
    yieldPrediction: {
      title: t.yieldPrediction.title,
      data: {
        [t.yieldPrediction.predictedYield]: "1500 kg",
        [t.yieldPrediction.weatherImpact]: "Moderate",
        [t.yieldPrediction.harvestTime]: "3 months",
        [t.yieldPrediction.pestRisk]: "Low",
        [t.yieldPrediction.diseaseRisk]: "Medium",
      },
    },
    weather: {
      title: t.weather.title,
      temperature: "30°C",
      rainfall: "5mm",
    },
    bestCrops: {
      title: t.bestCrops.title,
      table: [
        {
          season: t.best.winter,
          price: "₹50/" + t.best.kg,
          growth: "3 " + t.best.month,
        },
        {
          season: t.best.summer,
          price: "₹45/" + t.best.kg,
          growth: "2.5 " + t.best.month,
        },
      ],
    },
  };

  return (
    <div className="relative min-h-screen overflow font-orbitron">
      {notification.show && (
        <div className="fixed top-4 right-4 z-50 animate-fade-in">
          <div
            className={`border-l-4 text-emerald-700 p-4 rounded shadow-lg flex items-center justify-between min-w-[300px] ${notification.bgClass}`}
          >
            <h3
              className={`font-orbitron font-semibold ${notification.colorClass}`}
            >
              {notification.message}
            </h3>
            <button
              onClick={() =>
                setNotification({ show: false, message: "", colorClass: "" })
              }
              className={`ml-4 text-emerald-600 hover:text-emerald-800 transition-colors ${notification.colorClass}`}
            >
              <X size={20} />
            </button>
          </div>
        </div>
      )}
      <div
        className="fixed inset-0 w-full h-screen bg-cover bg-center bg-fixed z-0"
        style={{ backgroundImage: `url(${bg1})` }}
      >
        <div className="absolute inset-0 bg-white/70"></div>
      </div>

      <div className="relative z-10 h-screen flex flex-col">
        <nav className="flex justify-between items-center p-4 lg:px-6">
          <h1 className="text-2xl font-bold">{t.title}</h1>
          <div className="hidden md:flex gap-4">
            <button className="glassmorphism px-6 py-2 rounded-lg">
              {t.nav.crop}
            </button>
            <button className="glassmorphism px-6 py-2 rounded-lg">
              {t.nav.finance}
            </button>
            <button className="glassmorphism px-6 py-2 rounded-lg">
              {t.nav.resources}
            </button>
          </div>
          <div className="flex gap-4">
            <div className="glassmorphism p-3 rounded-[50%]">
              <Leaf className="w-6 h-6" />
            </div>
            <div className="glassmorphism p-3 rounded-[50%]">
              <BarChart3 className="w-6 h-6" />
            </div>
            <div
              className="glassmorphism p-3 rounded-[50%] cursor-pointer"
              onClick={toggleLanguage}
            >
              <Languages className="w-6 h-6" />
            </div>
          </div>
        </nav>

        <div className="flex flex-1 h-[calc(100vh-5rem)] overflow-hidden">
          <aside className="w-20 h-fit flex flex-col items-center py-8 gap-8 glassmorphism rounded-3xl self-center">
            {[
              { icon: Home, label: t.sidebar.home },
              { icon: Settings, label: t.sidebar.settings },
              { icon: Sprout, label: t.sidebar.crops },
              { icon: BarChart3, label: t.sidebar.analytics },
              { icon: Users, label: t.sidebar.team },
              { icon: FileText, label: t.sidebar.reports },
              { icon: AlertTriangle, label: t.sidebar.alerts },
            ].map((item, index) => (
              <div
                key={index}
                className="flex flex-col items-center gap-1 cursor-pointer"
              >
                <item.icon className="w-6 h-6" />
                <span className="text-xs">{item.label}</span>
              </div>
            ))}
          </aside>

          <div className="flex-1 p-6 pt-1 flex gap-6 overflow-hidden">
            <div className="w-full md:w-1/3 flex flex-col gap-2">
              <div className="flex-1 glassmorphism rounded-xl px-6 py-2 flex flex-col justify-center">
                <h2 className="text-xl font-semibold mb-2">
                  {dashboardData.soilHealth.title}
                </h2>
                <div className="space-y-0 text-base">
                  {Object.entries(dashboardData.soilHealth.data).map(
                    ([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span>{key}:</span>
                        <span className="font-medium">{value}</span>
                      </div>
                    )
                  )}
                </div>
              </div>

              <div className="flex-1 glassmorphism rounded-xl px-6 py-3 flex flex-col justify-center">
                <h2 className="text-xl font-semibold mb-2">
                  {dashboardData.finance.title}
                </h2>
                <div className="space-y-0 text-base">
                  {Object.entries(dashboardData.finance.data).map(
                    ([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span>{key}:</span>
                        <span className="font-medium">{value}</span>
                      </div>
                    )
                  )}
                </div>
              </div>

              <div className="flex-1 glassmorphism rounded-xl px-6 py-3 flex flex-col justify-center">
                <h2 className="text-xl font-semibold mb-2">
                  {dashboardData.yieldPrediction.title}
                </h2>
                <div className="space-y-0 text-base">
                  {Object.entries(dashboardData.yieldPrediction.data).map(
                    ([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span>{key}:</span>
                        <span className="font-medium">{value}</span>
                      </div>
                    )
                  )}
                </div>
              </div>
            </div>

            <div className="hidden md:flex md:w-2/3 flex-col gap-6">
              <div className="hidden h-[56%] md:flex md:w-[100%] flex-row gap-6">
                <div
                  className="bg-cover bg-center rounded-lg h-[100%] w-[70%]"
                  style={{ backgroundImage: `url(${bg2})` }}
                ></div>
                <div className="flex flex-col h-[100%] w-[30%] gap-3">
                  <div className="flex gap-3 h-[50%] w-[100%]">
                    <div className="flex-1 w-1/2 glassmorphism rounded-xl p-6 flex flex-col items-center justify-center">
                      <Leaf size={40} color="#7ED473" />
                      <p className="text-lg font-semibold mt-2">
                        {t.controls.nitrogen}
                      </p>
                      <button
                        onClick={() => toggleState("nitrogen")}
                        className="mt-4 px-6 py-2 rounded-lg text-white font-semibold transition-all scale-105"
                      >
                        <img
                          src={states.nitrogen ? onSVG : offSVG}
                          alt="toggle"
                          className="w-6 inline-block mr-2"
                        />
                      </button>
                    </div>

                    <div className="flex-1 w-1/2 glassmorphism rounded-xl p-6 flex flex-col items-center justify-center">
                      <Flame size={40} color="#FFA500" />
                      <p className="text-lg font-semibold mt-2">
                        {t.controls.phosphorus}
                      </p>
                      <button
                        onClick={() => toggleState("phosphorus")}
                        className="mt-4 px-6 py-2 rounded-lg text-white font-semibold transition-all scale-105"
                      >
                        <img
                          src={states.phosphorus ? onSVG : offSVG}
                          alt="toggle"
                          className="w-6 inline-block mr-2"
                        />
                      </button>
                    </div>
                  </div>

                  <div className="flex gap-3 h-[50%] w-[100%]">
                    <div className="flex-1 w-1/2 glassmorphism rounded-xl p-6 flex flex-col items-center justify-center">
                      <Droplets size={40} color="#1E90FF" />
                      <p className="text-lg font-semibold mt-2">
                        {t.controls.potassium}
                      </p>
                      <button
                        onClick={() => toggleState("potassium")}
                        className="mt-4 px-6 py-2 rounded-lg text-white font-semibold transition-all scale-105"
                      >
                        <img
                          src={states.potassium ? onSVG : offSVG}
                          alt="toggle"
                          className="w-6 inline-block mr-2"
                        />
                      </button>
                    </div>

                    <div className="flex-1 w-1/2 glassmorphism rounded-xl p-6 flex flex-col items-center justify-center">
                      <Waves size={40} color="#00CED1" />
                      <p className="text-lg font-semibold mt-2">
                        {t.controls.pump}
                      </p>
                      <button
                        onClick={() => toggleState("waterPump")}
                        className="mt-4 px-6 py-2 rounded-lg text-white font-semibold transition-all scale-105"
                      >
                        <img
                          src={states.waterPump ? onSVG : offSVG}
                          alt="toggle"
                          className="w-6 inline-block mr-2"
                        />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              <div className="flex gap-6 h-[40%]">
                <div className="flex-1 glassmorphism rounded-xl p-6">
                  <div className="flex flex-row items-center gap-10 mb-3">
                    <h2 className="text-xl font-semibold">
                      {dashboardData.weather.title}
                    </h2>
                    <div className="flex flex-row items-center gap-10">
                      <div className="flex items-center gap-2">
                        <Sun className="w-6 h-6" />
                        <span>{latestWeather.temperature}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <CloudRain className="w-6 h-6" />
                        <span>{latestWeather.rainfall}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex h-[91%] items-center justify-center">
                    {weatherChartData ? (
                      <Line data={weatherChartData} />
                    ) : (
                      <p>Loading weather data...</p>
                    )}
                  </div>
                </div>

                <div className="flex-1 glassmorphism rounded-xl px-6 py-3">
                  <h2 className="text-xl font-semibold mb-3">
                    {dashboardData.bestCrops.title}
                  </h2>
                  <table className="w-full mb-2">
                    <thead>
                      <tr className="text-left">
                        <th className="pb-0.5">{t.bestCrops.season}</th>
                        <th className="pb-0.5">{t.bestCrops.avgPrice}</th>
                        <th className="pb-0.5">{t.bestCrops.growthPeriod}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {dashboardData.bestCrops.table.map((row, index) => (
                        <tr key={index}>
                          <td className="py-0">{row.season}</td>
                          <td className="py-0">{row.price}</td>
                          <td className="py-0">{row.growth}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  <div className="flex gap-4 my-1">
                    <img
                      src="https://images.unsplash.com/photo-1528821128474-27f963b062bf?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80"
                      alt="Cherry"
                      className="w-1/3 h-20 object-cover rounded-lg"
                    />
                    <img
                      src="https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80"
                      alt="Apple"
                      className="w-1/3 h-20 object-cover rounded-lg"
                    />
                    <img
                      src="https://images.unsplash.com/photo-1595743825637-cdafc8ad4173?ixlib=rb-4.0.3&auto=format&fit=crop&w=300&q=80"
                      alt="Peach"
                      className="w-1/3 h-20 object-cover rounded-lg"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
