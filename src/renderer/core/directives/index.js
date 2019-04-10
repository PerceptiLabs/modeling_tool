import Vue from 'vue'
import store from '../../store'


Vue.directive('tooltip', {
  bind: function (el, binding, vnode) {
    el.classList.add('tooltip-wrap');
    let tooltipBlock = document.createElement('div');
    tooltipBlock.classList.add('tooltip', `tooltip--${binding.arg}`);
    tooltipBlock.innerHTML = binding.value;
    el.appendChild(tooltipBlock);
  }
});

Vue.directive('tooltipInteractive', {
  bind: function (el, binding, vnode) {
      el.addEventListener('mouseenter', createTooltip);
      el.addEventListener('mouseleave', removeTooltip);
      el._binding = binding
  },
  unbind: function (el) {
    el.removeEventListener('mouseenter', createTooltip);
    el.removeEventListener('mouseleave', removeTooltip);
  }
});

function createTooltip(event) {
  if(store.getters['mod_tutorials/getInteractiveInfo']) {
    let tooltip = document.createElement('div');
    tooltip.classList.add('tooltip-tutorial', `tooltip-tutorial--${event.target._binding.arg}`);
    tooltip.innerHTML = event.target._binding.value;
    event.target.appendChild(tooltip);
  }
}
function removeTooltip(event) {
  if(store.getters['mod_tutorials/getInteractiveInfo']) {
    let tooltip = event.target.querySelector('.tooltip-tutorial');
    tooltip.remove();
  }
}


