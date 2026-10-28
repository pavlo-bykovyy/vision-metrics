export const STATUS_CONFIG = {
    completed: {
        bgClass: 'bg-green-100',
        textClass: 'text-green-700',
        labelKey: 'common.tested',
        fallbackLabel: 'Tested',
        isSpinning: false,
        isActive: false
    },
    evaluating: {
        bgClass: 'bg-blue-50',
        textClass: 'text-blue-600',
        labelKey: 'common.evaluating',
        fallbackLabel: 'Evaluating...',
        isSpinning: true,
        isActive: true
    },
    processing: {
        bgClass: 'bg-blue-50',
        textClass: 'text-blue-600',
        labelKey: 'common.processing',
        fallbackLabel: 'Processing...',
        isSpinning: true,
        isActive: true
    },
    downloading: {
        bgClass: 'bg-indigo-50',
        textClass: 'text-indigo-600',
        labelKey: 'common.downloading',
        fallbackLabel: 'Downloading...',
        isSpinning: true,
        isActive: true
    },
    failed: {
        bgClass: 'bg-red-100',
        textClass: 'text-red-700',
        labelKey: 'common.failed',
        fallbackLabel: 'Failed',
        isSpinning: false,
        isActive: false
    },
    pending: {
        bgClass: 'bg-slate-100',
        textClass: 'text-slate-500',
        labelKey: 'common.pending',
        fallbackLabel: 'Pending',
        isSpinning: false,
        isActive: false
    },
    none: {
        bgClass: 'bg-gray-100',
        textClass: 'text-gray-400',
        labelKey: 'common.none',
        fallbackLabel: 'None',
        isSpinning: false,
        isActive: false
    }
}

export const getStatusData = (status) => {
    const normalizedStatus = status?.toLowerCase()
    return STATUS_CONFIG[normalizedStatus] || STATUS_CONFIG.pending
}