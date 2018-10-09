import Vue from 'vue'

// Vue.directive('editable-field', {
//   bind: function (el, binding, vnode) {
//     let newInput = document.createElement('input');
//     newInput.classList.add('editable-field_input');
//
//     el.classList.add('editable-field');
//     let vInput = el.appendChild(newInput);
//     vInput.value = binding.value;
//     let vInputValue = '';
//
//
//     el.addEventListener('dblclick', function() {
//       el.classList.add('edit');
//       vInput.focus();
//     });
//
//     vInput.addEventListener('blur', function() {
//       el.classList.remove('edit');
//       console.log(vInput.value);
//     });
//     //console.log(vInputValue);
//     // // spinner.className = 'progress-circular progress-circular--indeterminate primary--text';
//     // // spinner.style.cssText = 'height: 32px; width: 32px;';
//     // // spinner.innerHTML = spinnerSvg;
//     //
//   },
// });
