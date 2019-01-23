import Vue from 'vue'

Vue.directive('tooltip', {
  bind: function (el, binding, vnode) {
     el.classList.add('tooltip-wrap');
    let tooltipBlock = document.createElement('div');
    tooltipBlock.classList.add('tooltip', `tooltip--${binding.arg}`);
    tooltipBlock.innerHTML = binding.value;

    el.appendChild(tooltipBlock)
  },
});
