<script setup>
/**
 * OperadorasList.vue
 * Lista de operadoras com busca e paginação
 */
import { ref, onMounted, computed } from 'vue'
import { operadorasService } from '../services/api'

const loading = ref(true)
const error = ref(null)
const operadoras = ref([])
const total = ref(0)
const page = ref(1)
const limit = ref(20)
const searchQuery = ref('')
let searchTimeout = null

const totalPages = computed(() => Math.ceil(total.value / limit.value))
const canPrev = computed(() => page.value > 1)
const canNext = computed(() => page.value < totalPages.value)

function formatCnpj(cnpj) {
  if (!cnpj || cnpj.length !== 14) return cnpj
  return `${cnpj.slice(0, 2)}.${cnpj.slice(2, 5)}.${cnpj.slice(5, 8)}/${cnpj.slice(8, 12)}-${cnpj.slice(12)}`
}

async function fetchOperadoras() {
  loading.value = true
  error.value = null
  try {
    const data = await operadorasService.list({
      page: page.value,
      limit: limit.value,
      razaoSocial: searchQuery.value,
    })
    operadoras.value = data.data
    total.value = data.total
  } catch (err) {
    console.error('Erro ao carregar operadoras:', err)
    error.value = 'Erro ao carregar operadoras. A API pode estar processando - tente novamente.'
  } finally {
    loading.value = false
  }
}

function onSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    page.value = 1
    fetchOperadoras()
  }, 400)
}

function prevPage() { if (canPrev.value) { page.value--; fetchOperadoras() } }
function nextPage() { if (canNext.value) { page.value++; fetchOperadoras() } }
function clearSearch() { searchQuery.value = ''; page.value = 1; fetchOperadoras() }

onMounted(fetchOperadoras)
</script>

<template>
  <div class="operadoras animate-fade-in">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <div>
          <h2>🏢 Operadoras de Saúde</h2>
          <p class="text-muted">Lista de operadoras registradas na ANS</p>
        </div>
        <div class="header-stats">
          <div class="stat-mini">
            <span class="stat-mini-value">{{ formatNumber(total) }}</span>
            <span class="stat-mini-label">Operadoras</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Search Bar -->
    <div class="search-bar card">
      <div class="search-input-wrapper">
        <span class="search-icon">🔍</span>
        <input 
          v-model="searchQuery" 
          type="text" 
          class="input search-input" 
          placeholder="Buscar por razão social..." 
          @input="onSearch" 
        />
        <button v-if="searchQuery" class="clear-btn" @click="clearSearch">✕</button>
      </div>
      <div class="search-meta">
        <span v-if="!loading" class="badge badge-accent">{{ total }} resultado(s)</span>
      </div>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-card card">
        <div class="spinner"></div>
        <p class="loading-text">Carregando operadoras...</p>
        <p class="text-muted text-sm">Isso pode levar alguns segundos</p>
      </div>
    </div>
    
    <!-- Error State -->
    <div v-else-if="error" class="card error-card">
      <div class="error-icon">⚠️</div>
      <p class="text-error">{{ error }}</p>
      <button class="btn btn-accent mt-4" @click="fetchOperadoras">
        🔄 Tentar novamente
      </button>
    </div>
    
    <!-- Data Table -->
    <div v-else class="card table-card">
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th class="th-cnpj">CNPJ</th>
              <th class="th-razao">Razão Social</th>
              <th class="th-ans">Registro ANS</th>
              <th class="th-modalidade">Modalidade</th>
              <th class="th-uf">UF</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="op in operadoras" :key="op.cnpj" class="table-row">
              <td class="cnpj-cell">
                <code>{{ formatCnpj(op.cnpj) }}</code>
              </td>
              <td class="razao-cell">
                <span class="razao-text">{{ op.razao_social }}</span>
              </td>
              <td class="ans-cell">
                <span v-if="op.registro_ans" class="badge">{{ op.registro_ans }}</span>
                <span v-else class="text-muted">—</span>
              </td>
              <td class="modalidade-cell">
                <span v-if="op.modalidade" class="modalidade-tag">{{ op.modalidade }}</span>
                <span v-else class="text-muted">—</span>
              </td>
              <td>
                <span v-if="op.uf" class="uf-badge">{{ op.uf }}</span>
                <span v-else class="text-muted">—</span>
              </td>
            </tr>
            <tr v-if="operadoras.length === 0">
              <td colspan="5" class="empty-cell">
                <div class="empty-state">
                  <span class="empty-icon">📭</span>
                  <p>Nenhuma operadora encontrada</p>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Pagination -->
      <div v-if="totalPages > 1" class="pagination">
        <button class="pagination-btn" :disabled="!canPrev" @click="prevPage">
          ← Anterior
        </button>
        <div class="pagination-pages">
          <span class="pagination-current">{{ page }}</span>
          <span class="pagination-separator">de</span>
          <span class="pagination-total">{{ totalPages }}</span>
        </div>
        <button class="pagination-btn" :disabled="!canNext" @click="nextPage">
          Próxima →
        </button>
      </div>
    </div>
  </div>
</template>

<script>
function formatNumber(value) {
  return new Intl.NumberFormat('pt-BR').format(value || 0)
}
</script>

<style scoped>
.operadoras {
  animation: fadeIn 0.3s ease;
}

/* Page Header */
.page-header {
  margin-bottom: var(--space-6);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.page-header h2 {
  margin-bottom: var(--space-1);
  color: var(--color-text);
}

.header-stats {
  display: flex;
  gap: var(--space-4);
}

.stat-mini {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-3) var(--space-4);
  text-align: center;
}

.stat-mini-value {
  display: block;
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--color-accent);
}

.stat-mini-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Search Bar */
.search-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
  padding: var(--space-4);
}

.search-input-wrapper {
  position: relative;
  flex: 1;
  max-width: 500px;
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  opacity: 0.5;
}

.search-input {
  padding-left: 48px;
  padding-right: 40px;
}

.clear-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  opacity: 0.5;
  color: var(--color-text);
  font-size: 16px;
}

.clear-btn:hover {
  opacity: 1;
}

.search-meta {
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
}

/* Loading */
.loading-container {
  display: flex;
  justify-content: center;
  padding: var(--space-12);
}

.loading-card {
  text-align: center;
  padding: var(--space-8);
}

.loading-text {
  margin-top: var(--space-4);
  font-weight: 500;
  color: var(--color-text);
}

.text-sm {
  font-size: var(--font-size-sm);
}

/* Error */
.error-card {
  text-align: center;
  padding: var(--space-12);
}

.error-icon {
  font-size: 3rem;
  margin-bottom: var(--space-4);
}

/* Table */
.table-card {
  padding: 0;
  overflow: hidden;
}

.table-container {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th {
  background: var(--color-bg-elevated);
  padding: var(--space-4);
  text-align: left;
  font-weight: 600;
  font-size: var(--font-size-sm);
  color: var(--color-text);
  border-bottom: 2px solid var(--color-border);
  white-space: nowrap;
}

.table td {
  padding: var(--space-4);
  border-bottom: 1px solid var(--color-border);
  font-size: var(--font-size-sm);
}

.table-row {
  transition: background var(--transition-fast);
}

.table-row:hover {
  background: var(--color-bg-elevated);
}

.th-cnpj { width: 180px; }
.th-razao { min-width: 250px; }
.th-ans { width: 120px; }
.th-modalidade { width: 200px; }
.th-uf { width: 80px; }

/* Cells */
.cnpj-cell code {
  font-family: 'JetBrains Mono', 'Consolas', monospace;
  font-size: var(--font-size-xs);
  background: var(--color-bg-elevated);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
}

.razao-cell {
  max-width: 300px;
}

.razao-text {
  font-weight: 500;
  color: var(--color-text);
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ans-cell .badge {
  background: var(--color-bg-elevated);
  color: var(--color-text-muted);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  font-weight: 500;
}

.modalidade-tag {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  background: var(--color-bg-elevated);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  display: inline-block;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.uf-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  padding: var(--space-1) var(--space-2);
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-dark) 100%);
  color: white;
  border-radius: var(--radius-md);
  font-size: var(--font-size-xs);
  font-weight: 700;
}

/* Empty State */
.empty-cell {
  text-align: center;
  padding: var(--space-12) !important;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
}

.empty-icon {
  font-size: 2rem;
  opacity: 0.5;
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-4);
  padding: var(--space-4);
  border-top: 1px solid var(--color-border);
  background: var(--color-bg-elevated);
}

.pagination-btn {
  padding: var(--space-2) var(--space-4);
  border: 1px solid var(--color-border);
  background: var(--color-bg-card);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text);
  transition: all var(--transition-fast);
}

.pagination-btn:hover:not(:disabled) {
  background: var(--color-accent);
  color: white;
  border-color: var(--color-accent);
}

.pagination-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.pagination-pages {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

.pagination-current {
  background: var(--color-accent);
  color: white;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-weight: 600;
  min-width: 28px;
  text-align: center;
}

.pagination-total {
  font-weight: 500;
}

/* Responsive */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: var(--space-4);
  }
  
  .search-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-input-wrapper {
    max-width: none;
  }
  
  .search-meta {
    text-align: center;
  }
}
</style>
