<script setup>
/**
 * App.vue - Componente Raiz da Aplicação
 * 
 * Layout principal com header, navegação, dark mode e área de conteúdo.
 * Usa Composition API do Vue 3.
 */
import { ref, onMounted } from 'vue'
import OperadorasList from './components/OperadorasList.vue'
import EstatisticasDashboard from './components/EstatisticasDashboard.vue'

// Tab ativa (operadoras ou estatísticas)
const activeTab = ref('estatisticas')

// Dark Mode
const isDark = ref(false)

function toggleTheme() {
  isDark.value = !isDark.value
  document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

function initTheme() {
  const saved = localStorage.getItem('theme')
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  
  if (saved === 'dark' || (!saved && prefersDark)) {
    isDark.value = true
    document.documentElement.setAttribute('data-theme', 'dark')
  } else {
    document.documentElement.setAttribute('data-theme', 'light')
  }
}

onMounted(initTheme)
</script>

<template>
  <div class="app">
    <!-- Header -->
    <header class="header">
      <div class="container">
        <div class="header-content">
          <div class="logo">
            <span class="logo-icon">🏥</span>
            <div class="logo-text">
              <h1>Intuitive Care</h1>
              <span class="logo-subtitle">Análise de Despesas</span>
            </div>
          </div>
          
          <!-- Navigation Tabs -->
          <nav class="nav-tabs">
            <button 
              :class="['nav-tab', { active: activeTab === 'estatisticas' }]"
              @click="activeTab = 'estatisticas'"
            >
              📊 Dashboard
            </button>
            <button 
              :class="['nav-tab', { active: activeTab === 'operadoras' }]"
              @click="activeTab = 'operadoras'"
            >
              🏢 Operadoras
            </button>
          </nav>

          <!-- Theme Toggle -->
          <button class="theme-toggle" @click="toggleTheme" :title="isDark ? 'Modo Claro' : 'Modo Escuro'">
            <svg v-if="isDark" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="5"/>
              <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
            </svg>
          </button>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main">
      <div class="container">
        <!-- Dashboard Tab -->
        <EstatisticasDashboard v-if="activeTab === 'estatisticas'" :is-dark="isDark" />
        
        <!-- Operadoras Tab -->
        <OperadorasList v-else-if="activeTab === 'operadoras'" />
      </div>
    </main>

    <!-- Footer -->
    <footer class="footer">
      <div class="container">
        <p>Desenvolvido para o <a href="#">Teste de Estágio</a> • <span class="text-accent">Intuitive Care</span></p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* Header */
.header {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: var(--color-text-inverse);
  padding: var(--space-4) 0;
  box-shadow: var(--shadow-lg);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-4);
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.logo-icon {
  font-size: 2rem;
}

.logo-text h1 {
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--color-text-inverse);
  margin: 0;
}

.logo-subtitle {
  font-size: var(--font-size-xs);
  opacity: 0.8;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* Navigation Tabs */
.nav-tabs {
  display: flex;
  gap: var(--space-2);
}

.nav-tab {
  padding: var(--space-2) var(--space-4);
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-full);
  color: var(--color-text-inverse);
  font-size: var(--font-size-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.nav-tab:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.nav-tab.active {
  background: var(--color-accent);
  border-color: var(--color-accent);
}

/* Theme Toggle */
.theme-toggle {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-full);
  padding: var(--space-2);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-inverse);
  width: 40px;
  height: 40px;
  transition: all var(--transition-base);
}

.theme-toggle:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.05);
}

/* Main */
.main {
  flex: 1;
  padding: var(--space-8) 0;
}

/* Footer */
.footer {
  background: var(--color-bg-elevated);
  padding: var(--space-4) 0;
  text-align: center;
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  border-top: 1px solid var(--color-border);
}

.footer a {
  color: var(--color-accent);
  text-decoration: none;
}

.footer a:hover {
  text-decoration: underline;
}

/* Responsive */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    text-align: center;
    gap: var(--space-3);
  }
  
  .nav-tabs {
    width: 100%;
    justify-content: center;
  }

  .theme-toggle {
    position: absolute;
    top: var(--space-4);
    right: var(--space-4);
  }
}
</style>
