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
      el.addEventListener('click', removeTooltip);
      el._binding = binding
  },
  unbind: function (el) {
    el.removeEventListener('mouseenter', createTooltip);
    el.removeEventListener('mouseleave', removeTooltip);
    el.removeEventListener('click', removeTooltip);
  }
});

function createTooltip(event) {
  let textInfo = event.currentTarget._binding.value;
  if(store.getters['mod_tutorials/getInteractiveInfo'] && textInfo) {
    let tooltip = document.createElement('div');
    tooltip.classList.add('tooltip-tutorial', `tooltip-tutorial--${event.currentTarget._binding.arg}`);
    tooltip.innerHTML = textInfo;
    event.currentTarget.appendChild(tooltip);
  }
}
function removeTooltip(event) {
  let tooltip = event.currentTarget.querySelector('.tooltip-tutorial');
  if(store.getters['mod_tutorials/getInteractiveInfo'] && tooltip) {
    tooltip.remove();
  }
}


