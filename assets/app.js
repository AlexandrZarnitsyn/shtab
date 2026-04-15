


const API_BASE =
  window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost"
    ? "http://127.0.0.1:8000"
    : "";
const SESSION_KEY='shtab_backend_session_v1';
const SUPERADMIN_EMAIL='s.zarnitsyn@yandex.ru';

const PREF_THEME_KEY='shtab_theme_v1';
const PREF_LANG_KEY='shtab_lang_v1';

const TRANSLATIONS = {
  en: {
    'ШТАБ — главная админка': 'SHTAB — admin panel',
    'ШТАБ — панель': 'SHTAB — dashboard',
    'ШТАБ — настройки компании': 'SHTAB — company settings',
    'ШТАБ — детали SKU': 'SHTAB — SKU details',
    'ШТАБ — вход': 'SHTAB — sign in',
    'ШТАБ — регистрация': 'SHTAB — sign up',
    'ШТАБ — управление закупками, прибылью и командой': 'SHTAB — procurement, profit and team management',
    'Рабочее пространство для команды': 'Workspace for your team',
    'Новый аккаунт': 'New account',
    'Регистрация по приглашению': 'Register by invite',
    'Главная админка': 'Main admin panel',
    'Клиенты': 'Clients',
    'Выдача доступа': 'Grant access',
    'История оплат': 'Payment history',
    'Выйти': 'Sign out',
    'Организации': 'Organizations',
    'Настройки': 'Settings',
    'Панель': 'Dashboard',
    'Сегодня': 'Today',
    'Закупки': 'Procurement',
    'Финансы': 'Finance',
    'Команда': 'Team',
    'Тариф': 'Plan',
    'Вход': 'Sign in',
    'Создать аккаунт': 'Create account',
    'Начать работу': 'Get started',
    'Один центр управления': 'One control center',
    'Серверная логика уже подключена': 'Server logic is already connected',
    'Новый визуальный стиль': 'New visual style',
    'Регистрация': 'Sign up',
    'Создай доступ в систему': 'Create your access',
    'Имя и фамилия': 'Full name',
    'Пароль': 'Password',
    'Войти': 'Sign in',
    'Уже есть аккаунт?': 'Already have an account?',
    'Нет аккаунта?': "Don't have an account?",
    'Зарегистрироваться': 'Sign up',
    'Возвращайтесь к ежедневным решениям быстрее': 'Get back to daily decisions faster',
    'Открывайте рабочие области, смотрите риски по товарам, обновляйте ассортимент CSV и управляйте командой из одного интерфейса.': 'Open workspaces, monitor product risks, update your CSV assortment, and manage your team from one interface.',
    'Запустите рабочее пространство за несколько минут': 'Launch your workspace in minutes',
    'После регистрации можно создать организацию, загрузить CSV и перейти в рабочую область. Тариф выдаётся отдельно администратором.': 'After registration, create an organization, upload CSV data, and enter your workspace. Access is granted separately by the administrator.',
    'Создай профиль и войди в компанию по приглашению': 'Create a profile and enter the company by invite',
    'В этом сценарии тариф выбирать не нужно: аккаунт создастся без собственного тарифа, а доступ сразу откроется в приглашённую компанию.': 'In this flow, you do not choose a plan: the account is created without its own plan, and access opens directly to the invited company.',
    'Заполни все поля.': 'Fill in all fields.',
    'Введите email и пароль.': 'Enter your email and password.',
    'Вернись в рабочее пространство': 'Return to your workspace',
    'Операционная система для селлеров маркетплейсов': 'Operating system for marketplace sellers',
    'SaaS для Ozon, WB и Яндекс Маркета': 'SaaS for Ozon, WB and Yandex Market',
    'Держи в одном месте товары, деньги, закупки и доступы команды': 'Keep products, money, procurement, and team access in one place',
    'ШТАБ помогает селлерам и небольшим командам видеть остатки, сроки закупки, состояние доступа и рабочую картину по организации — без перегруженных таблиц и лишних действий.': 'SHTAB helps sellers and small teams track stock, replenishment timing, access status, and the full picture of each organization without overloaded tables or extra steps.',
    'Как это выглядит в работе': 'How it works in practice',
    'Пользователь создаёт организацию, ты выдаёшь доступ, и только после этого открываются рабочие разделы': 'A user creates an organization, you grant access, and only then do the working sections open',
    'Пользователь заходит в систему и создаёт организацию без выбора тарифа.': 'The user enters the system and creates an organization without choosing a plan.',
    'Связь с тобой': 'Contact you',
    'На экране доступа он видит контакты Telegram и VK для получения тарифа.': 'On the access screen, the user sees your Telegram and VK contacts to get a plan.',
    'Выдача из админки': 'Granted from the admin panel',
    'Ты активируешь доступ из своего админ-аккаунта и организация начинает работать.': 'You activate access from your admin account and the organization starts working.',
    'Для запуска без лишней сложности': 'For a simple launch',
    'Подходит для первых продаж и пилотных клиентов': 'Suitable for first sales and pilot clients',
    'Такой сценарий позволяет тебе вручную управлять доступами, тестировать спрос и не перегружать продукт ненужной оплатой на старте.': 'This flow lets you manage access manually, test demand, and avoid unnecessary payment integrations at the start.',
    'Фокус сейчас:': 'Current focus:',
    'понятный вход, аккуратный интерфейс, ручная выдача доступа и контроль над клиентами из одной админ-панели.': 'clear onboarding, a clean interface, manual access granting, and client control from one admin panel.',
    'Выбери организацию слева.': 'Choose an organization on the left.',
    'Период, дн.': 'Period, days',
    'Быстрый срок': 'Quick duration',
    'Продлить на 30 дн.': 'Extend for 30 days',
    'Продлить на 90 дн.': 'Extend for 90 days',
    'Продлить на 365 дн.': 'Extend for 365 days',
    'Выдать тариф': 'Grant plan',
    'Снять доступ': 'Remove access',
    'История ручных оплат': 'Manual payment history',
    'Поиск по названию или email владельца': 'Search by organization name or owner email',
    'Организации не найдены.': 'No organizations found.',
    'Рабочее пространство': 'Workspace',
    'Операционный центр управления': 'Operations control center',
    'Главные действия вынесены наверх, разделы собраны в компактную навигацию, а не спрятаны в длинной левой колонке.': 'Key actions are placed up top, and sections are grouped in compact navigation instead of a long left sidebar.',
    'Быстрые переходы': 'Quick links',
    'Сменить рабочую область': 'Switch workspace',
    'Импорт, команда и тариф': 'Import, team, and plan',
    'Корпоративная система управления': 'Corporate management system',
    'Управление компанией, импортами и командой': 'Company, import, and team management',
    'Приглашения пользователей': 'User invitations',
    'Роль': 'Role',
    'Отправить приглашение': 'Send invitation',
    'Общие настройки': 'General settings',
    'Название компании': 'Company name',
    'Тариф продукта': 'Product plan',
    'Основной маркетплейс': 'Primary marketplace',
    'Сохранить изменения': 'Save changes',
    'Обновление данных': 'Data update',
    'Заменить CSV внутри организации': 'Replace CSV inside the organization',
    'Можно загрузить новый CSV и полностью заменить текущий товарный набор в этой организации без создания новой рабочей области.': 'You can upload a new CSV and fully replace the current product set in this organization without creating a new workspace.',
    'Скачать шаблон CSV': 'Download CSV template',
    'Загрузить демо-данные': 'Load demo data',
    'Выбрать новый CSV': 'Choose new CSV',
    'Применить новый CSV к организации': 'Apply new CSV to organization',
    'Последние обновления товаров': 'Recent product updates',
    'Состав команды': 'Team members',
    'Отправленные приглашения': 'Sent invitations',
    'Журнал действий': 'Activity log',
    'Карточка товара': 'Product card',
    'В панель': 'Back to dashboard',
    'Динамика спроса': 'Demand trend',
    'Финансовая структура': 'Financial structure',
    'Финансовый разбор': 'Financial analysis',
    'Рекомендации': 'Recommendations',
    'Тема': 'Theme',
    'Язык': 'Language',
    'Светлая': 'Light',
    'Тёмная': 'Dark',
    'Контакты для доступа': 'Access contacts',
    'Напиши мне, чтобы получить или продлить доступ к организации.': 'Message me to get or extend organization access.',
    'Доступ не активирован': 'Access not activated',
    'Доступ закончился': 'Access expired',
    'Пустая рабочая область': 'Empty workspace'
  }
};

const PARTIAL_TRANSLATIONS = {
  en: {
    ' · ': ' · ',
    'Тариф: ': 'Plan: ',
    'Роль: ': 'Role: ',
    'Основной маркетплейс: ': 'Primary marketplace: ',
    'Тариф продукта': 'Product plan',
    'Оплачено': 'Paid',
    'Заблокировано': 'Blocked',
    'Ожидает оплаты': 'Awaiting activation',
    'Без активного тарифа': 'No active plan',
    'Доступ до ': 'Access until ',
    'Доступ закончился ': 'Access expired ',
    'Открыть': 'Open',
    'Рабочая область': 'Workspace',
    'Новых SKU': 'New SKUs',
    'Обновится SKU': 'Updated SKUs',
    'Удалится SKU': 'Removed SKUs',
    'Предпросмотр': 'Preview',
    'Сравнение с текущими данными': 'Compare with current data',
    'Перед заменой видно, что именно изменится в организации.': 'See exactly what will change before replacing data in the organization.',
    'Скрыто ролью': 'Hidden by role',
    'Маржа портфеля': 'Portfolio margin',
    'SKU под контролем': 'SKUs to watch',
    'Согласовать закупку ': 'Approve restock of ',
    ' шт.': ' pcs',
    'Проверить восстановление маржи': 'Review margin recovery',
    'Хватит на ': 'Coverage ',
    ' дн.': ' days',
    ' при сроке поставки ': ' with lead time ',
    'Вклад в прибыль ': 'Profit contribution ',
    ' на единицу': ' per unit',
    'Сейчас нет критичных действий. По текущим данным ситуация стабильна.': 'There are no critical actions right now. The current situation looks stable.',
    'Самый заметный риск сейчас — ': 'The main risk right now is ',
    'Самый слабый вклад в прибыль у товара ': 'The weakest profit contribution comes from ',
    'Средняя маржа портфеля — ': 'Average portfolio margin is ',
    'рекламная эффективность — ': 'ad efficiency is ',
    'Финансовые показатели скрыты для этой роли. Основной фокус — остатки, риски и операционные действия.': 'Financial metrics are hidden for this role. Focus on stock, risks, and operational actions.',
    'Прогноз на 30 дн.: выручка ': '30-day forecast: revenue ',
    'прибыль ': 'profit ',
    'Прогноз появится после загрузки товаров.': 'The forecast will appear after products are loaded.',
    'Закупка: ': 'Restock: ',
    'Хватит примерно на ': 'Stock will last for about ',
    'ожидаемая дата риска — ': 'estimated risk date — ',
    'Маржа: ': 'Margin: ',
    'Стоит проверить цену ': 'Review price ',
    'и рекомендованную цену ': 'and recommended price ',
    'Реклама: ': 'Ads: ',
    '— реклама может не окупаться.': '— ads may not pay back.',
    'Срочно': 'Urgent',
    'Контроль': 'Monitor',
    'Критичных уведомлений по текущим данным нет.': 'There are no critical notifications right now.',
    'Высокий': 'High',
    'Средний': 'Medium',
    'Низкий': 'Low',
    'Критичные позиции': 'Critical items',
    'Средний риск': 'Medium risk',
    'Потенциальный заказ': 'Potential order',
    'Рекомендуемый объём дозакупки: ': 'Recommended reorder volume: ',
    'По текущим данным срочные закупки не требуются.': 'No urgent procurement is needed based on current data.',
    'Выручка': 'Revenue',
    'Прибыль': 'Profit',
    'Остатки': 'Stock',
    'Комиссия': 'Commission',
    'Логистика': 'Logistics',
    'Реклама': 'Ads',
    'Чистая прибыль': 'Net profit',
    'Цена безубыточности': 'Break-even price',
    'Рекомендованная цена': 'Recommended price',
    'Дней покрытия': 'Days of cover',
    'Следующая закупка': 'Next purchase',
    'Ожидаемая дата риска': 'Expected risk date',
    'Нет данных по выбранному SKU.': 'No data for the selected SKU.',
    'Загрузка организаций...': 'Loading organizations...',
    'У тебя пока нет организаций. Нажми “Создать новую”.': 'You do not have organizations yet. Click “Create new”.',
    'Выбери нужную организацию, переключайся между компаниями и отслеживай доступ по каждой из них.': 'Choose an organization, switch between companies, and track access for each of them.',
    'Создать новую': 'Create new',
    'Пока пусто': 'Nothing here yet',
    'Организация без активного доступа пока остаётся пустой. Чтобы открыть рабочие разделы, напиши мне в Telegram или ВКонтакте.': 'An organization without active access stays empty for now. To unlock the workspace, message me on Telegram or VK.',
    'Написать в Telegram': 'Message on Telegram',
    'Написать во ВКонтакте': 'Message on VK',
    'Название': 'Name',
    'Владелец': 'Owner',
    'Дата выдачи': 'Granted on',
    'Дата окончания': 'Ends on',
    'Период': 'Period',
    'Пользователь': 'User',
    'Компания': 'Company',
    'Полное имя': 'Full name',
    'Email': 'Email',
    'Создать организацию': 'Create organization',
    'Перейти в рабочую область': 'Open workspace',
    'Принять приглашение': 'Accept invite',
    'Мои организации': 'My organizations',
    'Если аккаунта ещё нет, создай его прямо по приглашению — без выбора тарифа. Если аккаунт уже есть, просто войди и подтверди участие.': 'If you do not have an account yet, create it right from the invite — no plan selection required. If you already have an account, just sign in and confirm participation.',
    'Вступление в организацию': 'Join organization',
    'Принятие приглашения': 'Invite acceptance',
    'Создай компанию и загрузи первые данные': 'Create a company and upload your first data',
    'Укажи базовые параметры организации и при необходимости загрузи CSV с товарами. После создания рабочая область появится сразу, но разделы откроются только после выдачи доступа.': 'Set the basic organization parameters and optionally upload a CSV with products. The workspace appears immediately, but sections unlock only after access is granted.',
    'Загрузи CSV позже': 'Upload CSV later',
    'Создать компанию': 'Create company',
    'Организации и доступы': 'Organizations and access',
    'Выбери нужную организацию, переключайся между компаниями и отслеживай доступ по каждой из них.': 'Choose an organization, switch between companies, and track access for each one.',
    'Доступ выдаётся только администратором': 'Access is granted only by the administrator',
    'Самостоятельно выбрать тариф больше нельзя. Чтобы подключить или продлить доступ, напиши мне напрямую в один из каналов ниже.': 'Self-service plan selection is disabled. To activate or extend access, contact me directly using one of the channels below.',
    'Текущий статус': 'Current status',
    'Контакты': 'Contacts',
    'Активный доступ': 'Active access',
    'Скоро закончится': 'Expiring soon',
    'Нет доступа': 'No access',
    'Главная админка': 'Main admin panel',
    'Только этот аккаунт может вручную выдавать тарифы, продлевать срок доступа и контролировать организации клиентов.': 'Only this account can grant plans manually, extend access, and manage client organizations.',
    'Найди организацию, выбери срок и сразу открой доступ без автоматической оплаты.': 'Find an organization, choose a duration, and grant access immediately without automatic payments.',
    'Срок, дн.': 'Duration, days',
    'Быстрые действия': 'Quick actions',
    'Последние активации': 'Recent activations',
    'Инвайт': 'Invite',
    'Рабочее пространство для команды': 'Workspace for your team',
    'Рабочее пространство': 'Workspace',
    'Карточка товара': 'Product card',
    'Корпоративная система управления': 'Corporate management system',
    'Корпоративная система управления': 'Corporate management system'
  }
};

function getThemePreference(){ return localStorage.getItem(PREF_THEME_KEY) || document.documentElement.getAttribute('data-theme') || 'light'; }
function getLanguagePreference(){ return 'ru'; }
const __i18nTextNodes = new WeakMap();
function translateString(value, lang){
  if(lang !== 'en' || value == null) return value;
  let result = (TRANSLATIONS.en && TRANSLATIONS.en[value]) || value;
  const parts = Object.entries(PARTIAL_TRANSLATIONS.en || {}).sort((a,b)=>b[0].length-a[0].length);
  for(const [ru,en] of parts){
    if(result.includes(ru)) result = result.split(ru).join(en);
  }
  return result;
}
function applyTheme(theme){
  const finalTheme = theme === 'dark' ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', finalTheme);
  if(document.body) document.body.setAttribute('data-theme', finalTheme);
  localStorage.setItem(PREF_THEME_KEY, finalTheme);
  syncTopSwitchDock();
}
function translateAttributes(lang){
  document.querySelectorAll('input[placeholder], textarea[placeholder]').forEach(el=>{
    if(!el.hasAttribute('data-i18n-placeholder-ru')) el.setAttribute('data-i18n-placeholder-ru', el.getAttribute('placeholder') || '');
    const ru = el.getAttribute('data-i18n-placeholder-ru') || '';
    el.setAttribute('placeholder', lang === 'en' ? translateString(ru, 'en') : ru);
  });
}
function translateNodeTree(root, lang){
  if(!root) return;
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
    acceptNode(node){
      if(!node.nodeValue || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
      if(node.parentElement && ['SCRIPT','STYLE'].includes(node.parentElement.tagName)) return NodeFilter.FILTER_REJECT;
      return NodeFilter.FILTER_ACCEPT;
    }
  });
  const nodes=[];
  while(walker.nextNode()) nodes.push(walker.currentNode);
  nodes.forEach(node=>{
    if(!__i18nTextNodes.has(node)) __i18nTextNodes.set(node, node.nodeValue);
    const original = __i18nTextNodes.get(node);
    node.nodeValue = lang === 'en' ? translateString(original, 'en') : original;
  });
}
function applyLanguage(lang){
  const finalLang = 'ru';
  try{ localStorage.setItem(PREF_LANG_KEY, finalLang); }catch(e){}
  document.documentElement.setAttribute('lang', finalLang);
  const title=document.querySelector('title');
  if(title && title.dataset.ruTitle){ title.textContent = title.dataset.ruTitle; }
  document.querySelectorAll('[data-i18n-ru]').forEach(el=>{
    const ru = el.getAttribute('data-i18n-ru') || el.textContent;
    el.textContent = ru;
  });
  syncTopSwitchDock();
}
function injectPreferencesPanel(){
  if(document.getElementById('topSwitchDock') || !document.body) return;
  const dock=document.createElement('div');
  dock.id='topSwitchDock';
  dock.className='top-switch-dock';
  dock.innerHTML = `
    <button type="button" id="themeSwitch" class="top-switch top-switch-theme" aria-label="Переключить тему">
      <span class="theme-switch-track">
        <span class="theme-switch-icon theme-switch-icon-sun">☀️</span>
        <span class="theme-switch-thumb"></span>
        <span class="theme-switch-icon theme-switch-icon-moon">🌙</span>
      </span>
    </button>`;
  document.body.appendChild(dock);
  dock.querySelector('#themeSwitch').addEventListener('click', ()=>{
    applyTheme(getThemePreference() === 'dark' ? 'light' : 'dark');
  });
  syncTopSwitchDock();
}
function syncTopSwitchDock(){
  const dock=document.getElementById('topSwitchDock');
  if(!dock) return;
  const themeSwitch=dock.querySelector('#themeSwitch');
  const dark = getThemePreference() === 'dark';
  if(themeSwitch) themeSwitch.classList.toggle('is-on', dark);
  if(themeSwitch) themeSwitch.title = dark ? 'Тёмная тема' : 'Светлая тема';
}
function initUiPreferences(){ try{ applyTheme(getThemePreference()); injectPreferencesPanel(); applyLanguage('ru'); }catch(e){} }
window.applyTheme = applyTheme; window.applyLanguage = applyLanguage; window.initUiPreferences = initUiPreferences;



function markPageReady(){
  try{
    if(document.body){
      document.body.classList.remove('page-loading');
      document.body.classList.add('page-ready');
      try{ try{ localStorage.setItem(PREF_LANG_KEY,'ru'); }catch(e){}
initUiPreferences(); }catch(e){}
    }
  }catch(e){}
}
window.markPageReady = markPageReady;
initUiPreferences();

const demoProducts=[
{id:'SKU-1001',account:'Мой бренд / Основной кабинет',name:'Термокружка 350 мл',channel:'Ozon',warehouse:'Хоругвино',price:1490,unitCost:510,stock:120,reserved:10,inbound:40,leadTimeDays:14,avgDailySales:9,trend:0.12,commissionRate:0.18,logisticsPerUnit:95,adSpend:12000,returnRate:0.03},
{id:'SKU-1002',account:'Мой бренд / Основной кабинет',name:'Органайзер для кухни',channel:'WB',warehouse:'Коледино',price:990,unitCost:330,stock:260,reserved:12,inbound:0,leadTimeDays:18,avgDailySales:7,trend:-0.05,commissionRate:0.21,logisticsPerUnit:78,adSpend:9500,returnRate:0.04},
{id:'SKU-1003',account:'Мой бренд / Дополнительный кабинет',name:'Набор контейнеров детский',channel:'Яндекс Маркет',warehouse:'Софьино',price:1590,unitCost:610,stock:52,reserved:4,inbound:0,leadTimeDays:20,avgDailySales:9,trend:0.28,commissionRate:0.15,logisticsPerUnit:110,adSpend:8000,returnRate:0.03}
];

const csvTemplate=`id,account,name,channel,warehouse,price,unitCost,stock,reserved,inbound,leadTimeDays,avgDailySales,trend,commissionRate,logisticsPerUnit,adSpend,returnRate
SKU-1001,Мой бренд / Основной кабинет,Термокружка 350 мл,Ozon,Хоругвино,1490,510,120,10,40,14,9,0.12,0.18,95,12000,0.03
SKU-1002,Мой бренд / Основной кабинет,Органайзер для кухни,WB,Коледино,990,330,260,12,0,18,7,-0.05,0.21,78,9500,0.04`;

function money(n){const locale=getLanguagePreference()==='en'?'en-US':'ru-RU'; return new Intl.NumberFormat(locale,{style:'currency',currency:'RUB',maximumFractionDigits:0}).format(n||0);}
function pct(n,d=1){const raw=Number(n||0).toFixed(d); return `${getLanguagePreference()==='en'?raw:raw.replace('.',',')}%`;}
function ratio(n,d=2){ if(n==null) return '—'; const raw=Number(n).toFixed(d); return `${getLanguagePreference()==='en'?raw:raw.replace('.',',')}x`; }
function fmtDate(value){ if(!value) return '—'; const dt=new Date(value); const locale=getLanguagePreference()==='en'?'en-US':'ru-RU'; return Number.isNaN(dt.getTime()) ? value : dt.toLocaleString(locale); }

function declension(number, words){
  number = Math.abs(Number(number) || 0) % 100;
  const n1 = number % 10;
  if(number > 10 && number < 20) return words[2];
  if(n1 > 1 && n1 < 5) return words[1];
  if(n1 === 1) return words[0];
  return words[2];
}
function getSession(){const raw=localStorage.getItem(SESSION_KEY); return raw?JSON.parse(raw):{token:null,user:null,org:null};}
function setSession(next){localStorage.setItem(SESSION_KEY, JSON.stringify(next));}
async function clearSession(){try{await api('/api/v1/auth/logout',{method:'POST'});}catch{} localStorage.removeItem(SESSION_KEY); window.location='index.html';}
function requireSession(){const s=getSession(); if(!s.token){window.location='login.html'; return null;} return s;}

const TARIFF_LABELS = {
  none: 'Не назначен',
  starter: 'Старт',
  growth: 'Рост',
  enterprise: 'Корпоративный'
};

const TARIFF_FEATURES = {
  none: {dashboard:false, procurement:false, finance:false, team:false, sku_details:false, import_history:false, audit_log:false, forecasting:false, max_users:1, max_sku:500},
  starter: {dashboard:true, procurement:false, finance:false, team:false, sku_details:false, import_history:false, audit_log:false, forecasting:false, max_users:2, max_sku:500},
  growth: {dashboard:true, procurement:true, finance:true, team:true, sku_details:true, import_history:true, audit_log:true, forecasting:true, max_users:5, max_sku:5000},
  enterprise: {dashboard:true, procurement:true, finance:true, team:true, sku_details:true, import_history:true, audit_log:true, forecasting:true, max_users:9999, max_sku:999999}
};

const ROLE_PERMISSIONS = {
  'Руководитель': {manage_org:true, manage_billing:true, manage_team:true, manage_products:true, view_finance:true, view_team:true, view_audit:true, view_sku_details:true},
  'Финансы': {manage_org:false, manage_billing:false, manage_team:false, manage_products:false, view_finance:true, view_team:false, view_audit:false, view_sku_details:true},
  'Закупки': {manage_org:false, manage_billing:false, manage_team:false, manage_products:true, view_finance:false, view_team:false, view_audit:false, view_sku_details:true},
  'Оператор': {manage_org:false, manage_billing:false, manage_team:false, manage_products:false, view_finance:false, view_team:false, view_audit:false, view_sku_details:false}
};

function currentRole(org){
  return (org || getSession().org || {}).current_role || 'Оператор';
}
function rolePermissions(org){
  return ROLE_PERMISSIONS[currentRole(org)] || ROLE_PERMISSIONS['Оператор'];
}
function canRole(permissionName, org){
  return !!rolePermissions(org)[permissionName];
}
function hiddenMoney(value, placeholder='Скрыто ролью'){
  return value == null ? placeholder : money(value);
}
function hiddenPct(value, placeholder='Скрыто ролью'){
  return value == null ? placeholder : pct(value||0);
}
function formatTariff(code){
  return TARIFF_LABELS[code] || code || '—';
}
function billingStatusLabel(org){
  return org.billing_status === 'active' ? 'Оплачено' : org.billing_status === 'blocked' ? 'Заблокировано' : 'Ожидает оплаты';
}
function billingStatusClass(org){
  return org.billing_status === 'active' ? 'green' : org.billing_status === 'blocked' ? 'red' : 'amber';
}
function billingNoticeHtml(org){
  if(!org) return '';
  const note = org.billing_notice || '';
  if(note) return `<div class="badge ${billingStatusClass(org)}">${note}</div>`;
  if(org.billing_status === 'active' && org.paid_until) return `<div class="badge soft">Доступ до ${org.paid_until}</div>`;
  if(org.billing_status === 'blocked' && org.paid_until) return `<div class="badge red">Доступ закончился ${org.paid_until}</div>`;
  return `<div class="badge amber">Без активного тарифа</div>`;
}
function getTariffFeatures(code){
  return TARIFF_FEATURES[code] || TARIFF_FEATURES.starter;
}
function canUse(featureName, org){
  const features = getTariffFeatures((org || getSession().org || {}).tariff_code || 'none');
  return !!features[featureName];
}
function isSuperAdmin(sessionOrUser){
  const email = (sessionOrUser?.user?.email || sessionOrUser?.email || getSession()?.user?.email || '').toLowerCase();
  return email === SUPERADMIN_EMAIL;
}
function requireActiveBilling(redirect=true){
  const s=getSession();
  if(!s.token){ if(redirect) window.location='login.html'; return null; }
  if(!s.org){ if(redirect) window.location='organizations.html'; return null; }
  const status = s.org.billing_status || 'pending_payment';
  if(status !== 'active'){
    if(redirect) window.location='billing.html';
    return null;
  }
  return s;
}
async function api(path, options={}){
  const s=getSession(); const headers=Object.assign({}, options.headers||{});
  if(s.token) headers['Authorization']=`Bearer ${s.token}`;
  if(options.body && !(options.body instanceof FormData) && !headers['Content-Type']) headers['Content-Type']='application/json';
  const res=await fetch(`${API_BASE}${path}`, {...options, headers});
  const text=await res.text();
  let data=null; try{data=text?JSON.parse(text):null;}catch{data=text;}
  if(!res.ok){ throw new Error(data && data.detail ? data.detail : `HTTP ${res.status}`); }
  return data;
}
function splitCsvLine(line){const result=[]; let current=''; let inQuotes=false; for(let i=0;i<line.length;i++){const ch=line[i]; if(ch=='"'){ if(inQuotes && line[i+1]=='"'){current+='"'; i++;} else inQuotes=!inQuotes; } else if(ch===',' && !inQuotes){result.push(current.trim()); current='';} else current+=ch;} result.push(current.trim()); return result;}
function parseCSV(text){
  const lines=text.trim().split(/\r?\n/).filter(Boolean);
  if(lines.length<2) return {rows:[],errors:['Файл должен содержать заголовок и хотя бы одну строку данных.']};
  const headers=splitCsvLine(lines[0]);
  const required=['id','account','name','channel','warehouse','price','unitCost','stock','reserved','inbound','leadTimeDays','avgDailySales','trend','commissionRate','logisticsPerUnit','adSpend','returnRate'];
  const missing=required.filter(h=>!headers.includes(h)); if(missing.length) return {rows:[],errors:['Не хватает колонок: '+missing.join(', ')]};
  const rows=[],errors=[]; const num=v=>Number(String(v).replace(',','.')); const seenIds=new Set();
  for(let i=1;i<lines.length;i++){
    const values=splitCsvLine(lines[i]); const row=Object.fromEntries(headers.map((h,idx)=>[h, values[idx] ?? '']));
    if(!row.id || !row.account || !row.name){errors.push(`Строка ${i+1}: обязательные поля id, account и name должны быть заполнены.`); continue;}
    if(!row.channel || !row.warehouse){errors.push(`Строка ${i+1}: channel и warehouse должны быть заполнены.`); continue;}
    const idKey=String(row.id).trim().toLowerCase();
    if(seenIds.has(idKey)){errors.push(`Строка ${i+1}: найден дубликат id/SKU ${row.id}.`); continue;}
    seenIds.add(idKey);
    const parsed={id:row.id,account:row.account,name:row.name,channel:row.channel,warehouse:row.warehouse,price:num(row.price),unitCost:num(row.unitCost),stock:num(row.stock),reserved:num(row.reserved),inbound:num(row.inbound),leadTimeDays:num(row.leadTimeDays),avgDailySales:num(row.avgDailySales),trend:num(row.trend),commissionRate:num(row.commissionRate),logisticsPerUnit:num(row.logisticsPerUnit),adSpend:num(row.adSpend),returnRate:num(row.returnRate)};
    const bad=Object.entries(parsed).filter(([k,v])=>typeof v==='number' && Number.isNaN(v)).map(([k])=>k);
    if(bad.length){errors.push(`Строка ${i+1}: ошибка в числовых полях ${bad.join(', ')}.`); continue;}
    const negative=['price','unitCost','stock','reserved','inbound','leadTimeDays','avgDailySales','logisticsPerUnit','adSpend'].filter(k=>parsed[k]<0);
    if(negative.length){errors.push(`Строка ${i+1}: отрицательные значения недопустимы в полях ${negative.join(', ')}.`); continue;}
    if(parsed.commissionRate<0 || parsed.commissionRate>1 || parsed.returnRate<0 || parsed.returnRate>1){errors.push(`Строка ${i+1}: commissionRate и returnRate должны быть в диапазоне от 0 до 1.`); continue;}
    rows.push(parsed);
  }
  return {rows,errors};
}
function downloadTemplate(){const blob=new Blob([csvTemplate],{type:'text/csv;charset=utf-8;'}); const url=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url; a.download='shtab_template.csv'; a.click(); URL.revokeObjectURL(url);}
function toApiProduct(r){return {sku:r.id,account:r.account,name:r.name,channel:r.channel,warehouse:r.warehouse,price:r.price,unit_cost:r.unitCost,stock:r.stock,reserved:r.reserved,inbound:r.inbound,lead_time_days:r.leadTimeDays,avg_daily_sales:r.avgDailySales,trend:r.trend,commission_rate:r.commissionRate,logistics_per_unit:r.logisticsPerUnit,ad_spend:r.adSpend,return_rate:r.returnRate};}

async function renderOrganizations(){
  const s=requireSession(); if(!s) return;
  if(isSuperAdmin(s)){ window.location='admin.html'; return; }
  const who=document.getElementById('who'); if(who) who.textContent=`${s.user.full_name} · ${s.user.email}`;
  const holder=document.getElementById('orgList'); holder.innerHTML='<div class="notice">Загрузка организаций...</div>';
  try{
    const orgs=await api('/api/v1/organizations');
    if(!orgs.length){holder.innerHTML='<div class="item empty-block"><h3>Пока нет организаций</h3><p class="small">Создай первую организацию, чтобы загрузить товары и увидеть аналитику.</p><a class="btn primary" href="onboarding.html">Создать организацию</a></div>'; return;}
    holder.innerHTML='';
    orgs.forEach(org=>{
      const div=document.createElement('div'); div.className='item';
      const openLabel = org.billing_status === 'active' ? 'Открыть' : 'Рабочая область';
      div.innerHTML=`<div class="item-top"><div><h3>${org.name}</h3>
    <p class="small">Тариф: ${formatTariff(org.tariff_code)} · Роль: ${org.current_role || '—'} · Основной маркетплейс: ${org.marketplace||'—'}</p></div><span class="badge ${billingStatusClass(org)}">${billingStatusLabel(org)}</span></div><div class="actions">${billingNoticeHtml(org)}<button class="btn primary" data-open>${openLabel}</button><button class="btn secondary" data-settings>Настройки</button></div>`;
      div.querySelector('[data-open]').onclick=()=>{setSession({...getSession(), org}); window.location = 'app.html';};
      div.querySelector('[data-settings]').onclick=()=>{setSession({...getSession(), org}); window.location='settings.html';};
      holder.appendChild(div);
    });
  }catch(err){holder.innerHTML=`<div class="error">${err.message}</div>`;}
}



function renderLineChart(svgId, values){
  const svg=document.getElementById(svgId);
  if(!svg) return;
  const w=600, h=220, left=24, right=18, top=16, bottom=28;
  const innerW=w-left-right, innerH=h-top-bottom;
  const max=Math.max(...values,1);
  const step=innerW/Math.max(values.length-1,1);
  const points=values.map((v,i)=>{
    const x=left+i*step;
    const y=top+innerH-(v/max)*innerH;
    return [x,y];
  });
  const line=points.map((p,i)=>`${i===0?'M':'L'} ${p[0]} ${p[1]}`).join(' ');
  const area=`M ${left} ${top+innerH} ` + points.map((p,i)=>`${i===0?'L':'L'} ${p[0]} ${p[1]}`).join(' ') + ` L ${points[points.length-1][0]} ${top+innerH} Z`;
  let grid='';
  for(let i=0;i<5;i++){
    const y=top+(innerH/4)*i;
    grid += `<line x1="${left}" y1="${y}" x2="${w-right}" y2="${y}"></line>`;
  }
  const dots=points.map(p=>`<circle class="chart-dot" cx="${p[0]}" cy="${p[1]}" r="4"></circle>`).join('');
  svg.innerHTML=`<g class="chart-grid">${grid}</g><path class="chart-area" d="${area}"></path><path class="chart-line" d="${line}"></path>${dots}`;
}

function renderBarChart(svgId, items){
  const svg=document.getElementById(svgId);
  if(!svg) return;
  const w=600, h=220, left=24, right=18, top=16, bottom=36;
  const innerW=w-left-right, innerH=h-top-bottom;
  const max=Math.max(...items.map(i=>i.value),1);
  const gap=24;
  const barW=(innerW - gap*(items.length-1))/Math.max(items.length,1);
  let grid='';
  for(let i=0;i<5;i++){
    const y=top+(innerH/4)*i;
    grid += `<line x1="${left}" y1="${y}" x2="${w-right}" y2="${y}"></line>`;
  }
  const bars=items.map((item,idx)=>{
    const x=left+idx*(barW+gap);
    const bh=(item.value/max)*innerH;
    const y=top+innerH-bh;
    return `<rect class="chart-bar" x="${x}" y="${y}" width="${barW}" height="${bh}" rx="8"></rect>
            <text class="chart-bar-label" x="${x+barW/2}" y="${h-12}" text-anchor="middle">${item.label}</text>`;
  }).join('');
  svg.innerHTML=`<g class="chart-grid">${grid}</g>${bars}`;
}

function setTab(tabName){
  document.querySelectorAll('[data-tab]').forEach(btn=>{
    btn.classList.toggle('active', btn.dataset.tab === tabName);
  });
  document.querySelectorAll('.tab-panel').forEach(panel=>{
    panel.style.display = panel.dataset.panel === tabName ? '' : 'none';
  });
}

function setupDashboardTabs(){
  document.querySelectorAll('[data-tab]').forEach(btn=>{
    btn.onclick = () => setTab(btn.dataset.tab);
  });
}

function riskLabel(value){
  return value === 'high' ? 'Высокий' : value === 'medium' ? 'Средний' : 'Низкий';
}
function riskClass(value){
  return value === 'high' ? 'red' : value === 'medium' ? 'amber' : 'soft';
}

function recommendationText(p){
  if(!p) return '';
  if(p.stockout_risk === 'high') return `👉 Срочно закажи ${p.reorder_qty} шт.`;
  if(p.stockout_risk === 'medium') return `👉 Проверь закупку: ${p.reorder_qty} шт.`;
  return '✅ Всё стабильно';
}


function smartActionData(p){
  if(!p) return {label:'Проверить SKU', url:'sku.html'};
  if(p.stockout_risk === 'high' && (p.reorder_qty||0) > 0) return {label:'Заказать', url:'app.html', tab:'procurement'};
  if(p.stockout_risk === 'medium') return {label:'Перейти в закупку', url:'app.html', tab:'procurement'};
  return {label:'Проверить SKU', url:'sku.html'};
}
function estimatedLossValue(p){
  const stock = Number(p?.stock || 0);
  const unitCost = Number(p?.unit_cost || p?.unitCost || 0);
  const cover = Number(p?.days_of_cover || 0);
  if(!stock || !unitCost) return 0;
  const overstockDays = Math.max(0, cover - 35);
  const freezeShare = Math.min(0.8, overstockDays / 60);
  return Math.round(stock * unitCost * freezeShare);
}

function actionLabel(p){
  if(!p) return 'Открыть';
  if(p.stockout_risk === 'high' && (p.reorder_qty||0) > 0) return 'Заказать';
  if(p.stockout_risk === 'medium') return 'Перейти в закупку';
  return 'Проверить SKU';
}
function valueLossText(p){
  if(!p) return '';
  const loss = estimatedLossValue(p);
  return loss > 0 ? `Вы теряете ~${money(loss)} в месяц из-за пересидки товара` : '';
}
function coverText(p){
  return `Хватит на ${Math.round(p.days_of_cover||0)} ${declension(Math.round(p.days_of_cover||0), ['день','дня','дней'])}`;
}
function leadTimeText(p){
  return `при сроке поставки ${p.lead_time_days} ${declension(p.lead_time_days, ['день','дня','дней'])}`;
}


function renderActionButton(p){
  const action = smartActionData(p);
  return `<button class="btn ghost action-btn" type="button" data-action-label="${action.label}" data-action-url="${action.url}" data-action-tab="${action.tab||''}" data-action-sku="${p?.sku||''}">${action.label}</button>`;
}
function bindActionButtons(scope=document){
  scope.querySelectorAll('.action-btn').forEach(btn=>{
    btn.onclick = (e)=>{
      e.preventDefault();
      const label = btn.dataset.actionLabel || 'Проверить SKU';
      const url = btn.dataset.actionUrl || 'sku.html';
      const sku = btn.dataset.actionSku || '';
      const tabName = btn.dataset.actionTab || '';
      if(sku){
        try{ setSelectedSku(sku); }catch(e){}
      }
      if(tabName === 'procurement'){
        if(window.location.pathname.endsWith('app.html')){
          const tab = document.querySelector('[data-tab="procurement"]');
          if(tab){ tab.click(); return; }
        }
      }
      window.location = url;
    };
  });
}

function compareProductRows(currentRows, nextRows){
  const current = Object.fromEntries((currentRows||[]).map(r=>[String(r.sku||r.id).toLowerCase(), r]));
  const incoming = Object.fromEntries((nextRows||[]).map(r=>[String(r.id||r.sku).toLowerCase(), r]));
  const changed = {};
  let added=0, updated=0, removed=0;
  const fields=['account','name','channel','warehouse','price','unitCost','stock','reserved','inbound','leadTimeDays','avgDailySales','trend','commissionRate','logisticsPerUnit','adSpend','returnRate'];
  Object.entries(incoming).forEach(([sku,row])=>{
    const old=current[sku];
    if(!old){added++; return;}
    const diff=[];
    fields.forEach(f=>{
      const oldKey = ({unitCost:'unit_cost', leadTimeDays:'lead_time_days', avgDailySales:'avg_daily_sales', commissionRate:'commission_rate', logisticsPerUnit:'logistics_per_unit', adSpend:'ad_spend', returnRate:'return_rate'})[f] || f;
      const oldVal = old[oldKey];
      const newVal = row[f];
      if(typeof newVal === 'number' || typeof oldVal === 'number'){
        if(Math.abs(Number(oldVal||0)-Number(newVal||0))>1e-9) diff.push(f);
      }else if(String(oldVal||'')!==String(newVal||'')) diff.push(f);
    });
    if(diff.length){updated++; diff.forEach(f=>changed[f]=(changed[f]||0)+1);}
  });
  Object.keys(current).forEach(sku=>{ if(!incoming[sku]) removed++; });
  return {added_count:added, updated_count:updated, removed_count:removed, changed_fields:changed};
}

function renderDiffPreview(diff){
  const holder=document.getElementById('replaceCsvDiff');
  if(!holder) return;
  if(!diff){ holder.style.display='none'; holder.innerHTML=''; return; }
  holder.style.display='block';
  const topFields=Object.entries(diff.changed_fields||{}).sort((a,b)=>b[1]-a[1]).slice(0,5);
  holder.innerHTML = `<div class="item"><div class="item-top"><div><h3>Сравнение с текущими данными</h3>
    <p class="small">Перед заменой видно, что именно изменится в организации.</p></div><span class="badge soft">Предпросмотр</span></div><div class="mini-stat-row" style="margin-top:12px"><div class="mini-stat"><div class="small">Новых SKU</div><div style="font-weight:800;margin-top:8px">${diff.added_count||0}</div></div><div class="mini-stat"><div class="small">Обновится SKU</div><div style="font-weight:800;margin-top:8px">${diff.updated_count||0}</div></div><div class="mini-stat"><div class="small">Удалится SKU</div><div style="font-weight:800;margin-top:8px">${diff.removed_count||0}</div></div></div></div>`;
  if(topFields.length){
    const div=document.createElement('div');
    div.className='item';
    div.innerHTML = `<h3>Чаще всего меняются поля</h3>
    <p class="small">${topFields.map(([name,count])=>`${name}: ${count}`).join(' · ')}</p>`;
    holder.appendChild(div);
  }
}

async function loadAuditLog(holderId, organizationId){
  const holder=document.getElementById(holderId);
  if(!holder) return;
  try{
    const logs = await api(`/api/v1/audit-log?organization_id=${organizationId}`);
    holder.innerHTML='';
    logs.forEach(item=>{
      const div=document.createElement('div');
      div.className='item';
      const actor = item.actor_name ? `${item.actor_name} · ${item.actor_email}` : (item.actor_email || 'Система');
      div.innerHTML = `<div class="item-top"><div><h3>${item.action}</h3>
    <p class="small">${fmtDate(item.created_at)} · ${actor}</p></div><span class="badge soft">${item.entity_type}</span></div>`;
      holder.appendChild(div);
    });
    if(!logs.length) holder.innerHTML='<div class="item"><p class="small">Журнал действий пока пуст.</p></div>';
  }catch(err){ holder.innerHTML=`<div class="error">${err.message}</div>`; }
}

async function renderDashboard(){
  const s=requireSession(); if(!s) return;
  if(isSuperAdmin(s)){ window.location='admin.html'; return; }
  setupDashboardTabs();
  setTab('today');

  const who=document.getElementById('who');
  if(who) who.textContent=`${s.user.full_name} · ${s.user.email}${s.org ? ' · ' + s.org.name : ''}`;
  if(!s.org){
    document.getElementById('dashError').innerHTML='<div class="error">Не выбрана организация. Перейди в список организаций.</div>';
    return;
  }

  const currentTariffLabel = document.getElementById('currentTariffLabel');
  if(currentTariffLabel) currentTariffLabel.textContent = `${formatTariff(s.org.tariff_code)} · ${currentRole(s.org)}`;
  const billingBanner=document.getElementById('billingBanner');
  if(billingBanner){
    const label = billingStatusLabel(s.org);
    const until = s.org.paid_until ? ` · до ${s.org.paid_until}` : '';
    billingBanner.className = s.org.billing_status === 'active' ? 'success' : s.org.billing_status === 'blocked' ? 'error' : 'notice';
    billingBanner.innerHTML = `<strong>${label}</strong>${until}${s.org.billing_notice ? `<br>${s.org.billing_notice}` : ''}`;
  }

  if((s.org.billing_status || 'pending_payment') !== 'active' || (s.org.tariff_code || 'none') === 'none'){
    document.querySelectorAll('[data-tab]').forEach(btn=>btn.style.display='none');
    document.querySelectorAll('.tab-panel').forEach(panel=>panel.style.display='none');
    const empty=document.getElementById('dashEmptyState');
    if(empty) empty.style.display='';
    const emptyTitle=document.getElementById('emptyStateTitle');
    const emptyText=document.getElementById('emptyStateText');
    if(emptyTitle) emptyTitle.textContent='Рабочая область создана';
    if(emptyText) emptyText.innerHTML=(s.org.billing_status === 'blocked' ? `Доступ закончился${s.org.paid_until ? ` <strong>${s.org.paid_until}</strong>` : ''}. Чтобы продлить доступ, напишите в <strong>Telegram: @ALeX8nDeRR</strong> или во <strong>ВКонтакте: @sanyok228337</strong>.` : 'Сейчас организация создана без доступа. Разделы <strong>Сегодня</strong>, <strong>Закупки</strong>, <strong>Финансы</strong> и <strong>Команда</strong> появятся после того, как вы напишете в <strong>Telegram: @ALeX8nDeRR</strong> или во <strong>ВКонтакте: @sanyok228337</strong>, а администратор выдаст тариф.');
    bindActionButtons(document);
    markPageReady();
    return;
  }
  const empty=document.getElementById('dashEmptyState');
  if(empty) empty.style.display='none';

  const procurementBtn = document.querySelector('[data-tab="procurement"]');
  const financeBtn = document.querySelector('[data-tab="finance"]');
  const teamBtn = document.querySelector('[data-tab="team"]');
  if(procurementBtn) procurementBtn.style.display = canUse('procurement', s.org) && canRole('manage_products', s.org) ? '' : 'none';
  if(financeBtn) financeBtn.style.display = canUse('finance', s.org) && canRole('view_finance', s.org) ? '' : 'none';
  if(teamBtn) teamBtn.style.display = canUse('team', s.org) && canRole('view_team', s.org) ? '' : 'none';

  const procurementPanel = document.querySelector('[data-panel="procurement"]');
  const financePanel = document.querySelector('[data-panel="finance"]');
  const teamPanel = document.querySelector('[data-panel="team"]');

  if(procurementPanel && !(canUse('procurement', s.org) && canRole('manage_products', s.org))) procurementPanel.style.display='none';
  if(financePanel && !(canUse('finance', s.org) && canRole('view_finance', s.org))) financePanel.style.display='none';
  if(teamPanel && !(canUse('team', s.org) && canRole('view_team', s.org))) teamPanel.style.display='none';

  try{
    const summary=await api(`/api/v1/dashboard/summary?organization_id=${s.org.id}`);
    const products=await api(`/api/v1/products?organization_id=${s.org.id}`);

    document.getElementById('kpi1').textContent=hiddenMoney(summary.revenue_30d);
    document.getElementById('kpi2').textContent=hiddenMoney(summary.contribution_30d);
    document.getElementById('kpi3').textContent=hiddenMoney(summary.revenue_at_risk);
    document.getElementById('kpi4').textContent=hiddenMoney(summary.frozen_cash);
    document.querySelector('#kpi2 + .hint')?.remove;
    const todaySignals=document.getElementById('todaySignals');
    if(todaySignals){
      todaySignals.innerHTML = `
        <div class="mini-stat"><div class="small">Маржа портфеля</div><div style="font-weight:800;margin-top:8px">${hiddenPct(summary.profit_margin_pct)}</div></div>
        <div class="mini-stat"><div class="small">ROAS</div><div style="font-weight:800;margin-top:8px">${summary.roas == null ? 'Скрыто ролью' : ratio(summary.roas)}</div></div>
        <div class="mini-stat"><div class="small">SKU под контролем</div><div style="font-weight:800;margin-top:8px">${summary.high_risk_count + (summary.low_margin_count || 0)}</div></div>`;
    }

    // Сегодня
    const actions=document.getElementById('actions');
    actions.innerHTML='';
    products.filter(p=>p.stockout_risk!=='low' || (p.contribution_per_unit != null && p.contribution_per_unit < 140)).slice(0,8).forEach(p=>{
      const div=document.createElement('div');
      div.className='item';
      div.innerHTML=`<div class="item-top"><div><h3>${p.stockout_risk!=='low' ? 'Согласовать закупку ' + p.reorder_qty + ' шт.' : 'Проверить восстановление маржи'}</h3>
    <p class="small">${p.name} · ${p.account}</p></div><span class="badge ${riskClass(p.stockout_risk)}">${riskLabel(p.stockout_risk)}</span></div><p>${p.stockout_risk!=='low' ? coverText(p) + ' ' + leadTimeText(p) : 'Вклад в прибыль ' + hiddenMoney(p.contribution_per_unit) + ' на единицу'}</p>`;
      actions.appendChild(div);
    });
    if(!actions.children.length){
      actions.innerHTML='<div class="success">Пока всё спокойно. Когда появится риск по закупкам или марже, здесь появятся готовые действия.</div>';
    }
    bindActionButtons(actions);

    const tbody=document.getElementById('productsBody');
    tbody.innerHTML='';
    products.forEach(p=>{
      const tr=document.createElement('tr');
      const canSku = canUse('sku_details', s.org) && canRole('view_sku_details', s.org);
      const stock = Number(p.stock||0);
      const avg = Number(p.avg_daily_sales||0);
      const cover = Number(p.days_of_cover||0);
      const expectedDate = p.expected_stockout_date || '—';
      const unitProfit = hiddenMoney(p.contribution_per_unit);
      const forecastProfit = hiddenMoney(p.forecast_profit_30d);
      tr.innerHTML=`<td>${canSku ? `<a href="sku.html" data-sku-link>${p.sku}</a>` : p.sku}</td><td>${p.account}</td><td>${p.name}</td><td>${stock}</td><td>${avg.toFixed(1)}</td><td>${Math.round(cover)} дн.</td><td>${expectedDate}</td><td>${p.reorder_qty>0 ? p.reorder_qty + ' шт.' : '—'}</td><td>${unitProfit}</td><td>${forecastProfit}</td><td>${riskLabel(p.stockout_risk)}</td>`;
      if(canSku){
        tr.querySelector('[data-sku-link]').onclick=(e)=>{ e.preventDefault(); setSelectedSku(p.sku); window.location='sku.html'; };
      }
      tbody.appendChild(tr);
    });

    const assistant=document.getElementById('assistantAnswer');
    if(assistant){
      if(products.length){
        const riskiest=[...products].sort((a,b)=>a.days_of_cover-b.days_of_cover)[0];
        const financeVisible = canRole('view_finance', s.org);
        const weakest = financeVisible ? [...products].filter(x=>x.contribution_per_unit != null).sort((a,b)=>a.contribution_per_unit-b.contribution_per_unit)[0] : null;
        assistant.innerHTML=`Самый заметный риск сейчас — <strong>${riskiest.name}</strong>. Остатков хватит примерно на <strong>${Math.round(riskiest.days_of_cover)} дн.</strong>, а срок поставки — <strong>${riskiest.lead_time_days} дн.</strong>.${weakest ? `<br><br>Самая низкая прибыль по SKU сейчас у <strong>${weakest.name}</strong>: <strong>${money(weakest.contribution_per_unit)}</strong> на единицу.` : ''}<br><br>${financeVisible ? `Средняя маржа портфеля — <strong>${pct(summary.profit_margin_pct||0)}</strong>, рекламная эффективность — <strong>${ratio(summary.roas)}</strong>. Смотри блоки <strong>Прогноз остатков и прибыли</strong> и <strong>Центр уведомлений</strong> справа.` : 'Финансовые показатели скрыты для этой роли. Основной фокус — остатки, риски и операционные действия.'}`;
      }else{
        assistant.textContent='Пока нет данных по товарам. Загрузите CSV в онбординге.';
      }
    }

    const forecastList=document.getElementById('forecastList');
    if(forecastList){
      forecastList.innerHTML='';
      [...products]
        .sort((a,b)=>(a.days_of_cover||999)-(b.days_of_cover||999))
        .slice(0,6)
        .forEach(p=>{
          const div=document.createElement('div');
          div.className='item';
          const state = (p.days_of_cover||0) <= 7 ? 'red' : (p.days_of_cover||0) <= 14 ? 'amber' : 'soft';
          div.innerHTML=`<div class="item-top"><div><h3>${p.name}</h3>
    <p class="small">${p.account} · ${p.sku}</p></div><span class="badge ${state}">${Math.round(p.days_of_cover||0)} дн.</span></div><p>Остаток <strong>${Number(p.stock||0)}</strong> шт. · средние продажи <strong>${Number(p.avg_daily_sales||0).toFixed(1)}</strong> / день · прогноз прибыли 30 дн. <strong>${money(p.forecast_profit_30d)}</strong>.</p><p class="small">Ожидаемая дата риска: <strong>${p.expected_stockout_date || '—'}</strong></p>`;
          forecastList.appendChild(div);
        });
      if(!forecastList.children.length) forecastList.innerHTML='<div class="item empty-block"><h3>Пока нет прогноза</h3><p class="small">Загрузите товары, и ШТАБ покажет, на сколько дней хватит остатков и сколько можно заработать.</p><a class="btn primary" href="settings.html">Загрузить данные</a></div>';
      bindActionButtons(forecastList);
    }

    const notificationList=document.getElementById('notificationList');
    if(notificationList){
      notificationList.innerHTML='';
      const notes=[];
      products.forEach(p=>{
        if((p.days_of_cover||0)<=7) notes.push({title:`Закупка: ${p.sku}`, body:`Хватит примерно на ${Math.round(p.days_of_cover)} дн. При текущих продажах нужен заказ около ${p.reorder_qty||0} шт.`, level:'red', sort:1});
        else if((p.days_of_cover||0)<=14) notes.push({title:`Остатки под контролем: ${p.sku}`, body:`До нуля около ${Math.round(p.days_of_cover)} дн. Есть время подготовить следующую поставку.`, level:'amber', sort:2});
        if((p.contribution_per_unit||0)<120) notes.push({title:`Низкая прибыль: ${p.sku}`, body:`Прибыль на единицу ${money(p.contribution_per_unit)}. Проверь цену, логистику и рекламу.`, level:'amber', sort:3});
        if((p.forecast_profit_30d||0)<0) notes.push({title:`Отрицательный прогноз: ${p.sku}`, body:`Прогноз прибыли на 30 дн. ${money(p.forecast_profit_30d)}. Товар может работать в минус.`, level:'red', sort:2});
        if((p.roas||0)>0 && (p.roas||0)<3) notes.push({title:`Реклама: ${p.sku}`, body:`ROAS ${ratio(p.roas)} и ACOS ${pct(p.acos_pct||0)} — реклама может не окупаться.`, level:'amber', sort:4});
      });
      notes.sort((a,b)=>(a.sort||9)-(b.sort||9));
      notes.slice(0,10).forEach(n=>{ const div=document.createElement('div'); div.className='item'; div.innerHTML=`<div class="item-top"><div><h3>${n.title}</h3>
    <p class="small">${n.body}</p></div><span class="badge ${n.level==='red'?'red':'amber'}">${n.level==='red'?'Срочно':'Контроль'}</span></div>`; notificationList.appendChild(div); });
      if(!notificationList.children.length) notificationList.innerHTML='<div class="success">Критичных уведомлений по текущим данным нет.</div>';
    }

    // Графики
    const revenueSeries = products.slice(0, 6).map(p => Math.max(1, Math.round((p.price || 0) * (p.avg_daily_sales || 1) * (1 + (p.trend || 0)))));
    renderLineChart('revenueChart', revenueSeries.length ? revenueSeries : [1,2,3,2,4,5]);

    const highRisk = products.filter(p=>p.stockout_risk==='high').length;
    const mediumRisk = products.filter(p=>p.stockout_risk==='medium').length;
    const lowRisk = products.filter(p=>p.stockout_risk==='low').length;
    renderBarChart('riskChart', [
      {label:'Высокий', value: highRisk},
      {label:'Средний', value: mediumRisk},
      {label:'Низкий', value: lowRisk || 1},
    ]);

    // Закупки
    if(canUse('procurement', s.org) && canRole('manage_products', s.org)){
      const procurementList=document.getElementById('procurementList');
      const procurementSummary=document.getElementById('procurementSummary');
      const procurementTable=document.getElementById('procurementTable');
      if(procurementList && procurementSummary && procurementTable){
        procurementList.innerHTML='';
        const procurementRows=[...products].filter(p=>p.reorder_qty>0).sort((a,b)=>b.reorder_qty-a.reorder_qty);
        procurementRows.slice(0,8).forEach(p=>{
          const div=document.createElement('div');
          div.className='item';
          div.innerHTML=`<div class="item-top"><div><h3>${p.name}</h3>
    <p class="small">${p.account} · ${p.warehouse}</p></div><span class="badge ${riskClass(p.stockout_risk)}">${riskLabel(p.stockout_risk)}</span></div><p>Рекомендуемый объём дозакупки: <strong>${p.reorder_qty} шт.</strong></p>`;
          if(canUse('sku_details', s.org)){ div.style.cursor='pointer'; div.onclick=()=>{ setSelectedSku(p.sku); window.location='sku.html'; }; }
          procurementList.appendChild(div);
        });
        if(!procurementList.children.length){
          procurementList.innerHTML='<div class="success">Срочных закупок пока нет. Как только появится дефицит, здесь появится готовое действие.</div>';
        }
        bindActionButtons(procurementList);
        const highRiskCount=products.filter(p=>p.stockout_risk==='high').length;
        const mediumRiskCount=products.filter(p=>p.stockout_risk==='medium').length;
        const totalReorder=products.reduce((sum,p)=>sum+(p.reorder_qty||0),0);
        procurementSummary.innerHTML = `
          <div class="mini-stat"><div class="small">Критичные позиции</div><div style="font-weight:800;margin-top:8px">${highRiskCount} SKU</div></div>
          <div class="mini-stat"><div class="small">Средний риск</div><div style="font-weight:800;margin-top:8px">${mediumRiskCount} SKU</div></div>
          <div class="mini-stat"><div class="small">Потенциальный заказ</div><div style="font-weight:800;margin-top:8px">${totalReorder} шт.</div></div>
        `;
        procurementTable.innerHTML='';
        procurementRows.forEach(p=>{
          const tr=document.createElement('tr');
          tr.innerHTML=`<td>${canUse('sku_details', s.org) ? `<a href="sku.html" data-sku-link>${p.sku}</a>` : p.sku}</td><td>${p.name}</td><td>${p.warehouse}</td><td>${Math.round(p.days_of_cover)} дн.</td><td>${p.inbound}</td><td>${p.reorder_qty}</td><td>${riskLabel(p.stockout_risk)}</td>`;
          if(canUse('sku_details', s.org)){ tr.querySelector('[data-sku-link]').onclick=(e)=>{ e.preventDefault(); setSelectedSku(p.sku); window.location='sku.html'; }; }
          procurementTable.appendChild(tr);
        });
        renderBarChart('procurementChart', procurementRows.slice(0,5).map(p=>({label:p.sku, value:p.reorder_qty || 0})).length ? procurementRows.slice(0,5).map(p=>({label:p.sku, value:p.reorder_qty || 0})) : [{label:'—', value:1}]);
      }
    }

    // Деньги
    if(canUse('finance', s.org) && canRole('view_finance', s.org)){
      const financeMarginList=document.getElementById('financeMarginList');
      const financeCashList=document.getElementById('financeCashList');
      const financeTable=document.getElementById('financeTable');
      if(financeMarginList && financeCashList && financeTable){
        financeMarginList.innerHTML='';
        [...products].sort((a,b)=>a.contribution_per_unit-b.contribution_per_unit).slice(0,6).forEach(p=>{
          const bad = p.contribution_per_unit < 140;
          const div=document.createElement('div');
          div.className='item';
          div.innerHTML=`<div class="item-top"><div><h3>${p.name}</h3>
    <p class="small">${p.account}</p></div><span class="badge ${bad?'red':'soft'}">${bad?'Низкая маржа':'Норма'}</span></div><p>Вклад в прибыль: <strong>${money(p.contribution_per_unit)}</strong> на единицу</p>`;
          if(canUse('sku_details', s.org)){ div.style.cursor='pointer'; div.onclick=()=>{ setSelectedSku(p.sku); window.location='sku.html'; }; }
          financeMarginList.appendChild(div);
        });

        financeCashList.innerHTML='';
        const frozenRows=[...products].filter(p=>p.days_of_cover>45).sort((a,b)=>b.days_of_cover-a.days_of_cover);
        if(frozenRows.length){
          frozenRows.slice(0,6).forEach(p=>{
            const div=document.createElement('div');
            div.className='item';
            div.innerHTML=`<div class="item-top"><div><h3>${p.name}</h3>
    <p class="small">${p.account}</p></div><span class="badge amber">Избыточный остаток</span></div><p>${coverText(p)}</p>`;
            financeCashList.appendChild(div);
          });
        }else{
          financeCashList.innerHTML='<div class="success">Лишних остатков почти нет. Деньги не заморожены в товарах.</div>';
        }
        bindActionButtons(financeMarginList);
        bindActionButtons(financeCashList);

        financeTable.innerHTML='';
        [...products].sort((a,b)=>a.contribution_per_unit-b.contribution_per_unit).forEach(p=>{
          const tr=document.createElement('tr');
          tr.innerHTML=`<td>${canUse('sku_details', s.org) ? `<a href="sku.html" data-sku-link>${p.sku}</a>` : p.sku}</td><td>${p.name}</td><td>${money(p.price)}</td><td>${pct(p.profit_margin_pct||0)}</td><td>${ratio(p.roas)}</td><td>${p.acos_pct==null?'—':pct(p.acos_pct||0)}</td><td>${money(p.contribution_per_unit)}</td><td>${p.contribution_per_unit<140?'Низкая маржа':'Норма'}</td>`;
          if(canUse('sku_details', s.org)){ tr.querySelector('[data-sku-link]').onclick=(e)=>{ e.preventDefault(); setSelectedSku(p.sku); window.location='sku.html'; }; }
          financeTable.appendChild(tr);
        });

        renderBarChart('marginChart', [...products].sort((a,b)=>b.contribution_per_unit-a.contribution_per_unit).slice(0,5).map(p=>({label:p.sku, value:Math.max(1, Math.round(p.contribution_per_unit || 0))})).length ? [...products].sort((a,b)=>b.contribution_per_unit-a.contribution_per_unit).slice(0,5).map(p=>({label:p.sku, value:Math.max(1, Math.round(p.contribution_per_unit || 0))})) : [{label:'—', value:1}]);
      }
    }

    // Команда
    if(canUse('team', s.org) && canRole('view_team', s.org)){
      const members=await api(`/api/v1/members?organization_id=${s.org.id}`);
      const invites=await api(`/api/v1/invites?organization_id=${s.org.id}`);
      const teamMembers=document.getElementById('teamMembers');
      const teamInvites=document.getElementById('teamInvites');
      if(teamMembers && teamInvites){
        teamMembers.innerHTML='';
        members.forEach(m=>{
          const div=document.createElement('div');
          div.className='item';
          div.innerHTML=`<div class="item-top"><div><h3>${m.full_name}</h3>
    <p class="small">${m.email}</p></div><span class="badge soft">${m.role}</span></div><p class="small">${m.status}</p>`;
          teamMembers.appendChild(div);
        });
        if(!members.length){
          teamMembers.innerHTML='<div class="notice">Команда пока пустая. Добавь первого сотрудника, чтобы делегировать работу.</div>';
        }
        bindActionButtons(teamMembers);

        teamInvites.innerHTML='';
        invites.forEach(inv=>{
          const div=document.createElement('div');
          div.className='item';
          div.innerHTML=`<div class="item-top"><div><h3>${inv.email}</h3>
    <p class="small">${inv.status}</p></div><span class="badge amber">${inv.role}</span></div>`;
          teamInvites.appendChild(div);
        });
        if(!invites.length){
          teamInvites.innerHTML='<div class="success">Открытых приглашений нет.</div>';
        }
        bindActionButtons(teamInvites);
        if(canUse('audit_log', s.org) && canRole('view_audit', s.org)) await loadAuditLog('teamAuditLog', s.org.id);
      }
    }

  }catch(err){
    if(String(err.message||'').includes('Payment required')){
      try{
        const orgs=await api('/api/v1/organizations');
        const refreshed=orgs.find(org=>org.id===s.org.id) || s.org;
        setSession({...getSession(), org: refreshed});
        window.location='billing.html';
        return;
      }catch(_e){}
    }
    document.getElementById('dashError').innerHTML=`<div class="error">${err.message || 'Ошибка сервера. Попробуйте позже.'}</div>`;
  }
}

async function renderSettings(){
  const s=requireSession(); if(!s) return;
  if(isSuperAdmin(s)){ window.location='admin.html'; return; }
  const who=document.getElementById('who'); if(who) who.textContent=`${s.user.full_name} · ${s.user.email}${s.org?' · '+s.org.name:''}`;
  if(!s.org){ document.getElementById('settingsError').innerHTML='<div class="error">Не выбрана организация. Перейди в список организаций.</div>'; return; }
  document.getElementById('orgName').value=s.org.name||''; document.getElementById('orgTariff').value=s.org.tariff_code||'none'; document.getElementById('orgMarket').value=s.org.marketplace||'Ozon';
  const tariffReadonlyText = document.getElementById('tariffReadonlyText');
  if(tariffReadonlyText) tariffReadonlyText.value = formatTariff(s.org.tariff_code||'starter');
  const billingBadge = document.getElementById('billingBadge');
  if(billingBadge){
    billingBadge.textContent = s.org.billing_status === 'active' ? 'Оплачено' : s.org.billing_status === 'blocked' ? 'Заблокировано' : 'Ожидает оплаты';
    billingBadge.className = 'badge ' + (s.org.billing_status === 'active' ? 'green' : s.org.billing_status === 'blocked' ? 'red' : 'amber');
  }

  const teamEnabled = canUse('team', s.org) && (s.org.billing_status === 'active') && canRole('view_team', s.org);
  const teamCardIds = ['teamSettingsCard','teamMembersCard','teamInvitesCard'];
  teamCardIds.forEach(id=>{ const el=document.getElementById(id); if(el) el.style.display = teamEnabled ? '' : 'none'; });

  const historyCard = document.getElementById('importHistoryCard');
  if(historyCard) historyCard.style.display = canUse('import_history', s.org) ? '' : 'none';
  const auditLogCard = document.getElementById('auditLogCard');
  if(auditLogCard) auditLogCard.style.display = canUse('audit_log', s.org) && canRole('view_audit', s.org) ? '' : 'none';
  const replaceCard = document.getElementById('replaceCsvCard');
  if(replaceCard) replaceCard.style.display = canUse('dashboard', s.org) && canRole('manage_products', s.org) ? '' : 'none';

  const settingsError = document.getElementById('settingsError');
  if(settingsError) settingsError.innerHTML='';
  const canManageOrg = canRole('manage_org', s.org);
  const canManageTeam = canRole('manage_team', s.org);
  const canManageProducts = canRole('manage_products', s.org);
  const orgName = document.getElementById('orgName');
  const orgMarket = document.getElementById('orgMarket');
  const saveOrgBtn = document.getElementById('saveOrg');
  if(orgName) orgName.disabled = !canManageOrg;
  if(orgMarket) orgMarket.disabled = !canManageOrg;
  if(saveOrgBtn) saveOrgBtn.style.display = canManageOrg ? '' : 'none';
  ['inviteEmail','inviteRole'].forEach(id=>{ const el=document.getElementById(id); if(el) el.disabled = !canManageTeam; });
  const inviteBtn = document.getElementById('sendInvite');
  if(inviteBtn) inviteBtn.style.display = canManageTeam ? '' : 'none';
  const applyCsvBtn = document.getElementById('applyCsvReplace');
  const demoBtn = document.getElementById('useDemoReplace');
  const uploadInput = document.getElementById('replaceCsv');
  const downloadBtn = document.getElementById('downloadTemplate');
  if(applyCsvBtn) applyCsvBtn.style.display = canManageProducts ? '' : 'none';
  if(demoBtn) demoBtn.style.display = canManageProducts ? '' : 'none';
  if(uploadInput) uploadInput.disabled = !canManageProducts;
  if(downloadBtn) downloadBtn.disabled = !canManageProducts;
  if(settingsError && !canManageOrg) settingsError.innerHTML = '<div class="notice">У этой роли доступ к настройкам только для просмотра. Изменять организацию может только руководитель.</div>';

  try{
    if(teamEnabled){
      const members=await api(`/api/v1/members?organization_id=${s.org.id}`);
      const invites=await api(`/api/v1/invites?organization_id=${s.org.id}`);
      const mh=document.getElementById('members'); if(mh){ mh.innerHTML=''; members.forEach(m=>{const div=document.createElement('div'); div.className='item'; div.innerHTML=`<div class="item-top"><div><h3>${m.full_name}</h3>
    <p class="small">${m.email}</p></div><span class="badge soft">${m.role}</span></div><p class="small">${m.status}</p>`; mh.appendChild(div);}); if(!members.length){mh.innerHTML='<div class="item"><p class="small">В команде пока только владелец организации.</p></div>';}}
      const ih=document.getElementById('invites'); if(ih){ ih.innerHTML=''; invites.forEach(inv=>{const div=document.createElement('div'); div.className='item'; div.innerHTML=`<div class="item-top"><div><h3>${inv.email}</h3>
    <p class="small">${inv.status}</p></div><span class="badge amber">${inv.role}</span></div>`; ih.appendChild(div);}); if(!invites.length){ih.innerHTML='<div class="item"><p class="small">Приглашений пока нет.</p></div>';}}
    }
    if(canUse('import_history', s.org)){
      const history = await api(`/api/v1/import-history?organization_id=${s.org.id}`);
      const historyList = document.getElementById('importHistory');
      if(historyList){
        historyList.innerHTML='';
        history.forEach(record=>{
          const div=document.createElement('div'); div.className='item';
          const dt = new Date(record.created_at);
          const whoText = record.imported_by_name ? `${record.imported_by_name} · ${record.imported_by_email}` : (record.imported_by_email || '—');
          const changeText = `Новых: ${record.added_count||0} · Обновлено: ${record.updated_count||0} · Удалено: ${record.removed_count||0}`;
          div.innerHTML=`<div class="item-top"><div><h3>${dt.toLocaleString('ru-RU')}</h3>
    <p class="small">Импортировал: ${whoText}</p></div><span class="badge soft">${record.mode}</span></div><p class="small">Строк: ${record.row_count} · ${changeText}</p>`;
          historyList.appendChild(div);
        });
        if(!history.length){ historyList.innerHTML='<div class="item"><p class="small">История импортов пока пуста.</p></div>'; }
      }
      if(canUse('audit_log', s.org) && canRole('view_audit', s.org)){
        await loadAuditLog('auditLog', s.org.id);
      }
    }
  }catch(err){if(settingsError) settingsError.innerHTML=`<div class="error">${err.message}</div>`;}
}


function setSelectedSku(sku){
  const s = getSession();
  s.selectedSku = sku;
  setSession(s);
}

async function renderSkuDetails(){
  const s=requireActiveBilling(true); if(!s) return;
  const who=document.getElementById('who');
  if(who) who.textContent=`${s.user.full_name} · ${s.user.email}${s.org?' · '+s.org.name:''}`;
  if(!(canUse('sku_details', s.org) && canRole('view_sku_details', s.org))){
    document.getElementById('skuError').innerHTML='<div class="error">Детали SKU доступны на тарифе Рост и выше.</div>';
    return;
  }
  if(!s.org){
    document.getElementById('skuError').innerHTML='<div class="error">Не выбрана организация.</div>';
    return;
  }
  if(!s.selectedSku){
    document.getElementById('skuError').innerHTML='<div class="error">Не выбран товар. Вернись в панель и открой SKU.</div>';
    return;
  }
  try{
    const products=await api(`/api/v1/products?organization_id=${s.org.id}`);
    const p = products.find(x => x.sku === s.selectedSku);
    if(!p){
      document.getElementById('skuError').innerHTML='<div class="error">Товар не найден в текущей организации.</div>';
      return;
    }

    document.getElementById('skuTitle').textContent = `${p.name} · ${p.sku}`;
    document.getElementById('skuMeta').textContent = `${p.account} · ${p.channel} · ${p.warehouse}`;
    document.getElementById('skuRisk').textContent = riskLabel(p.stockout_risk);
    document.getElementById('skuRisk').className = `badge ${riskClass(p.stockout_risk)}`;

    document.getElementById('detailKpi1').textContent = `${Math.round(p.days_of_cover)} дн.`;
    document.getElementById('detailKpi2').textContent = p.reorder_qty > 0 ? `${p.reorder_qty} шт.` : '—';
    document.getElementById('detailKpi3').textContent = money(p.contribution_per_unit);
    document.getElementById('detailKpi4').textContent = money((p.price || 0) * (p.avg_daily_sales || 0) * 30);

    document.getElementById('skuFinance').innerHTML = `
      <div class="item"><h3>Цена продажи</h3><p><strong>${money(p.price)}</strong></p></div>
      <div class="item"><h3>Себестоимость</h3><p><strong>${money(p.unit_cost)}</strong></p></div>
      <div class="item"><h3>Вклад в прибыль</h3><p><strong>${money(p.contribution_per_unit)}</strong> на единицу</p></div>
      <div class="item"><h3>Маржа</h3><p><strong>${pct(p.profit_margin_pct||0)}</strong></p></div>
      <div class="item"><h3>ROAS / ACOS</h3><p><strong>${ratio(p.roas)}</strong> / <strong>${p.acos_pct==null?'—':pct(p.acos_pct||0)}</strong></p></div>
      <div class="item"><h3>Цена безубыточности</h3><p><strong>${money(p.break_even_price)}</strong></p></div>
      <div class="item"><h3>Рекомендованная цена</h3><p><strong>${money(p.recommended_price)}</strong></p></div>
      <div class="item"><h3>Прогноз прибыли за 30 дн.</h3><p><strong>${money(p.forecast_profit_30d)}</strong></p></div>
    `;

    const recommendations = [];
    if(p.stockout_risk === 'high'){
      recommendations.push(`Срочно согласовать дозакупку в объёме ${p.reorder_qty} шт., потому что покрытие ${Math.round(p.days_of_cover)} дн. меньше срока поставки ${p.lead_time_days} дн.`);
    }
    if(p.stockout_risk === 'medium'){
      recommendations.push(`Поставить товар на контроль: покрытие ${Math.round(p.days_of_cover)} дн., нужен резерв под срок поставки ${p.lead_time_days} дн.`);
    }
    if((p.contribution_per_unit || 0) < 140){
      recommendations.push(`Проверить цену, рекламу и логистику: вклад в прибыль ${money(p.contribution_per_unit)} на единицу слишком низкий.`);
    }
    if((p.days_of_cover || 0) > 45){
      recommendations.push(`Снизить заморозку капитала: покрытие ${Math.round(p.days_of_cover)} дн. указывает на избыточный остаток.`);
    }
    if(!recommendations.length){
      recommendations.push('По текущим данным товар выглядит стабильным. Достаточно наблюдать за продажами и сроком поставки.');
    }

    const recHolder=document.getElementById('skuRecommendations');
    recHolder.innerHTML='';
    recommendations.forEach(text=>{
      const div=document.createElement('div');
      div.className='item';
      div.innerHTML=`<p>${text}</p>`;
      recHolder.appendChild(div);
    });

    renderLineChart('skuTrendChart', [
      Math.max(1, Math.round((p.avg_daily_sales || 1) * 0.8)),
      Math.max(1, Math.round((p.avg_daily_sales || 1) * 0.9)),
      Math.max(1, Math.round((p.avg_daily_sales || 1) * 1.0)),
      Math.max(1, Math.round((p.avg_daily_sales || 1) * 1.05)),
      Math.max(1, Math.round((p.avg_daily_sales || 1) * (1 + (p.trend || 0)))),
      Math.max(1, Math.round((p.avg_daily_sales || 1) * (1 + (p.trend || 0.05))))
    ]);

    renderBarChart('skuCostChart', [
      {label:'Цена', value: Math.max(1, Math.round(p.price || 0))},
      {label:'Себес.', value: Math.max(1, Math.round(p.unit_cost || 0))},
      {label:'Прибыль', value: Math.max(1, Math.round(p.contribution_per_unit || 0))}
    ]);

  }catch(err){
    document.getElementById('skuError').innerHTML=`<div class="error">${err.message}</div>`;
  }
}


async function renderInviteAccept(){
  const holder=document.getElementById('inviteCard');
  const error=document.getElementById('inviteError');
  if(!holder || !error) return;
  const params=new URLSearchParams(window.location.search);
  const token=params.get('token')||'';
  if(!token){ error.innerHTML='<div class="error">Не найден токен приглашения.</div>'; return; }
  const loginLink=document.getElementById('inviteLoginLink');
  const registerLink=document.getElementById('inviteRegisterLink');
  if(loginLink) loginLink.href=`login.html?invite=${encodeURIComponent(token)}`;
  if(registerLink) registerLink.href=`register.html?invite=${encodeURIComponent(token)}`;
  try{
    const invite=await api(`/api/v1/invites/public?token=${encodeURIComponent(token)}`, {headers:{}});
    holder.innerHTML = `<div class="item"><div class="item-top"><div><h3>${invite.organization_name}</h3>
    <p class="small">Приглашён: ${invite.email}</p></div><span class="badge amber">${invite.role}</span></div><p class="small">Статус: ${invite.status}. Создано: ${fmtDate(invite.created_at)}</p></div>`;
    const btn=document.getElementById('acceptInviteBtn');
    if(btn){
      btn.onclick=async()=>{
        try{
          const s=getSession();
          if(!s.token){ window.location=`login.html?invite=${encodeURIComponent(token)}`; return; }
          const result=await api('/api/v1/invites/accept',{method:'POST', body:JSON.stringify({token})});
          const orgs=await api('/api/v1/organizations');
          const activeOrg=orgs.find(org=>org.id===result.organization_id) || orgs[0] || null;
          setSession({...getSession(), org:activeOrg});
          error.innerHTML=`<div class="success">Приглашение принято. Роль: ${result.role}. Компания добавлена в ваш профиль.</div>`;
        }catch(err){ error.innerHTML=`<div class="error">${err.message}</div>`; }
      };
    }
  }catch(err){ error.innerHTML=`<div class="error">${err.message}</div>`; }
}
