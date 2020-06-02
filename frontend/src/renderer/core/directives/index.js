import Vue from 'vue'
import store from '@/store'


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
    el.addEventListener('mousedown', removeTooltipInfo);
  },
  unbind: function (el) {
    el.removeEventListener('mouseenter', insertTooltipInfo);
    el.removeEventListener('mouseleave', removeTooltipInfo);
    el.removeEventListener('click', removeTooltipInfo);
  }
});

Vue.directive('comingSoon', {
  bind(el, binding) {
    if(binding.value) el.addEventListener('mousedown', showComingSoonPopup);
  },
  unbind(el) {
    el.removeEventListener('mousedown', showComingSoonPopup);
  }
});

function showComingSoonPopup() {
  store.dispatch('globalView/GP_ComingSoonPopup')
}

let delayTimer;

function insertTooltipInfo(event) {
  if(store.getters['mod_tutorials/getInteractiveInfo'] && event.currentTarget.tooltipTutorialBinding.value) {
    document.body.appendChild(createTooltipInfo(event.currentTarget, event.currentTarget.tooltipTutorialBinding));
  }
}
function insertStandardTooltip(event) {
  let openTooltipDelay = 500;

  if(event.target.tooltipStandardBinding.arg === 'networkElement')
  openTooltipDelay = 0;

  if(!store.getters['mod_tutorials/getInteractiveInfo']) {
    delayTimer = setTimeout(() => {
      event.target.appendChild(createStandardTooltip(event.target, event.target.tooltipStandardBinding));
    }, openTooltipDelay);
  }
}

function createTooltipInfo(el, info) {
  let tooltip = document.createElement('section');
  tooltip.classList.add('tooltip-tutorial',`tooltip-tutorial--${info.arg}`, 'js-tooltip-interactive');
  sideCalculate(el, tooltip, info);
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

function removeTooltipInfo() {
  let tooltip = document.body.querySelector('.js-tooltip-interactive');
  if(store.getters['mod_tutorials/getInteractiveInfo'] && tooltip) {
    tooltip.remove();
  }
}


function sideCalculate(element, tooltip, side) {
  let elCoord = element.getBoundingClientRect();
  let tooltipArrow = 10;
  let isDraggable = event.currentTarget.getAttribute('draggable');
  let zoom = isDraggable !== 'false' ? 1 : store.getters['mod_workspace/GET_currentNetwork'].networkMeta.zoom;

  switch (side.arg) {
    case 'right':
      tooltip.style.top = (elCoord.top + elCoord.height / 2) * zoom +'px';
      tooltip.style.left = (elCoord.left + elCoord.width + tooltipArrow) * zoom + 'px';
      break;
    case 'right-wrap-text':
      tooltip.style.top = (elCoord.top + elCoord.height / 2) * zoom +'px';
      tooltip.style.left = (elCoord.left + elCoord.width + tooltipArrow) * zoom + 'px';
      break;
    case 'left':
      tooltip.style.top = (elCoord.top + elCoord.height / 2) * zoom +'px';
      tooltip.style.left = (elCoord.left - tooltipArrow) * zoom + 'px';
      break;
    case 'top':
      tooltip.style.top = (elCoord.top - tooltipArrow) * zoom +'px';
      tooltip.style.left = (elCoord.left + elCoord.width / 2) * zoom + 'px';
      break;
    case 'bottom':
      tooltip.style.top = (elCoord.top + elCoord.height + tooltipArrow) * zoom +'px';
      tooltip.style.left = (elCoord.left + elCoord.width / 2) * zoom + 'px';
      break;
    case 'bottom-right':
      tooltip.style.top = (elCoord.top + elCoord.height + tooltipArrow) * zoom +'px';
      tooltip.style.left = (elCoord.left - tooltipArrow) * zoom + 'px';
      break;
  }
}


