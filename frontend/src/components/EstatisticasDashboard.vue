<script setup>
/**
 * EstatisticasDashboard.vue
 * 
 * Dashboard principal com:
 * - Cards de estatísticas (total, média, quantidade)
 * - Top 5 operadoras por despesa (gráfico donut)
 * - Gráfico de distribuição por UF (barras)
 * - Query 3: Operadoras acima da média em 2+ trimestres
 */
import { ref, onMounted, computed, defineProps, watch } from 'vue'
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js'
import { Doughnut, Bar } from 'vue-chartjs'
import { estatisticasService } from '../services/api'

// Props
const props = defineProps({
  isDark: {
    type: Boolean,
    default: false
  }
})

// Registrar componentes do Chart.js
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement)

// Estado reativo
const loading = ref(true)
const error = ref(null)
const stats = ref(null)
const distribuicaoUF = ref([])
const operadorasAcimaMedia = ref([])
const loadingQuery3 = ref(false)

// Cores para os gráficos (paleta elegante sem roxo)
const chartColors = [
  '#0d9488', // teal-600
  '#0891b2', // cyan-600
  '#0284c7', // sky-600
  '#2563eb', // blue-600
  '#16a34a', // green-600
  '#059669', // emerald-600
  '#0e7490', // cyan-700
  '#0369a1', // sky-700
  '#1d4ed8', // blue-700
  '#15803d', // green-700
]

// Cores do texto baseado no tema
const textColor = computed(() => props.isDark ? '#f1f5f9' : '#1e293b')
const gridColor = computed(() => props.isDark ? '#334155' : '#e2e8f0')

// Opções do gráfico de donut
const doughnutOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  cutout: '65%',
  plugins: {
    legend: {
      position: 'right',
      labels: {
        padding: 16,
        usePointStyle: true,
        pointStyle: 'circle',
        color: textColor.value,
        font: {
          size: 12,
          family: "'Inter', 'Segoe UI', sans-serif",
        },
      },
    },
    tooltip: {
      backgroundColor: props.isDark ? '#1e293b' : '#ffffff',
      titleColor: textColor.value,
      bodyColor: textColor.value,
      borderColor: gridColor.value,
      borderWidth: 1,
      padding: 12,
      cornerRadius: 8,
      callbacks: {
        label: (context) => {
          const value = context.raw
          return ` ${formatCurrency(value, true)}`
        }
      }
    }
  },
}))

// Opções do gráfico de barras
const barOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      backgroundColor: props.isDark ? '#1e293b' : '#ffffff',
      titleColor: textColor.value,
      bodyColor: textColor.value,
      borderColor: gridColor.value,
      borderWidth: 1,
      padding: 12,
      cornerRadius: 8,
      callbacks: {
        label: (context) => {
          const item = distribuicaoUF.value[context.dataIndex]
          return [
            ` Total: ${formatCurrency(context.raw, true)}`,
            ` Percentual: ${item?.percentual || 0}%`
          ]
        }
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        color: gridColor.value,
        drawBorder: false,
      },
      ticks: {
        color: textColor.value,
        font: {
          size: 11,
        },
        callback: (value) => formatCurrency(value, true),
      },
    },
    x: {
      grid: {
        display: false,
      },
      ticks: {
        color: textColor.value,
        font: {
          size: 11,
          weight: 500,
        },
      },
    },
  },
}))

// Dados do gráfico de UF
const ufChartData = computed(() => {
  const top10 = distribuicaoUF.value.slice(0, 10)
  return {
    labels: top10.map(item => item.uf),
    datasets: [
      {
        label: 'Total por UF',
        data: top10.map(item => item.total),
        backgroundColor: chartColors,
        borderRadius: 6,
        borderSkipped: false,
      },
    ],
  }
})

// Dados do gráfico de top operadoras
const topOperadorasChartData = computed(() => {
  if (!stats.value?.top_5_operadoras) return null
  
  const operadoras = stats.value.top_5_operadoras
  return {
    labels: operadoras.map(o => truncateText(o.razao_social, 20)),
    datasets: [
      {
        data: operadoras.map(o => o.total),
        backgroundColor: chartColors.slice(0, 5),
        borderWidth: 0,
        hoverOffset: 8,
      },
    ],
  }
})

// Média geral das despesas
const mediaGeral = computed(() => stats.value?.media_despesas || 0)

// Formatar moeda
function formatCurrency(value, compact = false) {
  if (compact && value >= 1e9) {
    return `R$ ${(value / 1e9).toFixed(1)}B`
  }
  if (compact && value >= 1e6) {
    return `R$ ${(value / 1e6).toFixed(1)}M`
  }
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(value)
}

// Formatar número
function formatNumber(value) {
  return new Intl.NumberFormat('pt-BR').format(value)
}

// Truncar texto
function truncateText(text, maxLength) {
  if (!text) return 'Sem nome'
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

// Buscar dados principais
async function fetchData() {
  loading.value = true
  error.value = null
  
  try {
    const [statsData, ufData] = await Promise.all([
      estatisticasService.getGerais(),
      estatisticasService.getDistribuicaoUF(),
    ])
    
    stats.value = statsData
    distribuicaoUF.value = ufData
    
    // Buscar Query 3 em paralelo após dados principais
    fetchOperadorasAcimaMedia()
  } catch (err) {
    error.value = 'Não foi possível carregar os dados. Verifique se a API está rodando.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

// Buscar operadoras acima da média (Query 3)
async function fetchOperadorasAcimaMedia() {
  loadingQuery3.value = true
  try {
    const data = await estatisticasService.getOperadorasAcimaMedia(10)
    operadorasAcimaMedia.value = data
  } catch (err) {
    console.error('Erro ao carregar Query 3:', err)
  } finally {
    loadingQuery3.value = false
  }
}

onMounted(fetchData)
</script>

<template>
  <div class="dashboard animate-fade-in">
    <!-- Loading State -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
    </div>
    
    <!-- Error State -->
    <div v-else-if="error" class="card error-card">
      <div class="error-icon">⚠️</div>
      <p class="text-error">{{ error }}</p>
      <button class="btn btn-accent mt-4" @click="fetchData">
        🔄 Tentar novamente
      </button>
    </div>
    
    <!-- Dashboard Content -->
    <template v-else-if="stats">
      <!-- Stats Cards -->
      <div class="grid grid-cols-3 mb-6">
        <div class="stat-card">
          <div class="stat-icon">💰</div>
          <div class="stat-content">
            <div class="stat-value">{{ formatCurrency(stats.total_despesas, true) }}</div>
            <div class="stat-label">Total de Despesas</div>
          </div>
        </div>
        
        <div class="stat-card accent">
          <div class="stat-icon">📊</div>
          <div class="stat-content">
            <div class="stat-value">{{ formatCurrency(stats.media_despesas, true) }}</div>
            <div class="stat-label">Média por Registro</div>
          </div>
        </div>
        
        <div class="stat-card dark">
          <div class="stat-icon">📋</div>
          <div class="stat-content">
            <div class="stat-value">{{ formatNumber(stats.quantidade_registros) }}</div>
            <div class="stat-label">Registros Processados</div>
          </div>
        </div>
      </div>
      
      <!-- Charts Row -->
      <div class="grid grid-cols-2">
        <!-- Top 5 Operadoras -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">🏆 Top 5 Operadoras por Despesa</h3>
          </div>
          
          <div v-if="topOperadorasChartData && stats.top_5_operadoras.length > 0" class="chart-container donut-chart">
            <Doughnut :data="topOperadorasChartData" :options="doughnutOptions" />
          </div>
          <div v-else class="empty-state">
            <p>Nenhuma operadora encontrada</p>
          </div>
          
          <ul v-if="stats.top_5_operadoras.length > 0" class="top-list">
            <li v-for="(op, index) in stats.top_5_operadoras" :key="index" class="top-item">
              <span class="top-rank" :style="{ background: chartColors[index] }">{{ index + 1 }}º</span>
              <span class="top-name">{{ truncateText(op.razao_social, 35) }}</span>
              <span class="top-value">{{ formatCurrency(op.total, true) }}</span>
            </li>
          </ul>
        </div>
        
        <!-- Distribuição por UF -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">📊 Distribuição por UF (Top 10)</h3>
            <span class="badge badge-accent">{{ distribuicaoUF.length }} estados</span>
          </div>
          
          <div v-if="distribuicaoUF.length" class="chart-container bar-chart">
            <Bar :data="ufChartData" :options="barOptions" />
          </div>
          <div v-else class="empty-state">
            <p>Nenhum dado de UF encontrado</p>
          </div>
        </div>
      </div>
      
      <!-- Query 3: Operadoras Acima da Média -->
      <div class="card mt-6">
        <div class="card-header">
          <div class="query3-header">
            <h3 class="card-title">📈 Operadoras Acima da Média em 2+ Trimestres</h3>
            <div class="query3-info">
              <span class="info-icon" title="Operadoras que tiveram despesas acima da média geral do mercado em pelo menos 2 trimestres diferentes">ℹ️</span>
            </div>
          </div>
          <span v-if="!loadingQuery3" class="badge badge-accent">{{ operadorasAcimaMedia.length }} operadoras</span>
        </div>
        
        <p class="query3-description">
          Identifica operadoras com despesas <strong>consistentemente acima</strong> da média geral 
          ({{ formatCurrency(mediaGeral, true) }}) em múltiplos trimestres.
        </p>
        
        <!-- Loading Query 3 -->
        <div v-if="loadingQuery3" class="query3-loading">
          <div class="spinner-small"></div>
          <span>Calculando operadoras...</span>
        </div>
        
        <!-- Tabela Query 3 -->
        <div v-else-if="operadorasAcimaMedia.length > 0" class="table-container">
          <table class="table query3-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Operadora</th>
                <th class="text-center">Trimestres Acima</th>
                <th class="text-right">Média da Operadora</th>
                <th class="text-right">Total Despesas</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(op, index) in operadorasAcimaMedia" :key="op.cnpj" class="table-row">
                <td>
                  <span class="rank-badge" :class="{ 'rank-top': index < 3 }">{{ index + 1 }}</span>
                </td>
                <td>
                  <div class="operadora-nome">{{ truncateText(op.razao_social, 40) }}</div>
                  <div class="operadora-cnpj">{{ op.cnpj }}</div>
                </td>
                <td class="text-center">
                  <span class="trimestre-badge">
                    {{ op.trimestres_acima_media }}/{{ op.total_trimestres }}
                  </span>
                </td>
                <td class="text-right">
                  <span class="valor-acima" v-if="op.media_operadora > mediaGeral">
                    {{ formatCurrency(op.media_operadora, true) }}
                  </span>
                  <span v-else>{{ formatCurrency(op.media_operadora, true) }}</span>
                </td>
                <td class="text-right font-bold">
                  {{ formatCurrency(op.total_despesas, true) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div v-else class="empty-state">
          <p>Nenhuma operadora com despesas acima da média em 2+ trimestres</p>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.dashboard {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Stat Card Variations */
.stat-card {
  display: flex;
  align-items: flex-start;
  gap: var(--space-4);
}

.stat-card.accent {
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-dark) 100%);
}

.stat-card.dark {
  background: linear-gradient(135deg, #475569 0%, #334155 100%);
}

.stat-icon {
  font-size: 2rem;
  opacity: 0.9;
}

.stat-content {
  flex: 1;
}

/* Chart Containers */
.chart-container {
  margin-bottom: var(--space-4);
  position: relative;
}

.donut-chart {
  height: 220px;
}

.bar-chart {
  height: 300px;
}

/* Top List */
.top-list {
  list-style: none;
  margin-top: var(--space-4);
  border-top: 1px solid var(--color-border);
  padding-top: var(--space-4);
}

.top-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) 0;
  border-bottom: 1px solid var(--color-border);
  transition: background var(--transition-fast);
}

.top-item:hover {
  background: var(--color-bg-elevated);
  margin: 0 calc(var(--space-3) * -1);
  padding-left: var(--space-3);
  padding-right: var(--space-3);
  border-radius: var(--radius-md);
}

.top-item:last-child {
  border-bottom: none;
}

.top-rank {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  font-weight: 600;
  font-size: var(--font-size-xs);
  color: white;
}

.top-name {
  flex: 1;
  font-size: var(--font-size-sm);
  color: var(--color-text);
  font-weight: 500;
}

.top-value {
  font-weight: 600;
  color: var(--color-accent);
  font-size: var(--font-size-sm);
}

/* Empty & Error States */
.empty-state {
  text-align: center;
  padding: var(--space-8);
  color: var(--color-text-muted);
}

.error-card {
  text-align: center;
  padding: var(--space-12);
}

.error-icon {
  font-size: 3rem;
  margin-bottom: var(--space-4);
}

/* Badge */
.badge {
  display: inline-flex;
  align-items: center;
  padding: var(--space-1) var(--space-3);
  font-size: var(--font-size-xs);
  font-weight: 500;
  border-radius: var(--radius-full);
  background: var(--color-bg-elevated);
  color: var(--color-text-muted);
}

.badge-accent {
  background: rgba(13, 148, 136, 0.15);
  color: var(--color-accent);
}

/* Query 3 Styles */
.query3-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.query3-info {
  cursor: help;
}

.info-icon {
  font-size: 1rem;
  opacity: 0.7;
}

.query3-description {
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  margin-bottom: var(--space-4);
  line-height: 1.5;
}

.query3-loading {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-6);
  color: var(--color-text-muted);
}

.spinner-small {
  width: 20px;
  height: 20px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Table Styles */
.table-container {
  overflow-x: auto;
  margin-top: var(--space-2);
}

.query3-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

.query3-table th {
  padding: var(--space-3) var(--space-4);
  text-align: left;
  font-weight: 600;
  font-size: var(--font-size-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
  border-bottom: 1px solid var(--color-border);
}

.query3-table td {
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--color-border);
}

.table-row {
  transition: background var(--transition-fast);
}

.table-row:hover {
  background: var(--color-bg-elevated);
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: var(--radius-full);
  background: var(--color-bg-elevated);
  font-weight: 600;
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.rank-badge.rank-top {
  background: var(--color-accent);
  color: white;
}

.operadora-nome {
  font-weight: 500;
  color: var(--color-text);
}

.operadora-cnpj {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  font-family: 'JetBrains Mono', monospace;
}

.trimestre-badge {
  display: inline-flex;
  padding: var(--space-1) var(--space-2);
  background: rgba(13, 148, 136, 0.15);
  color: var(--color-accent);
  border-radius: var(--radius-md);
  font-weight: 600;
  font-size: var(--font-size-sm);
}

.valor-acima {
  color: #16a34a;
  font-weight: 600;
}

.text-center {
  text-align: center;
}

.text-right {
  text-align: right;
}

.font-bold {
  font-weight: 600;
}

.mt-6 {
  margin-top: var(--space-6);
}
</style>
