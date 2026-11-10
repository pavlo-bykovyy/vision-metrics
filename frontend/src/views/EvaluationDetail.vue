<template>
  <div class="space-y-8 pb-12">

    <!-- Header Section -->
    <div class="flex flex-col md:flex-row md:items-start justify-between gap-4">
      <div>
        <button @click="$router.push('/evaluations')" class="text-sm font-bold text-slate-500 hover:text-slate-800 flex items-center gap-2 mb-4">
          <span>&larr;</span> {{ t('common.back') }}
        </button>
        <h1 class="text-3xl font-black text-slate-900 tracking-tight">
          <template v-if="evaluation">Evaluation #{{ evaluation.id }}</template>
          <template v-else>{{ t('modelDetails.loading') || 'Loading...' }}</template>
        </h1>

        <div v-if="evaluation" class="text-sm text-slate-500 mt-3 flex flex-wrap gap-6 font-medium">
          <!-- Model Link -->
          <span class="flex items-center gap-1.5">
            <strong class="text-slate-700">Model:</strong>
            <router-link v-if="evaluation.model" :to="`/models/${evaluation.model.id}`" class="text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-1 transition-colors">
              {{ evaluation.model.name }}
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
            </router-link>
            <span v-else>Unknown</span>
          </span>

          <!-- Dataset Link -->
          <span class="flex items-center gap-1.5">
            <strong class="text-slate-700">Dataset:</strong>
            <router-link v-if="evaluation.dataset" to="/datasets" class="text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-1 transition-colors">
              {{ evaluation.dataset.name }}
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
            </router-link>
            <span v-else>Unknown</span>
          </span>

          <!-- Date -->
          <span class="flex items-center gap-1.5 text-slate-400">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            {{ new Date(evaluation.created_at).toLocaleString() }}
          </span>
        </div>
      </div>

      <div v-if="evaluation" class="mt-2 md:mt-10">
        <span class="px-6 py-2.5 rounded-xl text-sm font-black uppercase tracking-wider shadow-sm border"
              :class="{
                'bg-green-50 text-green-700 border-green-100': evaluation.status === 'completed',
                'bg-red-50 text-red-700 border-red-100': evaluation.status === 'failed',
                'bg-blue-50 text-blue-700 border-blue-100': evaluation.status === 'processing' || evaluation.status === 'pending'
              }">
          <span v-if="evaluation.status === 'processing'" class="inline-block animate-pulse mr-1">●</span>
          {{ evaluation.status }}
        </span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-20 text-slate-400 font-medium animate-pulse"></div>

    <!-- Content Container -->
    <div v-else-if="evaluation" class="space-y-8">

      <!-- Failed Status Error Message -->
      <div v-if="evaluation.status === 'failed' && evaluation.error_message" class="bg-red-50 rounded-[2.5rem] shadow-xl shadow-red-200/20 border border-red-100 overflow-hidden">
        <div class="px-10 py-6 border-b border-red-100/50 bg-red-100/30 flex items-center gap-3">
          <h3 class="text-lg font-black text-red-800">{{ t('modelDetails.executionError') }}</h3>
        </div>
        <div class="px-10 py-8">
          <p class="text-red-600 font-mono text-sm whitespace-pre-wrap">{{ evaluation.error_message }}</p>
        </div>
      </div>

      <div v-if="evaluation.metrics" class="grid grid-cols-1 lg:grid-cols-2 gap-8">

        <!-- Main Metrics Box -->
        <div class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden flex flex-col">
          <div class="px-10 py-8 border-b border-slate-50 flex items-center justify-between bg-slate-50/30">
            <h2 class="text-xl font-black text-slate-800 tracking-tight">{{ t('modelDetails.mainMetrics') }}</h2>
          </div>
          <div class="p-10">
            <ul class="space-y-4 text-base">
              <!-- Original Metrics -->
              <li class="flex justify-between border-b border-slate-50 pb-3">
                <span class="text-slate-500 font-medium">Accuracy</span>
                <span class="font-bold text-slate-800">{{ formatMetric(evaluation.metrics.accuracy) }}</span>
              </li>
              <li class="flex justify-between border-b border-slate-50 pb-3">
                <span class="text-slate-500 font-medium">Precision</span>
                <span class="font-bold text-slate-800">{{ formatMetric(evaluation.metrics.precision) }}</span>
              </li>
              <li class="flex justify-between border-b border-slate-50 pb-3">
                <span class="text-slate-500 font-medium">Recall</span>
                <span class="font-bold text-slate-800">{{ formatMetric(evaluation.metrics.recall) }}</span>
              </li>
              <li class="flex justify-between border-b border-slate-50 pb-3">
                <span class="text-slate-500 font-medium">F1 Score</span>
                <span class="font-bold text-slate-800">{{ formatMetric(evaluation.metrics.f1_score) }}</span>
              </li>
              <li class="flex justify-between border-b border-slate-50 pb-3">
                <span class="text-slate-500 font-medium">ROC AUC</span>
                <span class="font-bold text-slate-800">{{ formatMetric(evaluation.metrics.roc_auc) }}</span>
              </li>
              <li class="flex justify-between border-b border-slate-50 pb-3">
                <span class="text-slate-500 font-medium">Balanced Accuracy</span>
                <span class="font-bold text-slate-800">{{ formatMetric(evaluation.metrics.balanced_accuracy) }}</span>
              </li>
              <!-- Newly Added Metrics -->
              <li class="flex justify-between border-b border-slate-50 pb-3">
                <span class="text-slate-500 font-medium">PR AUC</span>
                <span class="font-bold text-slate-800">{{ formatMetric(evaluation.metrics.pr_auc) }}</span>
              </li>
              <li class="flex justify-between border-b border-slate-50 pb-3">
                <span class="text-slate-500 font-medium">MCC (Matthews)</span>
                <span class="font-bold text-slate-800">{{ evaluation.metrics.mcc?.toFixed(4) || '—' }}</span>
              </li>
              <li class="flex justify-between border-b border-slate-50 pb-3">
                <span class="text-slate-500 font-medium">Log Loss</span>
                <span class="font-bold text-slate-800">{{ evaluation.metrics.log_loss_value?.toFixed(4) || '—' }}</span>
              </li>
              <li class="flex justify-between pb-1">
                <span class="text-slate-500 font-medium">Brier Score</span>
                <span class="font-bold text-slate-800">{{ evaluation.metrics.brier_score?.toFixed(4) || '—' }}</span>
              </li>
            </ul>
          </div>
        </div>

        <div class="space-y-8">

          <!-- Confusion Matrix Box -->
          <div class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden">
            <div class="px-10 py-8 border-b border-slate-50 flex items-center justify-between bg-slate-50/30">
              <h2 class="text-xl font-black text-slate-800 tracking-tight">{{ t('modelDetails.confusionMatrix') }}</h2>
            </div>
            <div class="p-10">
              <div v-if="hasConfusionMatrix(evaluation.metrics)" class="grid grid-cols-2 gap-4 text-center h-32">
                <div class="bg-slate-50 rounded-2xl flex flex-col justify-center border border-slate-100 shadow-sm">
                  <span class="text-xs text-slate-400 font-bold uppercase tracking-wider">{{ t('modelDetails.matrix.tn') || 'TN' }}</span>
                  <span class="text-3xl font-black text-slate-700 mt-1">{{ evaluation.metrics.tn }}</span>
                </div>
                <div class="bg-red-50 rounded-2xl flex flex-col justify-center border border-red-100 shadow-sm">
                  <span class="text-xs text-red-400 font-bold uppercase tracking-wider">{{ t('modelDetails.matrix.fp') || 'FP' }}</span>
                  <span class="text-3xl font-black text-red-700 mt-1">{{ evaluation.metrics.fp }}</span>
                </div>
                <div class="bg-orange-50 rounded-2xl flex flex-col justify-center border border-orange-100 shadow-sm">
                  <span class="text-xs text-orange-400 font-bold uppercase tracking-wider">{{ t('modelDetails.matrix.fn') || 'FN' }}</span>
                  <span class="text-3xl font-black text-orange-700 mt-1">{{ evaluation.metrics.fn }}</span>
                </div>
                <div class="bg-green-50 rounded-2xl flex flex-col justify-center border border-green-100 shadow-sm">
                  <span class="text-xs text-green-400 font-bold uppercase tracking-wider">{{ t('modelDetails.matrix.tp') || 'TP' }}</span>
                  <span class="text-3xl font-black text-green-700 mt-1">{{ evaluation.metrics.tp }}</span>
                </div>
              </div>
              <div v-else class="h-32 flex items-center justify-center text-slate-400 text-sm font-medium bg-slate-50 rounded-2xl border border-slate-100">
                Matrix data not available
              </div>
            </div>
          </div>

          <!-- Technical Details Box -->
          <div class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden">
            <div class="px-10 py-8 border-b border-slate-50 flex items-center justify-between bg-slate-50/30">
              <h2 class="text-xl font-black text-slate-800 tracking-tight">Technical Details</h2>
            </div>
            <div class="p-10">
              <ul class="space-y-4 text-base">
                <li class="flex justify-between border-b border-slate-50 pb-3">
                  <span class="text-slate-500 font-medium">Latency (ms)</span>
                  <span class="font-bold text-slate-800">{{ evaluation.metrics.mean_latency_ms?.toFixed(2) || '—' }}</span>
                </li>
                <li class="flex justify-between border-b border-slate-50 pb-3">
                  <span class="text-slate-500 font-medium">Averaging Mode</span>
                  <span class="font-bold text-slate-800 capitalize">{{ evaluation.metrics.averaging_mode || '—' }}</span>
                </li>
                <li class="flex justify-between border-b border-slate-50 pb-3">
                  <span class="text-slate-500 font-medium">Decision Threshold</span>
                  <span class="font-bold text-slate-800">{{ evaluation.metrics.decision_threshold || '0.5' }}</span>
                </li>
                <li class="flex justify-between border-b border-slate-50 pb-3">
                  <span class="text-slate-500 font-medium">Model Size</span>
                  <span class="font-bold text-slate-800">{{ formatBytes(evaluation.metrics.model_size_bytes) }}</span>
                </li>
                <li class="flex justify-between items-start pt-1">
                  <span class="text-slate-500 font-medium">Class Mapping</span>
                  <div class="font-mono text-xs text-slate-800 bg-slate-50 p-2 rounded text-right">
                    <span v-if="evaluation.metrics.class_mapping">{{ JSON.stringify(evaluation.metrics.class_mapping) }}</span>
                    <span v-else>—</span>
                  </div>
                </li>
              </ul>
            </div>
          </div>

        </div>
      </div>

      <!-- Diagnostic Report Box -->
      <div v-if="evaluation.metrics" class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden mt-8">
        <!-- Header & Controls -->
        <div class="px-10 py-8 border-b border-slate-100 bg-slate-50/40 flex flex-col xl:flex-row xl:items-center justify-between gap-6">
          <div class="space-y-1.5">
            <div class="flex items-center gap-3 flex-wrap">
              <h2 class="text-xl font-black text-slate-800 tracking-tight">Diagnostic Report</h2>
              <span
                v-if="report"
                class="px-3.5 py-1 rounded-xl text-xs font-black uppercase tracking-wider border shadow-sm"
                :class="statusBadgeClass(report.status)"
              >
                {{ report.status }}
              </span>
            </div>
            <p class="text-sm text-slate-500 font-medium">
              Automated metric discordance analysis and failure signature comparison
            </p>
          </div>

          <div class="flex flex-wrap items-center gap-3">
            <!-- Baseline Selector -->
            <div class="flex items-center gap-2 bg-white border border-slate-200 rounded-xl px-3 py-1.5 shadow-sm">
              <label for="baseline-select" class="text-xs font-bold text-slate-500 uppercase tracking-wider whitespace-nowrap">
                Baseline:
              </label>
              <select
                id="baseline-select"
                v-model="selectedBaselineId"
                @change="onBaselineChange"
                class="text-sm font-semibold text-slate-700 bg-transparent focus:outline-none pr-2"
              >
                <option :value="null">None</option>
                <option
                  v-for="item in candidateBaselines"
                  :key="item.id"
                  :value="item.id"
                >
                  #{{ item.id }} — {{ item.model?.name || `Model #${item.model_id}` }}
                  <template v-if="item.metrics?.roc_auc != null">
                    (AUC {{ Number(item.metrics.roc_auc).toFixed(3) }})
                  </template>
                </option>
              </select>
            </div>

            <!-- Export / View Buttons -->
            <button
              @click="downloadReport('md')"
              :disabled="!report || exportingFormat !== null"
              class="flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold text-slate-700 hover:text-blue-600 bg-white border border-slate-200 hover:border-blue-200 rounded-xl transition-colors shadow-sm disabled:opacity-50"
              title="Download Markdown Report"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
              Markdown
            </button>

            <button
              @click="openHtmlReport"
              :disabled="!report || exportingFormat !== null"
              class="flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold text-slate-700 hover:text-blue-600 bg-white border border-slate-200 hover:border-blue-200 rounded-xl transition-colors shadow-sm disabled:opacity-50"
              title="Open Standalone HTML Report"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
              HTML Report
            </button>

            <button
              @click="downloadReport('json')"
              :disabled="!report"
              class="flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold text-slate-700 hover:text-blue-600 bg-white border border-slate-200 hover:border-blue-200 rounded-xl transition-colors shadow-sm disabled:opacity-50"
              title="Download Report JSON"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
              JSON
            </button>
          </div>
        </div>

        <!-- Loading / Error States -->
        <div v-if="reportLoading" class="p-10 text-center text-sm font-medium text-slate-400 animate-pulse">
          Analyzing metric profile...
        </div>

        <div v-else-if="reportError" class="p-10">
          <div class="bg-amber-50 border border-amber-200 text-amber-800 rounded-2xl px-6 py-4 text-sm font-medium">
            {{ reportError }}
          </div>
        </div>

        <!-- Report Body -->
        <div v-else-if="report" class="p-10 space-y-8">
          <!-- Profile Summary Strip -->
          <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
            <div class="bg-slate-50 rounded-2xl p-4 border border-slate-100">
              <div class="text-xs font-bold text-slate-400 uppercase tracking-wider">Samples (N)</div>
              <div class="text-xl font-black text-slate-800 mt-1">{{ report.profile?.n ?? '—' }}</div>
            </div>
            <div class="bg-slate-50 rounded-2xl p-4 border border-slate-100">
              <div class="text-xs font-bold text-slate-400 uppercase tracking-wider">Prevalence</div>
              <div class="text-xl font-black text-slate-800 mt-1">{{ formatNumber(report.profile?.prevalence) }}</div>
            </div>
            <div class="bg-slate-50 rounded-2xl p-4 border border-slate-100">
              <div class="text-xs font-bold text-slate-400 uppercase tracking-wider">Pred. Positive Rate</div>
              <div class="text-xl font-black text-slate-800 mt-1">{{ formatNumber(report.profile?.predicted_positive_rate) }}</div>
            </div>
            <div class="bg-slate-50 rounded-2xl p-4 border border-slate-100">
              <div class="text-xs font-bold text-slate-400 uppercase tracking-wider">Specificity</div>
              <div class="text-xl font-black text-slate-800 mt-1">{{ formatNumber(report.profile?.metrics?.specificity) }}</div>
            </div>
            <div class="bg-slate-50 rounded-2xl p-4 border border-slate-100">
              <div class="text-xs font-bold text-slate-400 uppercase tracking-wider">Threshold</div>
              <div class="text-xl font-black text-slate-800 mt-1">{{ report.profile?.threshold ?? 0.5 }}</div>
            </div>
          </div>

          <!-- Findings Section -->
          <div class="space-y-4">
            <h3 class="text-base font-black text-slate-800 uppercase tracking-wider">
              Findings ({{ report.findings?.length || 0 }})
            </h3>

            <div
              v-if="!report.findings || report.findings.length === 0"
              class="bg-emerald-50/70 border border-emerald-200 rounded-2xl p-6 flex items-center gap-3 text-emerald-800"
            >
              <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 shrink-0"></span>
              <span class="text-sm font-bold">No metric discordance patterns detected.</span>
            </div>

            <div v-else class="space-y-4">
              <div
                v-for="(finding, idx) in report.findings"
                :key="finding.code || idx"
                class="rounded-2xl p-6 border transition-all"
                :class="findingCardClass(finding.severity)"
              >
                <div class="flex flex-wrap items-center justify-between gap-2 mb-2">
                  <div class="flex items-center gap-2.5 flex-wrap">
                    <span
                      class="px-2.5 py-0.5 rounded-lg text-[11px] font-black uppercase tracking-wider"
                      :class="findingBadgeClass(finding.severity)"
                    >
                      {{ finding.severity }}
                    </span>
                    <h4 class="text-base font-black text-slate-900">{{ finding.title }}</h4>
                  </div>
                  <code class="text-xs font-mono font-bold px-2.5 py-1 rounded-lg bg-white/80 text-slate-700 border border-slate-200/70">
                    {{ finding.code }}
                  </code>
                </div>

                <p v-if="finding.hint" class="text-sm text-slate-700 font-medium mt-1">
                  {{ finding.hint }}
                </p>

                <div
                  v-if="finding.evidence && Object.keys(finding.evidence).length > 0"
                  class="flex flex-wrap gap-2 mt-4"
                >
                  <span
                    v-for="(val, key) in finding.evidence"
                    :key="key"
                    class="inline-flex items-center gap-1.5 text-xs font-mono bg-white/90 border border-slate-200/80 text-slate-700 px-3 py-1 rounded-xl"
                  >
                    <span class="text-slate-400 font-semibold">{{ key }}:</span>
                    <strong class="text-slate-900">{{ formatNumber(val) }}</strong>
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Baseline Comparison Section -->
          <div v-if="report.baseline" class="space-y-6 pt-4 border-t border-slate-100">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <h3 class="text-base font-black text-slate-800 uppercase tracking-wider">
                Comparison with Baseline #{{ report.baseline.meta?.evaluation_id }}
                <span v-if="report.baseline.meta?.model_name" class="text-slate-500 font-bold normal-case">
                  ({{ report.baseline.meta.model_name }})
                </span>
              </h3>
            </div>

            <!-- Hypotheses -->
            <div class="space-y-3">
              <h4 class="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Failure Signature Hypotheses
              </h4>
              <div
                v-if="!report.baseline.hypotheses || report.baseline.hypotheses.length === 0"
                class="bg-slate-50 border border-slate-200/70 rounded-2xl px-5 py-4 text-sm text-slate-600 font-medium"
              >
                No similarity to the controlled failure signatures.
              </div>
              <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div
                  v-for="(hyp, hIdx) in report.baseline.hypotheses"
                  :key="hIdx"
                  class="bg-amber-50/70 border border-amber-200 rounded-2xl p-5 space-y-1.5"
                >
                  <div class="flex items-center justify-between gap-2">
                    <span class="text-sm font-black text-amber-900 font-mono">
                      {{ hyp.similar_to }}
                    </span>
                    <span class="px-2.5 py-0.5 rounded-lg text-[11px] font-bold uppercase bg-amber-100 text-amber-800 border border-amber-200">
                      {{ hyp.confidence }} confidence
                    </span>
                  </div>
                  <p class="text-xs text-amber-900/90 font-medium">
                    {{ hyp.why }}
                  </p>
                </div>
              </div>
            </div>

            <!-- Metric Deltas Table -->
            <div class="space-y-3">
              <h4 class="text-xs font-bold text-slate-400 uppercase tracking-wider">
                11D Metric Profile Deltas (Current vs Baseline)
              </h4>
              <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                <div
                  v-for="(delta, metricKey) in report.baseline.deltas"
                  :key="metricKey"
                  class="bg-slate-50 rounded-2xl p-4 border border-slate-100 flex flex-col justify-between"
                >
                  <div class="text-xs font-bold text-slate-500">{{ formatMetricLabel(metricKey) }}</div>
                  <div class="flex items-baseline justify-between gap-2 mt-2">
                    <span class="text-sm font-bold text-slate-700">
                      {{ formatNumber(report.profile?.metrics?.[metricKey]) }}
                    </span>
                    <span
                      class="text-xs font-mono font-black px-2 py-0.5 rounded-lg"
                      :class="deltaBadgeClass(metricKey, delta)"
                    >
                      {{ formatDelta(delta) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Disclaimer Footer -->
          <div v-if="report.disclaimer" class="pt-4 border-t border-slate-100 text-xs text-slate-400 italic leading-relaxed">
            {{ report.disclaimer }}
          </div>
        </div>
      </div>

      <!-- Raw JSON Data Box -->
      <div class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden mt-8">
        <div class="px-10 py-6 border-b border-slate-50 flex items-center justify-between bg-slate-50/30">
          <div>
            <h2 class="text-xl font-black text-slate-800 tracking-tight">Raw Evaluation Data</h2>
            <p class="text-sm text-slate-500 mt-1 font-medium">Full JSON response for this evaluation run.</p>
          </div>
          <button @click="copyToClipboard(JSON.stringify(evaluation, null, 2))" class="flex items-center gap-2 px-4 py-2 text-sm font-bold text-slate-600 hover:text-blue-600 bg-white border border-slate-200 hover:border-blue-200 rounded-xl transition-colors shadow-sm" title="Copy JSON">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
            Copy JSON
          </button>
        </div>
        <div class="p-6 bg-slate-50/50">
          <pre class="text-xs font-mono text-slate-700 overflow-x-auto whitespace-pre-wrap p-4 bg-white rounded-2xl border border-slate-100 shadow-inner">{{ JSON.stringify(evaluation, null, 4) }}</pre>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const route = useRoute()
const evaluation = ref(null)
const loading = ref(true)

const report = ref(null)
const reportLoading = ref(false)
const reportError = ref(null)
const selectedBaselineId = ref(null)
const candidateBaselines = ref([])
const exportingFormat = ref(null)

const API_URL = import.meta.env.VITE_API_URL || ''

const METRIC_LABELS = {
  accuracy: 'Accuracy',
  precision: 'Precision',
  recall: 'Recall',
  specificity: 'Specificity',
  f1: 'F1 Score',
  balanced_accuracy: 'Balanced Accuracy',
  mcc: 'MCC',
  roc_auc: 'ROC AUC',
  pr_auc: 'PR AUC',
  log_loss: 'Log Loss',
  brier_score: 'Brier Score'
}

const LOWER_IS_BETTER = new Set(['log_loss', 'brier_score'])

const getAuthHeaders = () => {
  const token = localStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

const formatMetric = (value) => {
  if (value === null || value === undefined) return '—'
  return (value * 100).toFixed(2) + '%'
}

const formatNumber = (value) => {
  if (value === null || value === undefined) return '—'
  return typeof value === 'number' ? value.toFixed(4) : String(value)
}

const formatMetricLabel = (key) => METRIC_LABELS[key] || key

const formatDelta = (delta) => {
  if (delta === null || delta === undefined) return '—'
  const sign = delta > 0 ? '+' : ''
  return `${sign}${Number(delta).toFixed(4)}`
}

const statusBadgeClass = (status) => {
  if (status === 'critical') return 'bg-red-50 text-red-700 border-red-200'
  if (status === 'warning') return 'bg-amber-50 text-amber-700 border-amber-200'
  return 'bg-emerald-50 text-emerald-700 border-emerald-200'
}

const findingCardClass = (severity) => {
  if (severity === 'critical') return 'bg-red-50/60 border-red-200'
  if (severity === 'warning') return 'bg-amber-50/60 border-amber-200'
  return 'bg-blue-50/60 border-blue-200'
}

const findingBadgeClass = (severity) => {
  if (severity === 'critical') return 'bg-red-600 text-white'
  if (severity === 'warning') return 'bg-amber-500 text-white'
  return 'bg-blue-600 text-white'
}

const deltaBadgeClass = (metricKey, delta) => {
  if (delta === null || delta === undefined || Math.abs(delta) < 1e-6) {
    return 'bg-slate-200/70 text-slate-600'
  }
  const improved = LOWER_IS_BETTER.has(metricKey) ? delta < 0 : delta > 0
  return improved
    ? 'bg-emerald-100 text-emerald-800'
    : 'bg-red-100 text-red-800'
}

const formatBytes = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  if (!bytes) return '—'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const hasConfusionMatrix = (metrics) => {
  return metrics.tn !== null && metrics.fp !== null && metrics.fn !== null && metrics.tp !== null
}

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    alert('JSON copied to clipboard!')
  } catch (err) {
    console.error('Failed to copy text', err)
    alert('Failed to copy text.')
  }
}

const fetchDiagnosticReport = async () => {
  if (!evaluation.value?.metrics) return
  reportLoading.value = true
  reportError.value = null
  try {
    const params = { format: 'json' }
    if (selectedBaselineId.value !== null) {
      params.baseline_id = selectedBaselineId.value
    }
    const response = await axios.get(
      `${API_URL}/evaluations/${route.params.id}/report`,
      { params, headers: getAuthHeaders() }
    )
    report.value = response.data
  } catch (error) {
    report.value = null
    reportError.value =
      error.response?.data?.detail || 'Failed to load diagnostic report for this evaluation.'
  } finally {
    reportLoading.value = false
  }
}

const fetchCandidateBaselines = async () => {
  if (!evaluation.value?.dataset_id) return
  try {
    const response = await axios.get(`${API_URL}/evaluations/`, {
      params: { page: 1, size: 100 },
      headers: getAuthHeaders()
    })
    const items = response.data?.items || []
    candidateBaselines.value = items.filter(
      (item) =>
        item.id !== evaluation.value.id &&
        item.dataset_id === evaluation.value.dataset_id &&
        item.status === 'completed' &&
        item.metrics &&
        (item.metrics.averaging_mode || 'binary') === 'binary'
    )
  } catch (error) {
    console.error('Error fetching candidate baselines:', error)
  }
}

const onBaselineChange = () => {
  fetchDiagnosticReport()
}

const triggerBlobDownload = (content, mimeType, filename) => {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

const downloadReport = async (format) => {
  if (!evaluation.value) return
  const evalId = evaluation.value.id
  const baseSuffix = selectedBaselineId.value ? `_vs_${selectedBaselineId.value}` : ''

  if (format === 'json' && report.value) {
    triggerBlobDownload(
      JSON.stringify(report.value, null, 2),
      'application/json;charset=utf-8',
      `evaluation_${evalId}_report${baseSuffix}.json`
    )
    return
  }

  exportingFormat.value = format
  try {
    const params = { format }
    if (selectedBaselineId.value !== null) {
      params.baseline_id = selectedBaselineId.value
    }
    const response = await axios.get(`${API_URL}/evaluations/${evalId}/report`, {
      params,
      headers: getAuthHeaders(),
      responseType: 'text'
    })
    const mime = format === 'md' ? 'text/markdown;charset=utf-8' : 'text/html;charset=utf-8'
    triggerBlobDownload(
      response.data,
      mime,
      `evaluation_${evalId}_report${baseSuffix}.${format}`
    )
  } catch (error) {
    console.error(`Failed to export ${format} report:`, error)
    alert(error.response?.data?.detail || `Failed to export ${format.toUpperCase()} report.`)
  } finally {
    exportingFormat.value = null
  }
}

const openHtmlReport = async () => {
  if (!evaluation.value) return
  exportingFormat.value = 'html'
  try {
    const params = { format: 'html' }
    if (selectedBaselineId.value !== null) {
      params.baseline_id = selectedBaselineId.value
    }
    const response = await axios.get(
      `${API_URL}/evaluations/${evaluation.value.id}/report`,
      {
        params,
        headers: getAuthHeaders(),
        responseType: 'text'
      }
    )
    const blob = new Blob([response.data], { type: 'text/html;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    window.open(url, '_blank', 'noopener,noreferrer')
    setTimeout(() => URL.revokeObjectURL(url), 60000)
  } catch (error) {
    console.error('Failed to open HTML report:', error)
    alert(error.response?.data?.detail || 'Failed to open HTML report.')
  } finally {
    exportingFormat.value = null
  }
}

const fetchEvaluationDetails = async () => {
  loading.value = true
  report.value = null
  reportError.value = null
  selectedBaselineId.value = null
  candidateBaselines.value = []
  try {
    const response = await axios.get(`${API_URL}/evaluations/${route.params.id}`, {
      headers: getAuthHeaders()
    })
    evaluation.value = response.data
    if (evaluation.value?.metrics) {
      await Promise.all([fetchDiagnosticReport(), fetchCandidateBaselines()])
    }
  } catch (error) {
    console.error("Error fetching evaluation details:", error)
  } finally {
    loading.value = false
  }
}

watch(
  () => route.params.id,
  (newId, oldId) => {
    if (newId && newId !== oldId) {
      fetchEvaluationDetails()
    }
  }
)

onMounted(() => {
  fetchEvaluationDetails()
})
</script>