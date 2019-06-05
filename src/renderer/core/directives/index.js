import Vue from 'vue'
import store from '../../store'


Vue.directive('tooltip', {
  bind: function (el, binding, vnode) {
    el.tooltipStandardBinding = binding;
    el.classList.add('tooltip-wrap');
    el.addEventListener('mouseenter', insertStandardTooltip);
    el.addEventListener('mouseleave', removeStandardTooltip);
  },
  unbind: function (el) {
    el.removeEventListener('mouseenter', insertStandardTooltip);
    el.removeEventListener('mouseleave', removeStandardTooltip);
  }
});

Vue.directive('tooltipInteractive', {
  bind: function (el, binding, vnode) {
    el.tooltipTutorialBinding = binding;
    el.addEventListener('mouseenter', insertTooltipInfo);
    el.addEventListener('mouseleave', removeTooltipInfo);
    el.addEventListener('click', removeTooltipInfo);
  },
  unbind: function (el) {
    el.removeEventListener('mouseenter', insertTooltipInfo);
    el.removeEventListener('mouseleave', removeTooltipInfo);
    el.removeEventListener('click', removeTooltipInfo);
  }
});

let delayTimer;

function insertTooltipInfo(event) {
  if(store.getters['mod_tutorials/getInteractiveInfo'] && event.currentTarget.tooltipTutorialBinding.value) {
    event.currentTarget.appendChild(createTooltipInfo(event.currentTarget, event.currentTarget.tooltipTutorialBinding));
    event.currentTarget.style.position = 'relative';
    if(event.currentTarget.classList.contains('btn--layersbar')) event.currentTarget.parentNode.parentNode.style.zIndex = 7;
  }
}
function insertStandardTooltip(event) {
  if(!store.getters['mod_tutorials/getInteractiveInfo']) {
    delayTimer = setTimeout(() => {
      event.target.appendChild(createStandardTooltip(event.target, event.target.tooltipStandardBinding));
    }, 500);
  }
}

function createTooltipInfo(el, info) {
  let tooltip = document.createElement('section');
  tooltip.classList.add('tooltip-tutorial',`tooltip-tutorial--${info.arg}`, 'js-tooltip-interactive');
  if(typeof info.value === 'string') {
    tooltip.innerHTML = info.value;
  } else {
    tooltip.innerHTML =  `<h4 class="tooltip-tutorial_bold tooltip-tutorial_italic">${info.value.title}</h4>
                          <span class="tooltip-tutorial_italic">${info.value.text}</span>`;
  }
  return tooltip;
}

function createStandardTooltip(el, info) {
  let tooltip = document.createElement('div');
  tooltip.classList.add('tooltip', `tooltip--${info.arg}`);
  tooltip.innerHTML = info.value;
  return tooltip;
}

function removeStandardTooltip(event) {
  event.currentTarget.style.position = '';
  let tooltip = event.currentTarget.querySelector('.tooltip');
  if(tooltip) tooltip.remove();
  clearTimeout(delayTimer);
}

function removeTooltipInfo(event) {
  let tooltip = event.currentTarget.querySelector('.js-tooltip-interactive');
  event.currentTarget.parentNode.parentNode.style.zIndex = '';
  if(store.getters['mod_tutorials/getInteractiveInfo'] && tooltip) {
    tooltip.remove();
  }
}



