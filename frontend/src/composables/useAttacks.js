/**
 * src/composables/useAttacks.js
 *
 * Composable for interacting with the LLM Attack and Evaluation API endpoints.
 * Handles authentication headers, Pydantic validation error formatting,
 * dynamic dataset creation, configuration inspection, and run execution.
 */

import axios from 'axios'

/**
 * Format FastAPI / Pydantic error details into a human-readable string.
 */
function formatDetail(detail) {
  if (!detail) return 'Невідома помилка'
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
        .map((d) => `${(d.loc || []).filter((p) => p !== 'body').join('.')}: ${d.msg}`)
        .join('\n')
  }
  return JSON.stringify(detail)
}

/**
 * Convert an Axios error object into a user-friendly message.
 */
function toMessage(error) {
  const res = error.response
  if (!res) return 'Не вдалося підключитися до сервера'
  if (res.status === 401) return 'Сесія завершилась. Увійдіть знову.'
  return formatDetail(res.data?.detail)
}

export function useAttacks(apiUrl) {
  const http = axios.create({ baseURL: apiUrl })

  // Attach Bearer token from localStorage if available
  http.interceptors.request.use((config) => {
    const token = localStorage.getItem('token')
    if (token) config.headers.Authorization = `Bearer ${token}`
    return config
  })

  // Unwrap response data or throw a formatted Error
  const call = async (promise) => {
    try {
      return (await promise).data
    } catch (e) {
      throw new Error(toMessage(e))
    }
  }

  return {
    // Create a new dynamic dataset (POST /llm/attacks/datasets)
    buildDataset: (payload) => call(http.post('/llm/attacks/datasets', payload)),

    // Fetch stored dynamic prompt configuration for a dataset (GET /llm/attacks/datasets/{id}/config)
    getDatasetConfig: (datasetId) => call(http.get(`/llm/attacks/datasets/${datasetId}/config`)),

    // Start an evaluation run on an existing dataset (POST /llm/attacks/runs)
    startRun: (payload) => call(http.post('/llm/attacks/runs', payload)),

    // List all attack evaluation runs (GET /llm/attacks/runs)
    listTasks: (params) => call(http.get('/llm/attacks/runs', { params })),

    // Get aggregated ASR summary for a run (GET /llm/attacks/runs/{id}/summary)
    getSummary: (taskId, judgeTaskRunId) =>
        call(
            http.get(`/llm/attacks/runs/${taskId}/summary`, {
              params: judgeTaskRunId ? { judge_task_run_id: judgeTaskRunId } : undefined,
            }),
        ),

    // Compute and persist charts/statistics for one or more tasks (POST /llm/attacks/visualizations)
    buildVisualizations: (payload) => call(http.post('/llm/attacks/visualizations', payload)),

    // List saved visualization runs, optionally filtered by task (GET /llm/attacks/visualizations)
    listVisualizations: (taskId) =>
        call(http.get('/llm/attacks/visualizations', { params: taskId ? { task_id: taskId } : undefined })),

    // Get a saved visualization run with all charts (GET /llm/attacks/visualizations/{id})
    getVisualization: (runId) => call(http.get(`/llm/attacks/visualizations/${runId}`)),

    // Delete a saved visualization run (DELETE /llm/attacks/visualizations/{id})
    deleteVisualization: (runId) => call(http.delete(`/llm/attacks/visualizations/${runId}`)),

    // External resources
    listAdapters: () => call(http.get('/llm/lora/adapters/')),
    listJudges: () => call(http.get('/llm/judges/')),
    listDatasets: (params) => call(http.get('/llm/attacks/datasets', { params })),
    deleteDataset: (datasetId) => call(http.delete(`/datasets/${datasetId}`)),

    // DB-backed Attack Templates (baseline, safety_attack, stereotyping, cultural_bias, toxicity, hallucination, etc.)
    listTemplates: (params) => call(http.get('/llm/attacks/templates', { params })),
    createTemplate: (payload) => call(http.post('/llm/attacks/templates', payload)),
    updateTemplate: (templateId, payload) => call(http.put(`/llm/attacks/templates/${templateId}`, payload)),
    deleteTemplate: (templateId) => call(http.delete(`/llm/attacks/templates/${templateId}`)),

    // DB-backed Task Configurations (heroes, disinfo, TASK_SPECS, INFERENCE_PROMPTS)
    listTaskConfigs: () => call(http.get('/llm/attacks/task-configs')),
    upsertTaskConfig: (payload) => call(http.post('/llm/attacks/task-configs', payload)),
    deleteTaskConfig: (taskName) => call(http.delete(`/llm/attacks/task-configs/${encodeURIComponent(taskName)}`)),

    // DB-backed Wrapping Techniques (direct, ignore, persona, roleplay, base64 with {t} / {b64_t})
    listTechniques: () => call(http.get('/llm/attacks/techniques')),
    upsertTechnique: (payload) => call(http.post('/llm/attacks/techniques', payload)),
    deleteTechnique: (key) => call(http.delete(`/llm/attacks/techniques/${encodeURIComponent(key)}`)),

    // Extract hero/person names dynamically from text (ported from code_from_ipynb.txt)
    extractEntities: (payload) => call(http.post('/llm/attacks/extract-entities', payload)),

    /**
     * Unified helper for the AttackWizard:
     * - If an existing dataset is selected, starts the run directly (with optional prompt overrides).
     * - If a custom ad-hoc prompt is provided, dynamically builds a dataset first and then starts the run.
     */
    startDynamicAttack: async (payload) => {
      let targetDatasetId = payload.dataset_id || payload.base_dataset_id

      if (!targetDatasetId && payload.dataset_builder_payload) {
        const createdDataset = await call(
            http.post('/llm/attacks/datasets', payload.dataset_builder_payload),
        )
        targetDatasetId = createdDataset.dataset_id
      }

      return call(
          http.post('/llm/attacks/runs', {
            dataset_id: Number(targetDatasetId),
            adapter_id: payload.adapter_id != null && payload.adapter_id !== '' ? Number(payload.adapter_id) : null,
            base_model_id: payload.base_model_id ? String(payload.base_model_id).trim() : null,
            judge_ids: payload.judge_ids || [],
            generation_params: payload.generation_params || null,
            judge_params: payload.judge_params || null,
            secret_system_prompt_template: payload.secret_system_prompt_template || null,
            inference_prompts_override: payload.inference_prompts_override || null,
          }),
      )
    },
  }
}