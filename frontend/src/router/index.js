import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../view/LoginView.vue'
import RegisterView from '../view/RegisterView.vue'
import TestView from '../view/TestView.vue'
import ChatView from '../view/ChatView.vue' 

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', component: TestView },
    { path: '/login', component: LoginView },
    { path: '/register', component: RegisterView },
    { path: '/chat', component: ChatView }, 
  ],
})

export default router
