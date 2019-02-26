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

Vue.directive('tooltipTutorial', {
  update: function (el, binding, vnode) {
    //console.log('tooltip', binding.value)
    if(binding.value.actionStatus === 'active' && binding.value.text) {
      let tooltipBlock = document.createElement('div');
      tooltipBlock.classList.add('tooltip-tutorial');
      tooltipBlock.innerHTML = binding.value.text;
      el.appendChild(tooltipBlock)
    } else {
        let tooltip = el.querySelector('.tooltip-tutorial');
        if (tooltip) tooltip.remove();
    }
  },
});