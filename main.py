import json
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiohttp import web
import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен бота
BOT_TOKEN = "8672976273:AAF2_7CQvkRFjtHbDoHdwxdc5ZMafWWrvo8"

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# HTML код игры (встроенный)
GAME_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>Soul Knight - Битва</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            user-select: none;
        }

        body {
            min-height: 100vh;
            background: linear-gradient(135deg, #1a0f0a 0%, #2d1b13 100%);
            font-family: 'Segoe UI', 'Courier New', monospace;
            padding: 15px;
            position: relative;
        }

        .game-wrapper {
            max-width: 500px;
            margin: 0 auto;
            background: rgba(0, 0, 0, 0.7);
            border-radius: 40px;
            border: 3px solid #ffd700;
            box-shadow: 0 10px 40px rgba(0,0,0,0.5), inset 0 1px 2px rgba(255,215,0,0.3);
            overflow: hidden;
            backdrop-filter: blur(5px);
        }

        .character-panel {
            background: linear-gradient(135deg, #2c1810, #1a0f0a);
            padding: 15px;
            border-bottom: 2px solid #ffd700;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-bottom: 10px;
        }

        .stat-card {
            background: rgba(0,0,0,0.6);
            padding: 8px;
            border-radius: 15px;
            text-align: center;
            border: 1px solid #ffd700;
        }

        .stat-value {
            font-size: 18px;
            font-weight: bold;
            color: #ffd700;
        }

        .stat-label {
            font-size: 10px;
            color: #ccc;
            margin-top: 3px;
        }

        .exp-bar {
            background: #3a2a1f;
            border-radius: 20px;
            height: 20px;
            overflow: hidden;
            margin-top: 10px;
        }

        .exp-fill {
            background: linear-gradient(90deg, #ffd700, #ff8c00);
            width: 0%;
            height: 100%;
            transition: width 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #000;
            font-size: 10px;
            font-weight: bold;
        }

        .scene {
            padding: 20px;
            transition: all 0.3s;
        }

        .spawn-scene {
            display: block;
        }

        .battle-scene {
            display: none;
        }

        .npc-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin-bottom: 20px;
        }

        .npc-card {
            background: linear-gradient(135deg, #3d2b1f, #2a1a10);
            border-radius: 20px;
            padding: 15px 8px;
            text-align: center;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            border: 1px solid #ffd700;
        }

        .npc-card:active {
            transform: scale(0.95);
        }

        .npc-emoji {
            font-size: 48px;
        }

        .npc-name {
            color: #ffd700;
            font-weight: bold;
            margin: 8px 0 5px;
        }

        .portal {
            background: radial-gradient(circle, #6a0dad, #4a0080);
            border-radius: 30px;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            border: 2px solid #ff00ff;
            box-shadow: 0 0 20px rgba(255,0,255,0.5);
            margin-bottom: 20px;
        }

        .portal:active {
            transform: scale(0.98);
        }

        .enemy-card {
            background: #8b0000;
            border-radius: 25px;
            padding: 20px;
            text-align: center;
            margin-bottom: 20px;
            border: 2px solid #ff4444;
        }

        .enemy-stats {
            margin: 10px 0;
        }

        .battle-buttons {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 15px;
        }

        .attack-btn {
            background: linear-gradient(135deg, #dc143c, #8b0000);
            color: white;
            border: none;
            padding: 15px;
            border-radius: 30px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
        }

        .flee-btn {
            background: linear-gradient(135deg, #696969, #363636);
            color: white;
            border: none;
            padding: 15px;
            border-radius: 30px;
            font-size: 18px;
            cursor: pointer;
        }

        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.9);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }

        .modal-content {
            background: linear-gradient(135deg, #2c1810, #1a0f0a);
            border-radius: 30px;
            padding: 25px;
            max-width: 350px;
            width: 90%;
            border: 2px solid #ffd700;
            max-height: 80vh;
            overflow-y: auto;
        }

        .shop-item {
            background: rgba(255,215,0,0.1);
            margin: 10px 0;
            padding: 12px;
            border-radius: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .buy-btn {
            background: #ffd700;
            border: none;
            padding: 8px 15px;
            border-radius: 20px;
            cursor: pointer;
            font-weight: bold;
        }

        .close-modal {
            background: #ff4444;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 20px;
            width: 100%;
            margin-top: 15px;
            cursor: pointer;
        }

        .notification {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0,0,0,0.9);
            color: #ffd700;
            padding: 10px 20px;
            border-radius: 30px;
            z-index: 1001;
            font-size: 14px;
            white-space: nowrap;
        }

        @keyframes damage {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); background: #ff0000; }
            100% { transform: scale(1); }
        }

        .damage-animation {
            animation: damage 0.3s ease;
        }
    </style>
</head>
<body>
<div class="game-wrapper">
    <div class="character-panel">
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value" id="playerName">Рыцарь</div>
                <div class="stat-label">Имя</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="playerHp">100</div>
                <div class="stat-label">❤️ Здоровье</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="playerDamage">15</div>
                <div class="stat-label">⚔️ Урон</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="playerLevel">1</div>
                <div class="stat-label">⭐ Уровень</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="playerCoins">0</div>
                <div class="stat-label">💰 Монеты</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="playerResources">0</div>
                <div class="stat-label">💎 Ресурсы</div>
            </div>
        </div>
        <div class="exp-bar">
            <div class="exp-fill" id="expBar">0/100</div>
        </div>
    </div>

    <div id="spawnScene" class="scene spawn-scene">
        <div class="portal" onclick="enterBattle()">
            <div class="npc-emoji">🌀</div>
            <div class="npc-name">Портал в Битву</div>
            <div style="font-size: 12px; color: #ccc;">Нажми, чтобы сражаться!</div>
        </div>

        <div class="npc-grid">
            <div class="npc-card" onclick="openShop('weapons')">
                <div class="npc-emoji">⚒️</div>
                <div class="npc-name">Кузнец</div>
                <div style="font-size: 10px;">Оружие</div>
            </div>
            <div class="npc-card" onclick="openShop('buffs')">
                <div class="npc-emoji">🧪</div>
                <div class="npc-name">Алхимик</div>
                <div style="font-size: 10px;">Баффы</div>
            </div>
            <div class="npc-card" onclick="openShop('merchant')">
                <div class="npc-emoji">💼</div>
                <div class="npc-name">Скупщик</div>
                <div style="font-size: 10px;">Обмен</div>
            </div>
        </div>

        <div class="npc-card" onclick="openQuests()" style="margin-top: 10px;">
            <div class="npc-emoji">📜</div>
            <div class="npc-name">Квесты</div>
        </div>
    </div>

    <div id="battleScene" class="scene battle-scene">
        <div class="enemy-card" id="enemyCard">
            <div class="npc-emoji" id="enemyEmoji">👾</div>
            <div class="npc-name" id="enemyName">Гоблин</div>
            <div class="enemy-stats">
                <div>❤️ <span id="enemyHp">30</span>/<span id="enemyMaxHp">30</span></div>
                <div>⚔️ Урон: <span id="enemyDamage">8</span></div>
            </div>
        </div>
        <div class="battle-buttons">
            <button class="attack-btn" onclick="attack()">⚔️ АТАКОВАТЬ</button>
            <button class="flee-btn" onclick="flee()">🏃‍♂️ СБЕЖАТЬ</button>
        </div>
    </div>
</div>

<div id="modal" class="modal">
    <div class="modal-content">
        <div id="modalBody"></div>
        <button class="close-modal" onclick="closeModal()">Закрыть</button>
    </div>
</div>

<script>
    let gameState = {
        name: "Рыцарь",
        hp: 100,
        maxHp: 100,
        damage: 15,
        level: 1,
        exp: 0,
        expToNext: 100,
        coins: 50,
        resources: 10,
        weapon: "Меч",
        buffs: []
    };

    let currentEnemy = null;
    let inBattle = false;

    const enemies = [
        { name: "Гоблин", emoji: "👺", hp: 30, maxHp: 30, damage: 8, exp: 20, coins: 15, resources: 3 },
        { name: "Скелет", emoji: "💀", hp: 45, maxHp: 45, damage: 12, exp: 35, coins: 25, resources: 5 },
        { name: "Орк", emoji: "👹", hp: 60, maxHp: 60, damage: 15, exp: 50, coins: 40, resources: 8 },
        { name: "Тролль", emoji: "🗿", hp: 80, maxHp: 80, damage: 18, exp: 70, coins: 60, resources: 12 },
        { name: "Дракон", emoji: "🐉", hp: 120, maxHp: 120, damage: 25, exp: 100, coins: 100, resources: 20 }
    ];

    const shops = {
        weapons: {
            title: "⚒️ Кузнец - Оружие",
            items: [
                { name: "Стальной меч", price: 50, effect: { damage: 5 }, desc: "+5 к урону" },
                { name: "Лук охотника", price: 80, effect: { damage: 8 }, desc: "+8 к урону" },
                { name: "Волшебный посох", price: 120, effect: { damage: 12 }, desc: "+12 к урону" }
            ]
        },
        buffs: {
            title: "🧪 Алхимик - Баффы",
            items: [
                { name: "Зелье здоровья", price: 40, effect: { hpBonus: 20 }, desc: "+20 к макс. HP" },
                { name: "Эликсир силы", price: 60, effect: { damageBonus: 5 }, desc: "+5 к урону" },
                { name: "Камень жизни", price: 100, effect: { hpBonus: 50 }, desc: "+50 к макс. HP" }
            ]
        },
        merchant: {
            title: "💼 Скупщик - Обмен ресурсов",
            items: [
                { name: "Продать ресурсы", price: 5, desc: "1 ресурс = 5 монет", type: "sell" }
            ]
        }
    };

    let activeQuest = {
        name: "Победить 3 монстров",
        progress: 0,
        required: 3,
        reward: { coins: 50, exp: 30 },
        completed: false
    };

    function updateUI() {
        document.getElementById('playerName').innerText = gameState.name;
        document.getElementById('playerHp').innerText = `${gameState.hp}/${gameState.maxHp}`;
        document.getElementById('playerDamage').innerText = gameState.damage;
        document.getElementById('playerLevel').innerText = gameState.level;
        document.getElementById('playerCoins').innerText = Math.floor(gameState.coins);
        document.getElementById('playerResources').innerText = gameState.resources;
        
        const expPercent = (gameState.exp / gameState.expToNext) * 100;
        const expBar = document.getElementById('expBar');
        expBar.style.width = `${expPercent}%`;
        expBar.innerText = `${gameState.exp}/${gameState.expToNext}`;
    }

    function addExp(amount) {
        gameState.exp += amount;
        while (gameState.exp >= gameState.expToNext) {
            gameState.exp -= gameState.expToNext;
            gameState.level++;
            gameState.maxHp += 10;
            gameState.hp = gameState.maxHp;
            gameState.damage += 3;
            gameState.expToNext = Math.floor(gameState.expToNext * 1.2);
            showNotification(`🎉 УРОВЕНЬ ${gameState.level}! +10 HP, +3 урона!`);
        }
        updateUI();
    }

    function showNotification(msg) {
        const notif = document.createElement('div');
        notif.className = 'notification';
        notif.innerText = msg;
        document.body.appendChild(notif);
        setTimeout(() => notif.remove(), 2000);
    }

    function enterBattle() {
        if (inBattle) return;
        const enemyIndex = Math.min(gameState.level - 1, enemies.length - 1);
        currentEnemy = JSON.parse(JSON.stringify(enemies[enemyIndex]));
        
        document.getElementById('spawnScene').style.display = 'none';
        document.getElementById('battleScene').style.display = 'block';
        inBattle = true;
        
        updateEnemyUI();
        showNotification("🌀 Ты вошел в битву! Сражайся или беги!");
    }

    function updateEnemyUI() {
        if (!currentEnemy) return;
        document.getElementById('enemyEmoji').innerText = currentEnemy.emoji;
        document.getElementById('enemyName').innerText = currentEnemy.name;
        document.getElementById('enemyHp').innerText = currentEnemy.hp;
        document.getElementById('enemyMaxHp').innerText = currentEnemy.maxHp;
        document.getElementById('enemyDamage').innerText = currentEnemy.damage;
    }

    function attack() {
        if (!inBattle || !currentEnemy) return;
        
        const playerDamage = gameState.damage + Math.floor(Math.random() * 5);
        currentEnemy.hp -= playerDamage;
        
        document.getElementById('enemyCard').classList.add('damage-animation');
        setTimeout(() => document.getElementById('enemyCard').classList.remove('damage-animation'), 300);
        
        showNotification(`⚔️ Вы нанесли ${playerDamage} урона!`);
        
        if (currentEnemy.hp <= 0) {
            const rewardCoins = currentEnemy.coins;
            const rewardExp = currentEnemy.exp;
            const rewardResources = currentEnemy.resources;
            
            gameState.coins += rewardCoins;
            gameState.resources += rewardResources;
            addExp(rewardExp);
            
            if (!activeQuest.completed) {
                activeQuest.progress++;
                if (activeQuest.progress >= activeQuest.required) {
                    activeQuest.completed = true;
                    gameState.coins += activeQuest.reward.coins;
                    addExp(activeQuest.reward.exp);
                    showNotification(`✅ Квест выполнен! +${activeQuest.reward.coins} монет, +${activeQuest.reward.exp} опыта!`);
                }
            }
            
            showNotification(`🎉 Победа! +${rewardCoins}💰 +${rewardExp}⭐ +${rewardResources}💎`);
            updateUI();
            flee();
            return;
        }
        
        const enemyDamage = currentEnemy.damage + Math.floor(Math.random() * 5);
        gameState.hp -= enemyDamage;
        updateUI();
        showNotification(`😖 ${currentEnemy.name} нанес ${enemyDamage} урона!`);
        
        if (gameState.hp <= 0) {
            gameState.hp = gameState.maxHp / 2;
            updateUI();
            showNotification("💀 Ты погиб... Возвращайся в спавн и лечись!");
            flee();
        }
        
        updateEnemyUI();
    }

    function flee() {
        inBattle = false;
        currentEnemy = null;
        document.getElementById('battleScene').style.display = 'none';
        document.getElementById('spawnScene').style.display = 'block';
        showNotification("🏠 Ты вернулся в спавн!");
    }

    function openShop(type) {
        const shop = shops[type];
        if (!shop) return;
        
        let html = `<h3>${shop.title}</h3>`;
        
        shop.items.forEach(item => {
            html += `
                <div class="shop-item">
                    <div>
                        <strong>${item.name}</strong><br>
                        <small>${item.desc}</small>
                    </div>
                    <button class="buy-btn" onclick="buyItem('${type}', '${item.name}')">
                        ${item.type === 'sell' ? 'Продать' : `${item.price}💰`}
                    </button>
                </div>
            `;
        });
        
        document.getElementById('modalBody').innerHTML = html;
        document.getElementById('modal').style.display = 'flex';
    }

    function buyItem(shopType, itemName) {
        const shop = shops[shopType];
        const item = shop.items.find(i => i.name === itemName);
        
        if (shopType === 'merchant') {
            if (gameState.resources >= 1) {
                gameState.resources--;
                gameState.coins += item.price;
                showNotification(`💸 Продано! +${item.price} монет`);
                updateUI();
                closeModal();
                openShop('merchant');
            } else {
                showNotification("❌ Нет ресурсов для продажи!");
            }
            return;
        }
        
        if (gameState.coins >= item.price) {
            gameState.coins -= item.price;
            
            if (item.effect.damage) {
                gameState.damage += item.effect.damage;
                showNotification(`⚔️ Урон увеличен на ${item.effect.damage}!`);
            }
            if (item.effect.hpBonus) {
                gameState.maxHp += item.effect.hpBonus;
                gameState.hp = gameState.maxHp;
                showNotification(`❤️ Максимальное HP увеличено на ${item.effect.hpBonus}!`);
            }
            
            updateUI();
            closeModal();
        } else {
            showNotification("❌ Недостаточно монет!");
        }
    }

    function openQuests() {
        let html = `
            <h3>📜 Активный квест</h3>
            <div class="shop-item">
                <div>
                    <strong>${activeQuest.name}</strong><br>
                    <small>Прогресс: ${activeQuest.progress}/${activeQuest.required}</small><br>
                    <small>Награда: ${activeQuest.reward.coins}💰 + ${activeQuest.reward.exp}⭐</small>
                </div>
                ${activeQuest.completed ? '<span style="color:#ffd700;">✅ ВЫПОЛНЕН</span>' : ''}
            </div>
        `;
        
        if (activeQuest.completed) {
            html += `<button class="buy-btn" onclick="claimQuestReward()" style="width:100%; margin-top:10px;">Получить награду</button>`;
        }
        
        document.getElementById('modalBody').innerHTML = html;
        document.getElementById('modal').style.display = 'flex';
    }

    function claimQuestReward() {
        if (activeQuest.completed) {
            gameState.coins += activeQuest.reward.coins;
            addExp(activeQuest.reward.exp);
            showNotification(`🎁 Награда получена! +${activeQuest.reward.coins}💰 +${activeQuest.reward.exp}⭐`);
            
            activeQuest = {
                name: "Победить 5 монстров",
                progress: 0,
                required: 5,
                reward: { coins: 80, exp: 50 },
                completed: false
            };
            updateUI();
            closeModal();
        }
    }

    function closeModal() {
        document.getElementById('modal').style.display = 'none';
    }

    function loadSave() {
        const saved = localStorage.getItem('soulKnightSave');
        if (saved) {
            try {
                const data = JSON.parse(saved);
                Object.assign(gameState, data);
                updateUI();
            } catch(e) {}
        }
        
        if (window.Telegram && window.Telegram.WebApp) {
            window.Telegram.WebApp.ready();
            window.Telegram.WebApp.expand();
        }
    }

    function saveGame() {
        localStorage.setItem('soulKnightSave', JSON.stringify(gameState));
    }

    setInterval(saveGame, 5000);
    loadSave();
    updateUI();
</script>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
</body>
</html>"""

# Обработчики команд бота
@dp.message(Command("start"))
async def start_command(message: types.Message):
    """Обработчик команды /start"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎮 Запустить Soul Knight",
            web_app=WebAppInfo(url="https://your-app.onrender.com")  # Замените на ваш URL
        )],
        [InlineKeyboardButton(
            text="📖 Как играть",
            callback_data="how_to_play"
        )]
    ])
    
    await message.answer(
        "🌟 **Добро пожаловать в Soul Knight!** 🌟\n\n"
        "⚔️ Сражайся с монстрами\n"
        "💰 Собирай монеты и ресурсы\n"
        "🛡️ Покупай оружие и баффы\n"
        "📜 Выполняй квесты\n\n"
        "Нажми на кнопку ниже, чтобы начать приключение!",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@dp.callback_query()
async def handle_callbacks(callback: types.CallbackQuery):
    """Обработчик callback кнопок"""
    if callback.data == "how_to_play":
        await callback.message.answer(
            "📖 **Как играть в Soul Knight:**\n\n"
            "1️⃣ **Битва** - Нажми на портал, чтобы отправиться в бой\n"
            "2️⃣ **Атака** - Нажимай на кнопки атаки для удара по врагам\n"
            "3️⃣ **Магазины** - Покупай оружие у Кузнеца\n"
            "4️⃣ **Баффы** - Улучшай характеристики у Алхимика\n"
            "5️⃣ **Ресурсы** - Продавай ресурсы Скупщику за монеты\n\n"
            "💡 Совет: Чем выше твой уровень, тем сильнее враги и лучше награды!",
            parse_mode="Markdown"
        )
    await callback.answer()

# Веб-сервер для отдачи HTML
async def handle(request):
    return web.Response(text=GAME_HTML, content_type='text/html')

async def main():
    # Запускаем веб-сервер
    app = web.Application()
    app.router.add_get('/', handle)
    app.router.add_get('/game', handle)  # На оба пути отвечаем
    app.router.add_get('/game.html', handle)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    
    print("🌐 Веб-сервер запущен на порту 8080")
    print("🤖 Бот Soul Knight запущен!")
    
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
