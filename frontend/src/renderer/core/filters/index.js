import Vue from 'vue'
import store from '@/store'


Vue.filter('round', (number, n)=> +number.toFixed(n) );
