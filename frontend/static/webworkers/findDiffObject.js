self.addEventListener('message', function(message) {
  switch (message.data) {
    case 'close':
      self.close();
      break;
    default:
      let newNet = message.data.newVal;
      let oldNet = message.data.oldVal;

      let diff = { was: {}, became: {}};
      console.log(newNet, oldNet);
      checkObjectKeys(newNet, oldNet, diff.became, diff.was);

      console.log(diff);
      // const canvasImg = message.data.canvasImg;
      // const dataImg = message.data.dataImg;
      // dataImg.data.forEach((el, index) => canvasImg.data[index] = el);

      postMessage('new val');
  }
  function checkObjectKeys(newObj, oldObj, diffNew, diffOld) {
    for (var key in newObj) {
      if(!!newObj[key] && ( newObj[key].constructor.name === 'Object'
          || newObj[key].constructor.name === 'Array')
      ) {
        const type = newObj[key].constructor.name;
        if(JSON.stringify(newObj[key]) !== JSON.stringify(oldObj[key])) {
          if(type === 'Object') {
            console.log('has diff in obj || array');
            const nextPathNew = diffNew[key] = {};
            const nextPathOld = diffOld[key] = {};
            checkObjectKeys(newObj[key], oldObj[key], nextPathNew, nextPathOld)
          }
          if(type === 'Array') {
            diffNew[key] = newObj[key];
            diffOld[key] = oldObj[key];
          }
        }
      }
      else {
        console.log('not the obg', key, ':', newObj[key]);

        if(newObj[key] === oldObj[key]) {
          console.log('no diff');
          continue;
        }
        else {
          diffNew[key] = newObj[key];
          diffOld[key] = oldObj[key];
        }
      }
    }
  }
}, false);
