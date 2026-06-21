// --- State & Gamification (LocalStorage) ---
const STORAGE_PREFIX = 'carbly_';
let carblyData = null;
let footprintResult = null;
let chartInstance = null;
let progressChartInstance = null;

// Gamification State
let xp = parseInt(localStorage.getItem(STORAGE_PREFIX + 'xp')) || 0;
let goals = JSON.parse(localStorage.getItem(STORAGE_PREFIX + 'goals')) || [];
let unlockedBadges = JSON.parse(localStorage.getItem(STORAGE_PREFIX + 'badges')) || [];
let weeklyLog = JSON.parse(localStorage.getItem(STORAGE_PREFIX + 'weekly_log')) || [];
let loginStreak = parseInt(localStorage.getItem(STORAGE_PREFIX + 'streak')) || 0;
let lastLogin = localStorage.getItem(STORAGE_PREFIX + 'last_login');

const LEVELS = [
    { max: 149, title: "Seedling", lvl: 1 },
    { max: 399, title: "Sapling", lvl: 2 },
    { max: 799, title: "Grove Keeper", lvl: 3 },
    { max: 1499, title: "Forest Guardian", lvl: 4 },
    { max: 999999, title: "Earth Champion", lvl: 5 }
];

const BADGES = [
    { id: 'first_step', icon: '🌱', name: 'First Step', desc: 'Complete onboarding' },
    { id: 'carbon_conscious', icon: '🧠', name: 'Carbon Conscious', desc: 'View your footprint breakdown' },
    { id: 'chipko_champion', icon: '🌳', name: 'Chipko Champion', desc: 'Footprint < India average' },
    { id: 'solar_saathi', icon: '☀️', name: 'Solar Saathi', desc: 'Log low electricity/high EV' },
    { id: 'metro_mover', icon: '🚇', name: 'Metro Mover', desc: 'Select public transit' },
    { id: 'ganga_guardian', icon: '🌊', name: 'Ganga Guardian', desc: 'Low AC usage' },
    { id: 'digital_detox', icon: '📵', name: 'Digital Detox', desc: 'Streaming < 1hr/day' },
    { id: 'green_grocer', icon: '🥗', name: 'Green Grocer', desc: 'Veg diet selected' },
    { id: 'transit_champion', icon: '🚌', name: 'Transit Champion', desc: 'High transit days' },
    { id: 'carbon_crusher', icon: '💥', name: 'Carbon Crusher', desc: 'Score > 80' },
    { id: 'earth_champion', icon: '🌍', name: 'Earth Champion', desc: 'Reach Level 5' },
    { id: 'streak_master', icon: '🔥', name: 'Streak Master', desc: '7-day login streak' }
];

function initGamification() {
    // Handle Streak
    const today = new Date().toDateString();
    if (lastLogin !== today) {
        if (lastLogin === new Date(Date.now() - 86400000).toDateString()) {
            loginStreak++;
        } else {
            loginStreak = 1; // Reset or start
        }
        localStorage.setItem(STORAGE_PREFIX + 'last_login', today);
        localStorage.setItem(STORAGE_PREFIX + 'streak', loginStreak);
    }
    if (loginStreak >= 7) checkBadge('streak_master');
    
    updateXP(0); // refresh UI
}

function updateXP(amount) {
    if(amount > 0) {
        xp += amount;
        localStorage.setItem(STORAGE_PREFIX + 'xp', xp);
        showToast(`+${amount} XP Earned!`);
    }
    
    let currentLevel = LEVELS[0];
    let nextLevelXP = LEVELS[1].max;
    let prevLevelXP = 0;
    
    for (let i = 0; i < LEVELS.length; i++) {
        if (xp <= LEVELS[i].max) {
            currentLevel = LEVELS[i];
            nextLevelXP = LEVELS[i].max + 1;
            prevLevelXP = i > 0 ? LEVELS[i-1].max + 1 : 0;
            break;
        }
    }
    
    document.getElementById('karma-title').textContent = `${currentLevel.title} - Lvl ${currentLevel.lvl}`;
    document.getElementById('stat-xp').textContent = `${xp} XP`;
    document.getElementById('stat-streak').textContent = `${loginStreak} Day Streak`;
    
    const progress = Math.max(0, Math.min(100, ((xp - prevLevelXP) / (nextLevelXP - prevLevelXP)) * 100));
    document.getElementById('xp-bar').style.width = `${progress}%`;
    
    if (currentLevel.lvl >= 5) checkBadge('earth_champion');
}

function checkBadge(badgeId) {
    if (!unlockedBadges.includes(badgeId)) {
        unlockedBadges.push(badgeId);
        localStorage.setItem(STORAGE_PREFIX + 'badges', JSON.stringify(unlockedBadges));
        confetti({ particleCount: 100, spread: 70, origin: { y: 0.6 } });
        showToast(`🏆 Badge Unlocked: ${BADGES.find(b=>b.id===badgeId).name}!`);
        renderBadges();
    }
}

// --- Navigation & Views ---
function navTo(viewId) {
    // Hide auth wrapper if visible
    document.getElementById('auth-wrapper').style.display = 'none';
    document.getElementById('app-container').style.display = 'flex';
    document.getElementById('top-stats-bar').classList.remove('hidden');

    // Update Nav active states
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    const targetNav = Array.from(document.querySelectorAll('.nav-item')).find(el => el.getAttribute('onclick') === `navTo('${viewId}')`);
    if(targetNav) targetNav.classList.add('active');

    // Hide all views
    document.querySelectorAll('.view-section').forEach(v => {
        v.classList.remove('active');
    });
    
    // Show target
    const target = document.getElementById(`${viewId}-view`);
    if(target) target.classList.add('active');

    if(viewId === 'dashboard') checkBadge('carbon_conscious');
    if(viewId === 'achievements') renderBadges();
    if(viewId === 'goals') renderGoals();
    if(viewId === 'progress') renderWeeklyProgress();
}

// --- Toast ---
function showToast(msg) {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.classList.remove('opacity-0', '-translate-y-full');
    setTimeout(() => {
        toast.classList.add('opacity-0', '-translate-y-full');
    }, 3000);
}

// --- Landing & Auth Selection ---
function startOnboarding(type) {
    document.getElementById('landing-view').classList.add('hidden');
    if(type === 'chat') {
        document.getElementById('chat-onboarding-view').classList.remove('hidden');
        setTimeout(() => document.getElementById('chat-onboarding-view').classList.remove('opacity-0'), 50);
        addMessage('ai', 'Hi! I am Carbly Assistant. To start, what is your name and which city in India do you live in?', 'onboarding-chat-container');
        onboardingHistory.push({ role: 'ai', content: 'Hi! I am Carbly Assistant. To start, what is your name and which city in India do you live in?'});
    } else {
        document.getElementById('form-onboarding-view').classList.remove('hidden');
        setTimeout(() => document.getElementById('form-onboarding-view').classList.remove('opacity-0'), 50);
    }
}

// --- Quick Form Logic ---
let currentStep = 1;
const totalSteps = 5;

document.querySelectorAll('.form-toggle').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const group = e.target.parentElement;
        group.querySelectorAll('.form-toggle').forEach(b => b.classList.remove('selected'));
        e.target.classList.add('selected');
    });
});

document.getElementById('f-ac').addEventListener('input', (e) => {
    document.getElementById('f-ac-val').textContent = e.target.value;
});

document.getElementById('form-next').addEventListener('click', () => {
    document.getElementById(`step-${currentStep}`).classList.add('hidden');
    document.getElementById(`step-${currentStep}`).classList.remove('block');
    currentStep++;
    updateFormUI();
});

document.getElementById('form-back').addEventListener('click', () => {
    document.getElementById(`step-${currentStep}`).classList.add('hidden');
    document.getElementById(`step-${currentStep}`).classList.remove('block');
    currentStep--;
    updateFormUI();
});

function updateFormUI() {
    document.getElementById(`step-${currentStep}`).classList.remove('hidden');
    document.getElementById(`step-${currentStep}`).classList.add('block');
    
    document.getElementById('form-step-indicator').textContent = `${currentStep} of ${totalSteps}`;
    document.getElementById('form-progress').style.width = `${(currentStep/totalSteps)*100}%`;
    
    const titles = ['Transport', 'Energy', 'Food', 'Digital & Lifestyle', 'Review'];
    document.getElementById('form-step-title').textContent = `Step ${currentStep}: ${titles[currentStep-1]}`;
    
    document.getElementById('form-back').classList.toggle('hidden', currentStep === 1);
    document.getElementById('form-next').classList.toggle('hidden', currentStep === totalSteps);
    document.getElementById('form-submit').classList.toggle('hidden', currentStep !== totalSteps);
}

document.getElementById('form-submit').addEventListener('click', () => {
    const mode = document.querySelector('#f-mode-group .selected').dataset.val;
    const diet = document.querySelector('#f-diet-group .selected').dataset.val;
    
    carblyData = {
        name: "User",
        city: "India",
        transport: {
            mode: mode,
            km_per_day: parseFloat(document.getElementById('f-km').value) || 0,
            flights_domestic: 0,
            flights_international: 0
        },
        energy: {
            kwh_per_month: parseFloat(document.getElementById('f-kwh').value) || 0,
            ac_hours_per_day: parseFloat(document.getElementById('f-ac').value) || 0,
            ac_units: 1,
            lpg_cylinders_per_month: parseFloat(document.getElementById('f-lpg').value) || 0
        },
        food: {
            diet_type: diet,
            chicken_meals_per_week: diet === 'non-veg' ? parseFloat(document.getElementById('f-meat').value) || 0 : 0,
            mutton_meals_per_week: 0,
            beef_meals_per_week: 0
        },
        digital: {
            streaming_hours_per_day: parseFloat(document.getElementById('f-stream').value) || 0,
            online_orders_per_month: parseFloat(document.getElementById('f-orders').value) || 0
        },
        lifestyle: {
            new_clothes_per_month: parseFloat(document.getElementById('f-clothes').value) || 0,
            daily_steps: 0
        }
    };
    
    completeOnboarding();
});

// --- Chat Onboarding Logic ---
let onboardingHistory = [];
const chatForm = document.getElementById('onboarding-form');
const chatInput = document.getElementById('onboarding-input');
let qCount = 1;

function addMessage(role, text, containerId) {
    const container = document.getElementById(containerId);
    const div = document.createElement('div');
    div.className = `chat-bubble ${role}`;
    
    if (role === 'ai') {
        const rawHtml = marked.parse(text);
        div.innerHTML = DOMPurify.sanitize(rawHtml);
    } else {
        div.textContent = text;
    }
    
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function showTyping(containerId) {
    const container = document.getElementById(containerId);
    const div = document.createElement('div');
    div.className = `chat-bubble ai typing-indicator shimmer w-24 h-8`;
    div.id = 'typing-' + containerId;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = chatInput.value.trim();
    if (!text) return;
    
    addMessage('user', text, 'onboarding-chat-container');
    onboardingHistory.push({ role: 'user', content: text });
    chatInput.value = '';
    
    qCount = Math.min(13, qCount + 1);
    document.getElementById('onboarding-progress').style.width = `${(qCount/13)*100}%`;
    document.getElementById('q-count').textContent = qCount;

    showTyping('onboarding-chat-container');
    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, history: onboardingHistory, phase: 'onboarding' })
        });
        const data = await res.json();
        document.getElementById('typing-onboarding-chat-container')?.remove();
        
        let replyText = data.reply.replace(/```carbly_data[\s\S]*?```/, '').trim();
        if(replyText) {
            addMessage('ai', replyText, 'onboarding-chat-container');
            onboardingHistory.push({ role: 'ai', content: replyText });
        }
        
        if (data.data_collected && data.carbly_data) {
            carblyData = data.carbly_data;
            completeOnboarding();
        }
    } catch (err) {
        document.getElementById('typing-onboarding-chat-container')?.remove();
        addMessage('ai', 'Error connecting.', 'onboarding-chat-container');
    }
});

function completeOnboarding() {
    localStorage.setItem(STORAGE_PREFIX + 'data', JSON.stringify(carblyData));
    checkBadge('first_step');
    updateXP(100);
    loadDashboard();
}

// --- Dashboard Loading ---
async function loadDashboard() {
    try {
        const res = await fetch('/api/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(carblyData)
        });
        footprintResult = await res.json();
        
        // Save to weekly log
        const todayStr = new Date().toLocaleDateString();
        const existingLogIndex = weeklyLog.findIndex(l => l.date === todayStr);
        if(existingLogIndex >= 0) {
            weeklyLog[existingLogIndex].kg = footprintResult.monthly_kg_total / 30; // approx daily
        } else {
            weeklyLog.push({ date: todayStr, kg: footprintResult.monthly_kg_total / 30 });
            if(weeklyLog.length > 7) weeklyLog.shift();
        }
        localStorage.setItem(STORAGE_PREFIX + 'weekly_log', JSON.stringify(weeklyLog));
        
        updateDashboardUI();
        navTo('dashboard');
        
    } catch(err) {
        showToast("Error calculating footprint.");
    }
}

function updateDashboardUI() {
    const r = footprintResult;
    
    // Header & Rings
    document.getElementById('dash-score').textContent = r.score;
    document.getElementById('dash-monthly-kg').textContent = Math.round(r.monthly_kg_total) + ' kg CO₂';
    document.getElementById('mini-kg').textContent = Math.round(r.monthly_kg_total) + ' kg CO₂';
    document.getElementById('mini-score-ring').textContent = r.score;
    document.getElementById('stat-monthly').textContent = Math.round(r.monthly_kg_total) + ' kg this month';
    
    // Planet Widget Logic
    const planet = document.getElementById('planet-widget');
    let colorHex = '#ef4444'; // Red
    let gradient = 'radial-gradient(circle at 30% 30%, #fca5a5, #7f1d1d)';
    
    if(r.score >= 60) { colorHex = '#4ade80'; gradient = 'radial-gradient(circle at 30% 30%, #86efac, #064e3b)'; checkBadge('carbon_crusher'); }
    else if(r.score >= 50) { colorHex = '#fbbf24'; gradient = 'radial-gradient(circle at 30% 30%, #fde047, #78350f)'; }
    
    planet.style.background = gradient;
    document.getElementById('score-ring').style.setProperty('--score-deg', `${(r.score / 100) * 360}deg`);
    document.getElementById('score-ring').style.setProperty('--score-color', colorHex);
    document.getElementById('mini-score-ring').style.borderColor = colorHex;
    document.getElementById('mini-score-ring').style.color = colorHex;
    
    // Badges Checks based on Footprint
    if (r.vs_india_avg < 0) checkBadge('chipko_champion');
    if (r.monthly_kg.energy < 50) checkBadge('solar_saathi');
    if (carblyData.transport.mode === 'metro') checkBadge('metro_mover');
    if (carblyData.energy.ac_hours_per_day < 2) checkBadge('ganga_guardian');
    if (carblyData.digital.streaming_hours_per_day < 1) checkBadge('digital_detox');
    if (carblyData.food.diet_type === 'veg') checkBadge('green_grocer');

    // Benchmarks
    const formatDiff = (val) => `${val > 0 ? '+' : ''}${Math.round(val)}%`;
    document.getElementById('bench-india').textContent = formatDiff(r.vs_india_avg);
    document.getElementById('bench-india').style.color = r.vs_india_avg > 0 ? 'var(--danger-red)' : 'var(--accent-green)';
    document.getElementById('bench-india-text').textContent = r.vs_india_avg > 0 ? 'Higher' : 'Lower';
    
    document.getElementById('bench-paris').textContent = formatDiff(r.vs_paris_target);
    document.getElementById('bench-paris').style.color = r.vs_paris_target > 0 ? 'var(--danger-red)' : 'var(--accent-green)';
    document.getElementById('bench-paris-text').textContent = r.vs_paris_target > 0 ? 'Higher' : 'Lower';
    
    document.getElementById('stat-rating').textContent = `${Math.round(100 - (r.annual_kg / 4800)*50)}% Rating`; // Rough rating
    
    // Equivalences
    document.getElementById('eq-trees').textContent = Math.round(r.trees_needed);
    document.getElementById('eq-flights').textContent = r.equivalent_flights.toFixed(1);
    
    // Charts & Actions
    renderDoughnutChart(r.monthly_kg);
    renderActions(r.actions);
}

// --- Charts ---
function renderDoughnutChart(kgData) {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    if(chartInstance) chartInstance.destroy();
    
    chartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Transport', 'Energy', 'Food', 'Digital', 'Lifestyle'],
            datasets: [{
                data: [kgData.transport, kgData.energy, kgData.food, kgData.digital, kgData.lifestyle],
                backgroundColor: ['#4ade80', '#fbbf24', '#2dd4bf', '#60a5fa', '#c084fc'],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { color: '#f0fdf4' } } } }
    });
}

// --- Actions ---
function renderActions(actions) {
    const container = document.getElementById('actions-container');
    container.innerHTML = '';
    
    actions.forEach(act => {
        const div = document.createElement('div');
        div.className = 'glass-card p-5 flex flex-col interactive';
        let diffColor = act.difficulty === 'easy' ? 'text-green-300' : act.difficulty === 'medium' ? 'text-amber-300' : 'text-red-300';
        
        div.innerHTML = `
            <div class="flex justify-between items-start mb-3">
                <h4 class="font-bold leading-tight">${act.title}</h4>
                <span class="text-xs px-2 py-1 bg-black/30 rounded capitalize ${diffColor}">${act.difficulty}</span>
            </div>
            <p class="text-xs text-green-100/70 mb-4 flex-1">${act.description}</p>
            <div class="flex items-center justify-between mt-auto">
                <span class="font-semibold text-green-300 text-sm">-${Math.round(act.potential_saving_kg_monthly)} kg/mo</span>
                <button class="text-xs bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded-full transition" onclick="takeAction('${act.title}')">Take Action</button>
            </div>
        `;
        container.appendChild(div);
    });
}

function takeAction(title) {
    updateXP(5);
    navTo('chat');
    document.getElementById('chat-input').value = `I want to commit to: ${title}. How do I start?`;
}

// --- Main Chat ---
let sidebarHistory = [];
document.getElementById('chat-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = document.getElementById('chat-input').value.trim();
    if(!text) return;
    
    addMessage('user', text, 'chat-container');
    sidebarHistory.push({ role: 'user', content: text });
    document.getElementById('chat-input').value = '';
    showTyping('chat-container');
    
    let contextHistory = [...sidebarHistory];
    if(contextHistory.length === 1 && footprintResult) {
        contextHistory[0].content = `Context: My monthly carbon footprint is ${Math.round(footprintResult.monthly_kg_total)} kg. ` + contextHistory[0].content;
    }

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, history: contextHistory, phase: 'dashboard' })
        });
        const data = await res.json();
        document.getElementById('typing-chat-container')?.remove();
        addMessage('ai', data.reply, 'chat-container');
        sidebarHistory.push({ role: 'ai', content: data.reply });
        updateXP(5);
    } catch(err) {
        document.getElementById('typing-chat-container')?.remove();
        addMessage('ai', 'Error connecting to coach.', 'chat-container');
    }
});

// --- Achievements ---
function renderBadges() {
    const container = document.getElementById('badges-container');
    if(!container) return;
    container.innerHTML = '';
    
    document.getElementById('stat-badges').textContent = `${unlockedBadges.length}/12 Badges`;
    document.getElementById('badge-count-display').textContent = `${unlockedBadges.length}/12 Unlocked`;
    
    BADGES.forEach(b => {
        const isUnlocked = unlockedBadges.includes(b.id);
        const stateClass = isUnlocked ? 'unlocked' : 'locked bg-black/40';
        
        container.innerHTML += `
            <div class="glass-card badge-card p-4 text-center ${stateClass}">
                <div class="text-4xl mb-2">${b.icon}</div>
                <h4 class="font-bold text-sm mb-1">${b.name}</h4>
                <p class="text-xs text-white/50">${isUnlocked ? 'Unlocked!' : b.desc}</p>
                ${!isUnlocked ? '<div class="absolute top-2 right-2 text-xs">🔒</div>' : ''}
            </div>
        `;
    });
}

// --- Goals Memory Bank ---
function renderGoals() {
    const container = document.getElementById('goals-container');
    if(!container) return;
    container.innerHTML = '';
    
    if(goals.length === 0) {
        container.innerHTML = '<p class="text-white/50 text-center py-4">No goals yet. Add one above!</p>';
        return;
    }
    
    goals.forEach((g, index) => {
        const checkClass = g.completed ? 'text-green-400 bg-green-400/10 border-green-400/50' : 'text-white/50 bg-white/5 border-white/10';
        container.innerHTML += `
            <div class="glass-card p-4 flex items-center justify-between border ${g.completed ? 'border-green-500/30' : ''}">
                <div class="flex items-center gap-4 flex-1">
                    <button class="w-6 h-6 rounded-full border ${checkClass} flex items-center justify-center text-xs" onclick="toggleGoal(${index})">
                        ${g.completed ? '✓' : ''}
                    </button>
                    <div>
                        <p class="${g.completed ? 'line-through text-white/50' : 'font-medium'}">${g.text}</p>
                        <p class="text-xs text-white/40">Added ${g.date}</p>
                    </div>
                </div>
                <button class="text-red-400/50 hover:text-red-400 text-sm px-2" onclick="deleteGoal(${index})">✕</button>
            </div>
        `;
    });
}

document.getElementById('goal-form').addEventListener('submit', (e) => {
    e.preventDefault();
    const input = document.getElementById('goal-input');
    if(!input.value.trim()) return;
    goals.push({ text: input.value.trim(), date: new Date().toLocaleDateString(), completed: false });
    localStorage.setItem(STORAGE_PREFIX + 'goals', JSON.stringify(goals));
    input.value = '';
    renderGoals();
    showToast('Goal Added!');
});

function toggleGoal(index) {
    goals[index].completed = !goals[index].completed;
    localStorage.setItem(STORAGE_PREFIX + 'goals', JSON.stringify(goals));
    if(goals[index].completed) {
        updateXP(75);
        confetti({ particleCount: 50, spread: 50, origin: { y: 0.8 } });
    }
    renderGoals();
}

function deleteGoal(index) {
    goals.splice(index, 1);
    localStorage.setItem(STORAGE_PREFIX + 'goals', JSON.stringify(goals));
    renderGoals();
}

// --- Weekly Progress Chart ---
function renderWeeklyProgress() {
    if(weeklyLog.length === 0) return;
    
    const ctx = document.getElementById('progressChart').getContext('2d');
    if(progressChartInstance) progressChartInstance.destroy();
    
    const labels = weeklyLog.map(l => l.date.substring(0, 5));
    const data = weeklyLog.map(l => l.kg);
    
    progressChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Daily CO₂ (kg)',
                data: data,
                borderColor: '#4ade80',
                backgroundColor: 'rgba(74, 222, 128, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.1)' } }, x: { grid: { display: false } } } }
    });
    
    // Heatmap
    const heatContainer = document.getElementById('heatmap-container');
    heatContainer.innerHTML = '';
    for(let i=0; i<30; i++) {
        // Mock heatmap: last N days green based on streak
        const isLogged = i < loginStreak;
        const color = isLogged ? 'bg-green-400' : 'bg-white/10';
        heatContainer.innerHTML += `<div class="w-4 h-4 rounded-sm ${color}"></div>`;
    }
}

// --- Manual Entry ---
function openManualEntry() {
    document.getElementById('manual-modal').classList.remove('hidden');
    setTimeout(() => {
        document.getElementById('manual-modal').classList.remove('opacity-0');
        document.getElementById('manual-modal-content').classList.remove('scale-95');
    }, 10);
}
function closeManualEntry() {
    document.getElementById('manual-modal').classList.add('opacity-0');
    document.getElementById('manual-modal-content').classList.add('scale-95');
    setTimeout(() => document.getElementById('manual-modal').classList.add('hidden'), 300);
}

document.getElementById('manual-form').addEventListener('submit', (e) => {
    e.preventDefault();
    if(!carblyData) { showToast("No data to update!"); return; }
    
    const kwh = document.getElementById('manual-kwh').value;
    const flights = document.getElementById('manual-flights').value;
    const ac = document.getElementById('manual-ac').value;
    
    if(kwh) carblyData.energy.kwh_per_month = parseFloat(kwh);
    if(flights) carblyData.transport.flights_domestic = parseFloat(flights);
    if(ac) carblyData.energy.ac_hours_per_day = parseFloat(ac);
    
    localStorage.setItem(STORAGE_PREFIX + 'data', JSON.stringify(carblyData));
    updateXP(10);
    closeManualEntry();
    showToast("Updating Dashboard...");
    loadDashboard();
});

// Init
initGamification();
const savedData = localStorage.getItem(STORAGE_PREFIX + 'data');
if (savedData) {
    carblyData = JSON.parse(savedData);
    document.getElementById('auth-wrapper').style.display = 'none';
    document.getElementById('app-container').style.display = 'flex';
    document.getElementById('top-stats-bar').classList.remove('hidden');
    loadDashboard();
}
