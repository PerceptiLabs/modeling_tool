const findIndexId = function (arr, ID) {
  return arr.findIndex(function(item) {return item.layerId == ID});
};

export {findIndexId}
