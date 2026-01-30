import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../view/LoginView.vue'
import ChatView from '../view/ChatView.vue' 

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', component: LoginView },
    { path: '/chat', component: ChatView }, 
  ],
})

export default router
