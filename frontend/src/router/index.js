import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import Dashboard from '../views/DashboardView.vue'
import Login from '../views/Login.vue'
import ModelsView from "@/views/ModelsView.vue"
import ModelDetails from "@/views/ModelDetails.vue";
import LoraTestView from "@/views/LoraTestView.vue";
import LoraTasksView from "@/views/LoraTasksView.vue";
import DatasetsView from "@/views/DatasetsView.vue";
import EvaluateModelView from "@/components/EvaluateModelView.vue";
import EditModelView from "@/views/EditModelView.vue";
import Evaluations from "@/views/Evaluations.vue";
import DatasetUpload from "@/components/DatasetUpload.vue";
import EvaluationDetail from "@/views/EvaluationDetail.vue";
import DatasetDetail from "@/views/DatasetDetail.vue";
import ModelUpload from "@/views/ModelUpload.vue";
import LoraTaskResultsView from "@/views/LoraTaskResultsView.vue";
import LoraAdaptersView from "@/views/LoraAdaptersView.vue";
import LoraAdapterUploadView from "@/views/LoraAdapterUploadView.vue";
import ActiveModelsView from "@/views/ActiveModelsView.vue";
import ApiDocsView from "@/views/ApiDocsView.vue";
import BaseModelTasksView from "@/views/BaseModelTasksView.vue";
import BaseModelCreateTaskView from "@/views/BaseModelCreateTaskView.vue";
import JudgesView from "@/views/JudgesView.vue";
import AddJudgeView from "@/views/AddJudgeView.vue";
import JudgeTasksView from "@/views/JudgeTasksView.vue";
import CreateJudgeView from "@/views/CreateJudgeView.vue";

const routes = [
    {
        path: '/login',
        component: Login,
        name: 'Login'
    },
    {
        path: '/',
        component: MainLayout,
        meta: { requiresAuth: true },
        children: [
            {
                path: '',
                component: Dashboard,
                name: 'Dashboard'
            },
            {
                path: 'test-lora',
                component: LoraTestView,
                name: 'TestLoRA'
            },
            {
                path: 'lora-tasks',
                component: LoraTasksView,
                name: 'LoraTasks'
            },
            {
                path: 'lora-tasks/:id/results',
                component: LoraTaskResultsView,
                name: 'LoraTaskResults',
                props: true
            },
            {
                path: 'models',
                component: ModelsView,
                name: 'Models'
            },
            {
                path: 'models/create',
                component: ModelUpload,
                name: 'ModelSetup'
            },
            {
                path: 'models/:id',
                name: 'model-details',
                component: ModelDetails,
                props: true
            },
            {
                path: 'models/:id/edit',
                name: 'EditModel',
                component: EditModelView,
                props: true
            },
            {
                path: 'datasets',
                component: DatasetsView,
                name: 'Datasets'
            },
            {
                path: 'datasets/upload',
                name: 'DatasetUpload',
                component: DatasetUpload
            },
            {
                path: 'datasets/:id',
                name: 'DatasetDetail',
                component: DatasetDetail,
                props: true
            },
            {
                path: 'base-model-tasks',
                component: BaseModelTasksView,
                name: 'BaseModelTasks'
            },
            {
                path: 'base-models-tasks/create',
                component: BaseModelCreateTaskView,
                name: 'BaseModelCreateTask'
            },
            {
                path: 'base-models-tasks/:id/results',
                component: LoraTaskResultsView,
                name: 'BaseModelCreateTaskResults',
                props: true
            },
            {
                path: 'lora-adapters',
                component: LoraAdaptersView,
                name: 'LoraAdapters'
            },
            {
                path: 'lora-adapters/upload',
                component: LoraAdapterUploadView,
                name: 'LoraAdapterUpload'
            },
            {
                path: 'evaluations',
                name: 'Evaluations',
                component: Evaluations
            },
            {
                path: 'evaluations/create',
                name: 'EvaluateModel',
                component: EvaluateModelView,
                props: true
            },
            {
                path: 'evaluations/:id',
                name: 'EvaluationDetails',
                component: EvaluationDetail,
                props: true
            },
            {
                path: 'active-models',
                component: ActiveModelsView,
                name: 'ActiveModels'
            },
            {
                path: 'api-docs',
                component: ApiDocsView,
                name: 'ApiDocs'
            },
            {
                path: 'judges',
                component: JudgesView,
                name: 'Judges'
            },
            {
                path: 'judges/create',
                component: AddJudgeView,
                name: 'AddJudge'
            },
            {
                path: 'judge-tasks',
                component: JudgeTasksView,
                name: 'JudgeTasks'
            },
            {
                path: 'judge-tasks/create',
                component: CreateJudgeView,
                name: 'CreateJudge'
            },
        ]
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token')

    if (to.meta.requiresAuth && !token) {
        next('/login')
    } else if (to.path === '/login' && token) {
        next('/')
    } else {
        next()
    }
})

export default router