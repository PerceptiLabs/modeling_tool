import Vue from 'vue'

Vue.directive('tooltip', {
  bind: function (el, binding, vnode) {
    let hasClass = el.getAttribute('class');
    el.className = hasClass + ' tooltip-wrap';

    let tooltipBlock = document.createElement('div');
    tooltipBlock.className = 'tooltip';
    tooltipBlock.innerHTML = binding.value;

    el.appendChild(tooltipBlock)
    // let newInput = document.createElement('input');
    // newInput.classList.add('editable-field_input');

    // el.classList.add('editable-field');
    // let vInput = el.appendChild(newInput);
    // vInput.value = binding.value;
    // let vInputValue = '';
    //
    //
    // el.addEventListener('dblclick', function() {
    //   el.classList.add('edit');
    //   vInput.focus();
    // });
    //
    // vInput.addEventListener('blur', function() {
    //   el.classList.remove('edit');
    //   console.log(vInput.value);
    // });
  },
});
