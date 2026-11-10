export const STRESS_TEST_STEPS = ['simulate', 'reviewer', 'figures', 'archive']

export const FIGURE_FORMATS = ['png', 'svg', 'pdf']

export const ACTIVE_STATUSES = ['pending', 'evaluating']

// Visual style per failure path (mode:direction), used for chips in config and tables.
export const FAILURE_PATH_STYLES = {
    'collapse:positive': 'bg-red-50 text-red-700 border-red-100',
    'collapse:negative': 'bg-red-50 text-red-700 border-red-100',
    'score_bias:positive': 'bg-orange-50 text-orange-700 border-orange-100',
    'score_bias:negative': 'bg-orange-50 text-orange-700 border-orange-100',
    'calibration_drift:over': 'bg-indigo-50 text-indigo-700 border-indigo-100',
    'calibration_drift:under': 'bg-indigo-50 text-indigo-700 border-indigo-100',
    'score_inversion:none': 'bg-purple-50 text-purple-700 border-purple-100',
}

// Run-size presets for the create form.
export const STRESS_TEST_PRESETS = {
    smoke: { replicates: 25, ood_replicates: 10, n_boot: 100 },
    medium: { replicates: 200, ood_replicates: 30, n_boot: 500 },
    article: { replicates: 1000, ood_replicates: 60, n_boot: 1000 },
}

// Key tables shown on the Overview tab (in this order) — file names written by the stress test runner.
export const OVERVIEW_TABLES = [
    'publication_table_metric_family_ablation.csv',
    'publication_table_leave_one_prevalence_out.csv',
    'publication_table_baseline_prevalence.csv',
    'publication_table_calibration_invariance.csv',
]

export const REVIEWER_TABLES = [
    'reviewer_table8_extended_ablation.csv',
    'reviewer_wilcoxon_full_vs_reduced.csv',
    'reviewer_alternative_probes.csv',
    'reviewer_non_gaussian_ood_transfer.csv',
    'reviewer_non_gaussian_ood_transfer_crosscheck.csv',
    'reviewer_pca_dimensionality.csv',
    'reviewer_redundant_metric_pairs.csv',
]

export const MANUSCRIPT_FILE = 'manuscript_ready_values.txt'

// Large raw files are not previewed inline (download only).
export const NO_PREVIEW_FILES = ['monte_carlo_raw_results.csv.gz', 'leave_one_prevalence_out_predictions.csv.gz']

export const formatBytes = (bytes) => {
    if (bytes == null) return '—'
    const units = ['B', 'KB', 'MB', 'GB']
    let value = bytes
    let i = 0
    while (value >= 1024 && i < units.length - 1) {
        value /= 1024
        i++
    }
    return `${value.toFixed(i === 0 ? 0 : 1)} ${units[i]}`
}

export const prettifyFileName = (path) =>
    path
        .split('/')
        .pop()
        .replace(/\.(csv\.gz|csv|png|svg|pdf|txt)$/i, '')
        .replace(/_/g, ' ')

export const formatDuration = (start, end) => {
    if (!start) return '—'
    const ms = (end ? new Date(end) : new Date()) - new Date(start)
    if (ms < 0) return '—'
    const s = Math.floor(ms / 1000)
    const h = Math.floor(s / 3600)
    const m = Math.floor((s % 3600) / 60)
    if (h) return `${h}h ${m}m`
    if (m) return `${m}m ${s % 60}s`
    return `${s}s`
}
