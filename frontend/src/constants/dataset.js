export const DatasetType = {
    NONE: 'none',
    CV: 'cv',
    LLM: 'llm'
};

export const DatasetSource = {
    LOCAL_FILE: 'local_file',
    DIRECT_URL: 'direct_url',
    KAGGLE: 'kaggle',
    HUGGING_FACE: 'hugging_face'
};

export const DatasetFormat = {
    NONE: 'none',
    CSV: 'csv',
    JSONL: 'jsonl',
    IMAGE_FOLDER: 'image_folder',
    ARROW: 'arrow'
};

export const TYPE_OPTIONS = [
    { value: DatasetType.NONE, label: 'None / Unspecified' },
    { value: DatasetType.CV, label: 'Computer Vision (CV)' },
    { value: DatasetType.LLM, label: 'Large Language Models (LLM)' }
];

export const SOURCE_OPTIONS = [
    { value: DatasetSource.LOCAL_FILE, label: 'Upload Local File' },
    { value: DatasetSource.DIRECT_URL, label: 'Direct URL' },
    { value: DatasetSource.HUGGING_FACE, label: 'Hugging Face' },
    { value: DatasetSource.KAGGLE, label: 'Kaggle' }
];

export const FORMAT_OPTIONS = [
    { value: DatasetFormat.CSV, label: 'CSV' },
    { value: DatasetFormat.JSONL, label: 'JSONL' },
    { value: DatasetFormat.IMAGE_FOLDER, label: 'Image Folder (ZIP)' },
    { value: DatasetFormat.ARROW, label: 'Arrow (Hugging Face)' },
    { value: DatasetFormat.NONE, label: 'None' }
];