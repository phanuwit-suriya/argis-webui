import '@babel/polyfill'
import 'mutationobserver-shim'
import './plugins/bootstrap-vue'
import Vue from 'vue'
import App from './App.vue'
import axios from 'axios'
import VueAxios from 'vue-axios'
import { Datetime } from 'vue-datetime'
import 'vue-datetime/dist/vue-datetime.css'

Vue.config.productionTip = false
Vue.use(VueAxios, axios)
Vue.component('datetime', Datetime)

new Vue({
  render: h => h(App),
}).$mount('#app')
