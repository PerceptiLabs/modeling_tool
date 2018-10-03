function add123 (num) {
  let x = num.x;
  let y = num.y;
  //return x + y
  console.log(x+y)
}

function init (name, value) {
  console.log('init');
  console.log(name);
  console.log(window[name]);
  //return window[name](value);
}


init('add123', {x: 1, y: 2});
