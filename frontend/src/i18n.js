import { createI18n } from 'vue-i18n'

const messages = {
    en: {
        common: {
            back: 'Back',
            loading: 'Loading...',
            delete: 'Delete',
            none: 'None',
            cancel: "Cancel",
            tested: 'Tested',
            evaluating: 'Evaluating...',
            processing: 'Processing...',
            downloading: 'Downloading...',
            failed: 'Failed',
            pending: 'Pending',
        },
        pagination: {
            page: 'Page',
        },
        header: {
            title: 'VisionMetrics Hub',
            logout: 'LOGOUT',
            online: 'Online',
            admin: 'Admin',
            pages: 'Pages',
            overview: 'Overview'
        },
        sidebar: {
            dashboard: 'Dashboard',
            models: 'AI Models',
            testRuns: 'Test Runs',
            settings: 'Settings',
            analytics: 'Analytics',
            logout: 'Logout'
        },
        auth: {
            username: 'Username',
            password: 'Password',
            login: 'Login',
            invalid: 'Invalid username or password'
        },
        dashboard: {
            title: 'Model Dashboard',
            subtitle: 'Monitor and evaluate your neural network performances',
            uploading: 'Uploading...',
            uploadBtn: 'Create New Model',
            historyTitle: 'Evaluation History',
            liveUpdates: 'Live Updates',
            stats: {
                total: 'Total Models',
                accuracy: 'Avg Accuracy',
                precision: 'Avg Precision',
                recall: 'Avg Recall',
                f1: 'Avg F1-Score',
                roc: 'Avg ROC AUC',
            },
            storage: {
                title: 'Server Storage',
                used: 'Used',
                available: 'Available'
            }
        },
        runsTable: {
            noEvaluationsTitle: 'No Evaluations Found',
            noEvaluationsDesc: 'Start your first evaluation to see the results here.',
            name: 'Evaluation Name',
            status: 'Status',
            accuracy: 'Accuracy',
            precision: 'Precision',
            recall: 'Recall',
            f1Score: 'F1 Score',
            rocAuc: 'ROC AUC',
            confMatrix: 'Matrix',
            action: 'Action',
            tested: 'Tested',
            evaluating: 'Evaluating...',
            failed: 'Failed',
            pending: 'Pending',
            reevaluate: 'Reevaluate',
        },
        modelDetails: {
            loading: 'Loading model data...',
            id: 'ID',
            created: 'Created',
            errorHeader: 'Execution Error:',
            createdAt: "Created at:",
            noRuns: "No runs yet",
            executionError: "Execution Error:",
            mainMetrics: "Key Metrics",
            confusionMatrix: "Confusion Matrix",
            matrix: {
                tn: "True Negative",
                fp: "False Positive",
                fn: "False Negative",
                tp: "True Positive"
            }
        },
        modelSetup: {
            step1Title: "1. Upload Assets",
            archLabel: "Architecture",
            weightsLabel: "Weights",
            selectJson: "Select JSON",
            selectH5: "Select H5",
            uploading: "Uploading...",
            step2Title: "2. Create AI Model",
            namePlaceholder: "Enter model name (e.g. Xception v1)...",
            createBtn: "Create Model",
            creating: "Creating...",
            errorUpload: "File upload failed",
            errorCreate: "Model creation failed"
        },
        modelsTable: {
            pageSubtitle: "Manage your registered AI models and architectures",
            noModels: "No models found",
            noModelsDesc: "Upload your first model to see it here.",
            name: "Name",
            description: "Description",
            createdAt: "Created At",
            actions: "Actions",
            edit: "Edit",
            delete: "Delete",
            editModel: "Edit Model",
            editSubtitle: "Update the information for your model.",
            confirmDelete: "Are you sure you want to delete the model",
            deleteSuccess: "Model deleted successfully!",
            deleteError: "An error occurred while deleting the model.",
            editSuccess: "Model updated successfully!",
            editError: "An error occurred while updating the model.",
            fetchModelError: "Failed to load model data.",
            cancel: "Cancel",
            saveChanges: "Save Changes"
        },
        evaluation: {
            title: "Evaluation",
            historySubtitle: "View and manage all your model runs and metrics.",
            allModels: "All Models",
            liveUpdates: "Live Updates",
            backToTable: "Back to table",
            pageTitle: "Start Evaluation",
            pageSubtitle: "Select a dataset and parameters to evaluate the model.",
            parametersHeader: "Evaluation Parameters",
            loadingData: "Loading data...",
            selectedModel: "Selected Model",
            unknownModel: "Unknown Model",
            selectDatasetLabel: "Select Dataset",
            selectDatasetPlaceholder: "-- Choose a dataset for testing --",
            noDatasetsText: "No datasets available. Please upload them on the Datasets page first.",
            formatLabel: "Format",
            startingTest: "Starting test...",
            fetchError: "Failed to load data from the server.",
            startError: "An error occurred while starting the evaluation.",
            fetchModelError: "Failed to load model data.",
            startTestBtn: 'Start New Test',
            allEvaluations: 'All Evaluations',
            confirmDelete: 'Are you sure you want to delete this evaluation?'
        },
        attacks: {
            title: 'Model Attacks',
            subtitle: 'Generate attack datasets, run them on an adapter, and view the Attack Success Rate (ASR).',
            refresh: 'Refresh',
            createAttack: 'Create Attack',
            runsTitle: 'Attack Runs',
            total: 'Total',
            table: {
                id: 'ID',
                taskName: 'Name / Task',
                status: 'Status',
                date: 'Date',
                actions: 'Actions',
                defaultTaskName: 'Attack Task #{id}',
                loading: 'Loading attack runs...',
                noTasks: 'No attacks created yet. Click "+ Create Attack" to get started.',
                results: 'Results',
                completed: 'Completed',
            },
            dynamic: {
                title: 'Launch Dynamic Attack',
                subtitle: 'Configure mutation settings, target adapter, and judges on a single interactive panel.',
                back: 'Back to attacks',
                sections: {
                    target: 'Target Model (Adapter)',
                    source: 'Base Prompt Source',
                    techniques: 'Attack Techniques',
                    judges: 'Automated Judges',
                    advanced: 'Advanced Generation Parameters (JSON)'
                },
                mode: {
                    dataset: 'From existing dataset',
                    custom: 'Single test prompt'
                },
                placeholders: {
                    selectAdapter: 'Select adapter for testing...',
                    selectDataset: 'Select base dataset...',
                    customPrompt: 'Enter test instruction or prompt to attack...',
                    advancedJson: '{\n  "temperature": 0.7,\n  "max_tokens": 512\n}'
                },
                labels: {
                    rowsCount: 'rows',
                    totalMutations: 'Estimated mutated prompts:',
                    promptsCount: '{count} prompts',
                    selectedJudges: 'Selected judges: {count}'
                },
                buttons: {
                    submit: 'Launch Dynamic Attack',
                    launching: 'Generating & queuing task in Celery...'
                },
                errors: {
                    invalidJson: 'Invalid JSON format in generation parameters.',
                    fetchFailed: 'Failed to load backend resources.',
                    submitFailed: 'Failed to launch the attack.'
                }
            }
        },
    },
    uk: {
        common: {
            back: 'Назад до панелі',
            loading: 'Завантаження...',
            delete: 'Видалити',
            none: 'Нічого',
            cancel: "Скасувати",
            tested: 'Протестовано',
            evaluating: 'Оцінювання...',
            processing: 'Обробка...',
            downloading: 'Завантаження...',
            failed: 'Помилка',
            pending: 'В очікуванні',
        },
        pagination: {
            page: 'Сторінка',
        },
        header: {
            title: 'VisionMetrics Hub',
            logout: 'ВИЙТИ',
            online: 'В мережі',
            admin: 'Адміністратор',
            pages: 'Сторінки',
            overview: 'Огляд'
        },
        sidebar: {
            dashboard: 'Дашборд',
            models: 'Моделі ШІ',
            testRuns: 'Запуски тестів',
            settings: 'Налаштування',
            analytics: 'Аналітика',
            logout: 'Вийти'
        },
        auth: {
            username: 'Ім\'я користувача',
            password: 'Пароль',
            login: 'Увійти',
            invalid: 'Невірне ім\'я користувача або пароль'
        },
        dashboard: {
            title: 'Панель керування',
            subtitle: 'Моніторинг та оцінка продуктивності ваших нейромереж',
            uploading: 'Завантаження...',
            uploadBtn: 'Створити нову модель',
            historyTitle: 'Історія оцінювання',
            liveUpdates: 'Живе оновлення',
            stats: {
                total: 'Всього моделей',
                accuracy: 'Сер. Точність',
                precision: 'Сер. Precision',
                recall: 'Сер. Recall',
                f1: 'Сер. F1-Score',
                roc: 'Сер. ROC AUC',
            },
            storage: {
                title: 'Пам\'ять сервера',
                used: 'Використано',
                available: 'Вільно'
            }
        },
        runsTable: {
            noEvaluationsTitle: 'Оцінювань не знайдено',
            noEvaluationsDesc: 'Запустіть своє перше оцінювання, щоб побачити результати тут.',
            name: 'Назва оцінювання',
            status: 'Статус',
            accuracy: 'Точність (Accuracy)',
            precision: 'Влучність (Precision)',
            recall: 'Повнота (Recall)',
            f1Score: 'F1 Оцінка',
            rocAuc: 'ROC AUC',
            confMatrix: 'Матриця',
            action: 'Дія',
            tested: 'Перевірено',
            evaluating: 'Оцінюється...',
            failed: 'Помилка',
            pending: 'Очікує',
            reevaluate: 'Переоцінити'
        },
        modelDetails: {
            loading: 'Завантаження даних моделі...',
            id: 'ID',
            createdAt: "Створено:",
            errorHeader: 'Помилка виконання:',
            mainMetrics: 'Основні показники',
            noRuns: "Ще не тестувалась",
            executionError: "Помилка виконання:",
            confusionMatrix: "Матриця помилок (Confusion Matrix)",
            matrix: {
                tn: "Істинно негативні (TN)",
                fp: "Хибно позитивні (FP)",
                fn: "Хибно негативні (FN)",
                tp: "Істинно позитивні (TP)"
            }
        },
        modelSetup: {
            step1Title: "1. Завантаження файлів",
            archLabel: "Архітектура",
            weightsLabel: "Ваги",
            selectJson: "Вибрати JSON",
            selectH5: "Вибрати H5",
            uploading: "Завантаження...",
            step2Title: "2. Створення моделі",
            namePlaceholder: "Введіть назву моделі (напр. Xception v1)...",
            createBtn: "Створити модель",
            creating: "Створення...",
            errorUpload: "Помилка при завантаженні файлу",
            errorCreate: "Помилка при створенні моделі"
        },
        modelsTable: {
            pageSubtitle: "Керуйте вашими зареєстрованими ШІ моделями та архітектурами",
            noModels: "Моделей не знайдено",
            noModelsDesc: "Завантажте вашу першу модель, щоб вона з'явилася тут.",
            name: "Назва",
            description: "Опис",
            createdAt: "Дата створення",
            actions: "Дії",
            edit: "Редагувати",
            delete: "Видалити",
            editModel: "Редагування моделі",
            editSubtitle: "Оновіть інформацію про вашу модель.",
            confirmDelete: "Ви впевнені, що хочете видалити модель",
            deleteSuccess: "Модель успішно видалено!",
            deleteError: "Помилка при видаленні моделі.",
            editSuccess: "Модель успішно оновлено!",
            editError: "Помилка при оновленні моделі.",
            fetchModelError: "Не вдалося завантажити дані моделі.",
            cancel: "Скасувати",
            saveChanges: "Зберегти зміни"
        },
        evaluation: {
            title: "Оцінювання",
            historySubtitle: "Переглядайте та керуйте всіма запусками моделей та їх метриками.",
            allModels: "Всі моделі",
            liveUpdates: "Автооновлення",
            backToTable: "Назад до таблиці",
            pageTitle: "Запуск тестування",
            pageSubtitle: "Оберіть датасет та параметри для оцінки моделі.",
            parametersHeader: "Параметри оцінювання",
            loadingData: "Завантаження даних...",
            selectedModel: "Обрана модель",
            unknownModel: "Невідома модель",
            selectDatasetLabel: "Виберіть датасет",
            selectDatasetPlaceholder: "-- Оберіть датасет для перевірки --",
            noDatasetsText: "Немає доступних датасетів. Спочатку завантажте їх на сторінці Datasets.",
            formatLabel: "Формат",
            startingTest: "Запуск тесту...",
            fetchError: "Не вдалося завантажити дані з сервера.",
            startError: "Виникла помилка під час запуску тестування.",
            startTestBtn: 'Почати новий тест',
            allEvaluations: 'Всі оцінювання',
            confirmDelete: 'Ви впевнені, що хочете видалити це оцінювання?'
        },
        attacks: {
            title: 'Атаки на модель',
            subtitle: 'Згенеруйте набір атак, запустіть його на адаптері й перегляньте рівень успішності (ASR).',
            refresh: 'Оновити',
            createAttack: 'Створити атаку',
            runsTitle: 'Запуски атак',
            total: 'Всього',
            table: {
                id: 'ID',
                taskName: 'Назва / Задача',
                status: 'Статус',
                date: 'Дата',
                actions: 'Дії',
                defaultTaskName: 'Задача атаки #{id}',
                loading: 'Завантаження запусків...',
                noTasks: 'Атак ще не створено. Натисніть "+ Створити атаку", щоб розпочати.',
                results: 'Результати',
                completed: 'Завершено',
            },
            dynamic: {
                title: 'Запуск динамічної атаки',
                subtitle: 'Налаштуйте конфігурацію мутацій, оберіть цільову модель та суддів на єдиній панелі.',
                back: 'До списку атак',
                sections: {
                    target: 'Цільова модель (Адаптер)',
                    source: 'Джерело базових промптів',
                    techniques: 'Техніки атак',
                    judges: 'Автоматичні судді (Judges)',
                    advanced: 'Додаткові параметри генерації (JSON)'
                },
                mode: {
                    dataset: 'З існуючого датасету',
                    custom: 'Один тестовий промпт'
                },
                placeholders: {
                    selectAdapter: 'Оберіть адаптер для тестування...',
                    selectDataset: 'Оберіть базовий датасет...',
                    customPrompt: 'Введіть тестову інструкцію чи питання для атаки...',
                    advancedJson: '{\n  "temperature": 0.7,\n  "max_tokens": 512\n}'
                },
                labels: {
                    rowsCount: 'рядків',
                    totalMutations: 'Прогнозована кількість мутованих промптів:',
                    promptsCount: 'Згенеровано {count} промптів',
                    selectedJudges: 'Обрано суддів: {count}'
                },
                buttons: {
                    submit: 'Запустити динамічну атаку',
                    launching: 'Генерація та запуск у Celery...'
                },
                errors: {
                    invalidJson: 'Помилка у форматі JSON параметрів генерації.',
                    fetchFailed: 'Помилка завантаження ресурсів з бекенду.',
                    submitFailed: 'Не вдалося запустити атаку.'
                }
            }
        },
    }
}

export const i18n = createI18n({
    legacy: false,
    locale: 'en',
    fallbackLocale: 'en',
    messages,
})