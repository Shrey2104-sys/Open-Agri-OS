import React, { createContext, useState, useContext } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { MapContainer, TileLayer, Polygon, Tooltip } from 'react-leaflet';
import { GoogleGenerativeAI } from '@google/generative-ai';
import { LayoutDashboard, Map, Stethoscope, Globe, ArrowRight, Activity, ShieldCheck, Upload, Loader, CheckCircle, AlertTriangle } from 'lucide-react';

// --- LanguageContext ---
const LanguageContext = createContext();

const translations = {
    en: {
        dashboard: "Dashboard",
        scout: "Agri-Scout",
        doctor: "Agri-Doctor",
        welcome: "Welcome to Open-Agri OS",
        subtitle: "Empowering Farmers with AI & Satellite Tech",
        scan_now: "Scan Now",
        explore_map: "Explore Map",
        upload_image: "Upload Plant Image",
        analyzing: "Analyzing...",
        treatment_plan: "Treatment Plan",
        disease_detected: "Disease Detected",
        healthy: "Healthy Plant",
        simulation_mode: "Simulation Mode Active",
        status: "System Status: Online"
    },
    hi: {
        dashboard: "डैशबोर्ड",
        scout: "एग्री-स्काउट",
        doctor: "एग्री-डॉक्टर",
        welcome: "ओपन-एग्री ओएस में आपका स्वागत है",
        subtitle: "एआई और सैटेलाइट तकनीक के साथ किसानों को सशक्त बनाना",
        scan_now: "अभी स्कैन करें",
        explore_map: "नक्शा देखें",
        upload_image: "पौधे की छवि अपलोड करें",
        analyzing: "विश्लेषण कर रहा है...",
        treatment_plan: "उपचार योजना",
        disease_detected: "रोग का पता चला",
        healthy: "स्वस्थ पौधा",
        simulation_mode: "सिमुलेशन मोड सक्रिय",
        status: "सिस्टम स्थिति: ऑनलाइन"
    },
    kn: {
        dashboard: "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
        scout: "ಅಗ್ರಿ-ಸ್ಕೌಟ್",
        doctor: "ಅಗ್ರಿ-ಡಾಕ್ಟರ್",
        welcome: "ಓಪನ್-ಅಗ್ರಿ ಓಎಸ್‌ಗೆ ಸುಸ್ವಾಗತ",
        subtitle: "ಎಐ ಮತ್ತು ಉಪಗ್ರಹ ತಂತ್ರಜ್ಞಾನದೊಂದಿಗೆ ರೈತರನ್ನು ಸಬಲೀಕರಣಗೊಳಿಸುವುದು",
        scan_now: "ಈಗ ಸ್ಕ್ಯಾನ್ ಮಾಡಿ",
        explore_map: "ನಕ್ಷೆಯನ್ನು ಅನ್ವೇಷಿಸಿ",
        upload_image: "ಸಸ್ಯದ ಚಿತ್ರವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",
        analyzing: "ವಿಶ್ಲೇಷಿಸಲಾಗುತ್ತಿದೆ...",
        treatment_plan: "ಚಿಕಿತ್ಸಾ ಯೋಜನೆ",
        disease_detected: "ರೋಗ ಪತ್ತೆಯಾಗಿದೆ",
        healthy: "ಆರೋಗ್ಯಕರ ಸಸ್ಯ",
        simulation_mode: "ಸಿಮ್ಯುಲೇಶನ್ ಮೋಡ್ ಸಕ್ರಿಯವಾಗಿದೆ",
        status: "ಸಿಸ್ಟಮ್ ಸ್ಥಿತಿ: ಆನ್‌ಲೈನ್"
    }
};

const LanguageProvider = ({ children }) => {
    const [language, setLanguage] = useState('en');
    const t = (key) => translations[language][key] || key;
    return (
        <LanguageContext.Provider value={{ language, setLanguage, t }}>
            {children}
        </LanguageContext.Provider>
    );
};

const useLanguage = () => useContext(LanguageContext);

// --- Navbar ---
const Navbar = () => {
    const { language, setLanguage, t } = useLanguage();
    const location = useLocation();
    const isActive = (path) => location.pathname === path ? "bg-green-600 text-white" : "text-gray-300 hover:bg-slate-800";

    return (
        <nav className="bg-slate-900 border-b border-slate-700 p-4 flex justify-between items-center sticky top-0 z-50">
            <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center">
                    <span className="font-bold text-slate-900">OA</span>
                </div>
                <span className="text-xl font-bold bg-gradient-to-r from-green-400 to-blue-500 bg-clip-text text-transparent">
                    Open-Agri OS
                </span>
            </div>
            <div className="flex space-x-4">
                <Link to="/" className={`px-4 py-2 rounded-lg flex items-center space-x-2 transition ${isActive('/')}`}>
                    <LayoutDashboard size={20} />
                    <span>{t('dashboard')}</span>
                </Link>
                <Link to="/scout" className={`px-4 py-2 rounded-lg flex items-center space-x-2 transition ${isActive('/scout')}`}>
                    <Map size={20} />
                    <span>{t('scout')}</span>
                </Link>
                <Link to="/doctor" className={`px-4 py-2 rounded-lg flex items-center space-x-2 transition ${isActive('/doctor')}`}>
                    <Stethoscope size={20} />
                    <span>{t('doctor')}</span>
                </Link>
            </div>
            <div className="flex items-center space-x-2 bg-slate-800 px-3 py-1 rounded-full border border-slate-700">
                <Globe size={16} className="text-gray-400" />
                <select value={language} onChange={(e) => setLanguage(e.target.value)} className="bg-transparent text-sm focus:outline-none text-gray-200 cursor-pointer">
                    <option value="en">English</option>
                    <option value="hi">हिंदी</option>
                    <option value="kn">ಕನ್ನಡ</option>
                </select>
            </div>
        </nav>
    );
};

// --- Dashboard ---
const Dashboard = () => {
    const { t } = useLanguage();
    return (
        <div className="p-8 max-w-7xl mx-auto">
            <header className="mb-12 text-center">
                <h1 className="text-5xl font-bold bg-gradient-to-r from-green-400 to-blue-500 bg-clip-text text-transparent mb-4">
                    {t('welcome')}
                </h1>
                <p className="text-xl text-gray-400">{t('subtitle')}</p>
            </header>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="bg-slate-800 rounded-2xl p-8 border border-slate-700 hover:border-green-500 transition group relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition">
                        <Activity size={120} />
                    </div>
                    <h2 className="text-2xl font-bold mb-4 flex items-center space-x-2">
                        <Activity className="text-green-400" />
                        <span>{t('scout')}</span>
                    </h2>
                    <p className="text-gray-400 mb-6">
                        Monitor crop health using high-resolution satellite imagery. Detect stress areas before they become visible to the naked eye.
                    </p>
                    <Link to="/scout" className="inline-flex items-center space-x-2 bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-semibold transition">
                        <span>{t('explore_map')}</span>
                        <ArrowRight size={20} />
                    </Link>
                </div>
                <div className="bg-slate-800 rounded-2xl p-8 border border-slate-700 hover:border-blue-500 transition group relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition">
                        <ShieldCheck size={120} />
                    </div>
                    <h2 className="text-2xl font-bold mb-4 flex items-center space-x-2">
                        <ShieldCheck className="text-blue-400" />
                        <span>{t('doctor')}</span>
                    </h2>
                    <p className="text-gray-400 mb-6">
                        Instant plant disease diagnosis using Gen-AI. Upload a photo and get an organic treatment plan in your local language.
                    </p>
                    <Link to="/doctor" className="inline-flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition">
                        <span>{t('scan_now')}</span>
                        <ArrowRight size={20} />
                    </Link>
                </div>
            </div>
            <div className="mt-12 flex justify-center">
                <div className="bg-slate-800/50 px-6 py-2 rounded-full border border-slate-700 flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-sm text-gray-400">{t('status')}</span>
                </div>
            </div>
        </div>
    );
};

// --- AgriScout ---
const AgriScout = () => {
    const { t } = useLanguage();
    const center = [14.4644, 75.9218];
    const polygons = [
        { positions: [[14.465, 75.922], [14.466, 75.923], [14.465, 75.924], [14.464, 75.923]], color: 'red', status: 'Critical Stress' },
        { positions: [[14.463, 75.920], [14.464, 75.921], [14.463, 75.922], [14.462, 75.921]], color: 'green', status: 'Healthy Crop' }
    ];

    return (
        <div className="h-[calc(100vh-64px)] relative">
            <MapContainer center={center} zoom={15} style={{ height: '100%', width: '100%' }}>
                <TileLayer
                    url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                    attribution='Tiles &copy; Esri'
                />
                {polygons.map((poly, idx) => (
                    <Polygon key={idx} positions={poly.positions} pathOptions={{ color: poly.color, fillOpacity: 0.5 }}>
                        <Tooltip sticky>
                            <div className="font-bold">{poly.status}</div>
                            <div className="text-xs">NDVI Simulation</div>
                        </Tooltip>
                    </Polygon>
                ))}
            </MapContainer>
            <div className="absolute bottom-8 left-8 bg-slate-900/90 p-4 rounded-xl border border-slate-700 backdrop-blur-md z-[1000]">
                <h3 className="font-bold mb-2 text-white">{t('scout')} - Legend</h3>
                <div className="flex items-center space-x-2 mb-1">
                    <div className="w-4 h-4 bg-green-500 rounded opacity-50 border border-green-500"></div>
                    <span className="text-sm text-gray-300">Healthy (NDVI &gt; 0.6)</span>
                </div>
                <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 bg-red-500 rounded opacity-50 border border-red-500"></div>
                    <span className="text-sm text-gray-300">Critical (NDVI &lt; 0.3)</span>
                </div>
            </div>
        </div>
    );
};

// --- AgriDoctor ---
const SIMULATION_DATA = [
    { disease: "Tomato Early Blight", treatment: ["Remove infected leaves", "Apply copper fungicide", "Improve air circulation"] },
    { disease: "Tomato Late Blight", treatment: ["Destroy infected plants", "Use resistant varieties", "Apply neem oil"] },
    { disease: "Tomato Leaf Mold", treatment: ["Reduce humidity", "Water at base", "Apply sulfur fungicide"] },
    { disease: "Healthy Tomato", treatment: ["Continue regular watering", "Monitor for pests", "Add compost"] }
];

const AgriDoctor = () => {
    const { t, language } = useLanguage();
    const [image, setImage] = useState(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [isSimulation, setIsSimulation] = useState(false);
    const API_KEY = localStorage.getItem('VITE_GEMINI_API_KEY') || "YOUR_API_KEY_HERE";

    const handleImageUpload = (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => { setImage(reader.result); setResult(null); };
            reader.readAsDataURL(file);
        }
    };

    const analyzeImage = async () => {
        if (!image) return;
        setLoading(true);
        setIsSimulation(false);
        try {
            if (!API_KEY || API_KEY === "YOUR_API_KEY_HERE") throw new Error("Missing API Key");
            const genAI = new GoogleGenerativeAI(API_KEY);
            const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });
            const prompt = `Analyze this plant image. Identify the disease name (or say 'Healthy'). Provide a 3-step organic treatment plan in strictly JSON format: { "disease": "...", "treatment": ["step1", "step2", "step3"] }. Return the response in ${language === 'hi' ? 'Hindi' : language === 'kn' ? 'Kannada' : 'English'}.`;
            const base64Data = image.split(',')[1];
            const result = await model.generateContent([prompt, { inlineData: { data: base64Data, mimeType: "image/jpeg" } }]);
            const response = await result.response;
            const text = response.text().replace(/```json/g, '').replace(/```/g, '').trim();
            setResult(JSON.parse(text));
        } catch (err) {
            console.warn("API Failed, switching to Simulation Mode", err);
            setIsSimulation(true);
            setTimeout(() => {
                setResult(SIMULATION_DATA[Math.floor(Math.random() * SIMULATION_DATA.length)]);
                setLoading(false);
            }, 1500);
        } finally {
            if (API_KEY && API_KEY !== "YOUR_API_KEY_HERE") setLoading(false);
        }
    };

    return (
        <div className="p-8 max-w-4xl mx-auto">
            <h1 className="text-3xl font-bold mb-8 flex items-center space-x-2">
                <span className="text-blue-400">{t('doctor')}</span>
                <span className="text-gray-500 text-lg font-normal">/ AI Diagnosis</span>
            </h1>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="bg-slate-800 p-8 rounded-2xl border border-slate-700">
                    <div className="border-2 border-dashed border-slate-600 rounded-xl h-64 flex flex-col items-center justify-center relative overflow-hidden hover:border-blue-500 transition">
                        {image ? <img src={image} alt="Upload" className="w-full h-full object-cover" /> : <div className="text-center p-4"><Upload className="mx-auto text-gray-400 mb-2" size={48} /><p className="text-gray-400">{t('upload_image')}</p></div>}
                        <input type="file" accept="image/*" onChange={handleImageUpload} className="absolute inset-0 opacity-0 cursor-pointer" />
                    </div>
                    <button onClick={analyzeImage} disabled={!image || loading} className={`w-full mt-6 py-3 rounded-lg font-bold flex items-center justify-center space-x-2 transition ${!image || loading ? 'bg-slate-700 text-gray-500 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 text-white'}`}>
                        {loading ? <><Loader className="animate-spin" /><span>{t('analyzing')}</span></> : <span>{t('scan_now')}</span>}
                    </button>
                </div>
                <div className="bg-slate-800 p-8 rounded-2xl border border-slate-700 min-h-[400px]">
                    {result ? (
                        <div className="animate-fadeIn">
                            {isSimulation && <div className="bg-yellow-500/10 border border-yellow-500/50 text-yellow-500 px-4 py-2 rounded-lg mb-4 flex items-center space-x-2 text-sm"><AlertTriangle size={16} /><span>{t('simulation_mode')}</span></div>}
                            <h2 className="text-2xl font-bold text-white mb-2">{t('disease_detected')}</h2>
                            <div className="text-3xl font-bold text-red-400 mb-6">{result.disease}</div>
                            <h3 className="text-xl font-semibold text-green-400 mb-4 flex items-center space-x-2"><CheckCircle size={20} /><span>{t('treatment_plan')}</span></h3>
                            <ul className="space-y-3">{result.treatment.map((step, idx) => <li key={idx} className="flex items-start space-x-3 bg-slate-700/50 p-3 rounded-lg"><span className="bg-blue-500/20 text-blue-400 w-6 h-6 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">{idx + 1}</span><span className="text-gray-300">{step}</span></li>)}</ul>
                        </div>
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center text-gray-500 opacity-50"><CheckCircle size={64} className="mb-4" /><p>Results will appear here</p></div>
                    )}
                </div>
            </div>
        </div>
    );
};

// --- App ---
const App = () => {
    return (
        <LanguageProvider>
            <Router>
                <div className="min-h-screen bg-slate-900 text-white font-sans">
                    <Navbar />
                    <main>
                        <Routes>
                            <Route path="/" element={<Dashboard />} />
                            <Route path="/scout" element={<AgriScout />} />
                            <Route path="/doctor" element={<AgriDoctor />} />
                        </Routes>
                    </main>
                </div>
            </Router>
        </LanguageProvider>
    );
};

// --- Entry Point ---
const container = document.getElementById('root');
const root = createRoot(container);
root.render(<App />);
