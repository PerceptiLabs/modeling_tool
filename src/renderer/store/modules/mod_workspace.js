import { generateID, calcLayerPosition }  from "@/core/helpers.js";
import { widthElement } from '@/core/constants.js'
import Vue    from 'vue'
import router from '@/router'

const namespaced = true;

const state = {
  workspaceContent: [],
  currentNetwork: 0,
  dragElement: null,
  startArrowID: null,
  preArrow: {
    show: false,
    start: {x: 0, y: 0},
    stop: {x: 0, y: 0},
  },
  showStartTrainingSpinner: false,
};

const getters = {
  GET_networkIsNotEmpty(state) {
    return !!state.workspaceContent.length
  },
  GET_currentNetwork(state, getters)  {
    return getters.GET_networkIsNotEmpty
      ? state.workspaceContent[state.currentNetwork]
      : {networkID: '1'} //for the close ap when the empty workspace
  },
  GET_currentNetworkSettings(state, getters) {
    return getters.GET_networkIsNotEmpty
      ? state.workspaceContent[state.currentNetwork].networkSettings
      : {}
  },
  GET_currentNetworkElementList(state, getters) {
    return getters.GET_networkIsNotEmpty
      ? state.workspaceContent[state.currentNetwork].networkElementList
      : null
  },
  GET_networkCoreStatus(state, getters) {
    return getters.GET_networkIsNotEmpty
      ? getters.GET_currentNetwork.networkMeta.coreStatus.Status
      : null
  },
  GET_currentSelectedEl(state, getters) {
    let selectedIndex = [];
    if(getters.GET_networkIsNotEmpty) {
      let elList = getters.GET_currentNetworkElementList;
      for(var el in elList) {
        if (elList[el].layerMeta.isSelected) selectedIndex.push(elList[el]);
      }
    }
    return selectedIndex;
  },
  GET_networkIsTraining(state, getters) {
    const coreStatus = getters.GET_networkCoreStatus;
    const statusList = ['Training', 'Validation', 'Paused'];
    return statusList.includes(coreStatus) ? true : false
  },
  GET_tutorialActiveId(state, getters, rootState, rootGetters) {
    if( rootGetters['mod_tutorials/getIstutorialMode'] && rootGetters['mod_tutorials/getActiveAction']) {
      return rootGetters['mod_tutorials/getActiveAction'].dynamic_id
    }
  },
  // GET_networkCanEditLayers(state, getters) {
  //   if(getters.GET_networkIsNotEmpty) {
  //     let openStatistics = getters.GET_currentNetwork.networkMeta.openStatistics;
  //     let openTest = getters.GET_currentNetwork.networkMeta.openTest;
  //     return !(openStatistics || openTest) ? true : false;
  //   }
  // },
  GET_statisticsIsOpen(state, getters) {
    if(getters.GET_networkIsNotEmpty) {
      return getters.GET_currentNetwork.networkMeta.openStatistics;
    }
  },
  GET_testIsOpen(state, getters) {
    if(getters.GET_networkIsNotEmpty) {
      return getters.GET_currentNetwork.networkMeta.openTest;
    }
  },
  GET_networkIsOpen(state, getters) {
    if(getters.GET_networkIsNotEmpty) {
      let openStatistics = getters.GET_currentNetwork.networkMeta.openStatistics;
      let openTest = getters.GET_currentNetwork.networkMeta.openTest;
      return !(openStatistics || openTest) ? true : false;
    }
  },
  GET_networkWaitGlobalEvent(state, getters) {
    if(getters.GET_networkIsNotEmpty) {
      return getters.GET_currentNetwork.networkMeta.chartsRequest.waitGlobalEvent;
    }
  },
  GET_networkShowCharts(state, getters) {
    if(getters.GET_networkIsNotEmpty) {
      return getters.GET_currentNetwork.networkMeta.chartsRequest.showCharts;
    }
  },
  GET_networkDoRequest(state, getters) {
    if(getters.GET_networkIsNotEmpty) {
      return getters.GET_currentNetwork.networkMeta.chartsRequest.doRequest;
    }
  },
  GET_showStartTrainingSpinner(state) {
    return state.showStartTrainingSpinner
  },
};

const mutations = {
  reset_network(state) {
    state.workspaceContent = []
  },
  //---------------
  //  NETWORK
  //---------------
  set_networkName(state, {getters, value}) {
    getters.GET_currentNetwork.networkName = value
  },
  add_network (state, network) {
    //console.log(JSON.stringify(network));
    //console.log('add_network', network);
    let workspace = state.workspaceContent;
    let newNetwork = {};
    //-- DEFAULT DATA
    const defaultNetwork = {
      networkName: 'New_Network',
      networkID: '',
      networkSettings: null,
      networkMeta: {},
      networkElementList: null,
      //networkContainerList: [],
    };
    const defaultMeta = {
      openStatistics: null, //null - hide Statistics; false - close Statistics, true - open Statistics
      openTest: null,
      zoom: 1,
      netMode: 'edit',//'addArrow'
      coreStatus: {
        Status: 'Waiting' //Created, Training, Validation, Paused, Finished
      },
      chartsRequest: {
        timerID: null,
        waitGlobalEvent: false,
        doRequest: 0,
        showCharts: 0
      }
    };
    //--
    network === undefined
      ? newNetwork = defaultNetwork
      : newNetwork = network;

    newNetwork.networkMeta = defaultMeta;
    //-- Create unic ID
    if(findNetId(newNetwork, workspace) || !newNetwork.networkID) {
      newNetwork.networkID = generateID();
    }
    //console.log(newNetwork);
    //-- Check and create the position
    createPositionElements(newNetwork.networkElementList);
    //-- Add to workspace
    workspace.push(JSON.parse(JSON.stringify(newNetwork)));
    //-- Open last Network
    state.currentNetwork = workspace.length - 1;
    //-- Go to app page
    if(router.history.current.name !== 'app') {
      router.replace({name: 'app'});
    }
    function findNetId(newNet, netList) {
      let indexId = netList.findIndex((el)=> el.networkID === newNet.networkID);
      return (indexId < 0) ? false : true
    }
    function createPositionElements(list) {
      if(!list || Object.values(list)[0].layerMeta.position.top !== null) {
        return;
      }
      else {
        //let elList = JSON.parse(JSON.stringify(Object.values(list)));
        let elList = Object.values(list);
        const elGap = 60;
        const widthEl = widthElement;
        const defaultPosition = { top: 0, left: 0 };
        let arrLeft = [];
        let arrTop = [];

        elList[0].layerMeta.position = {...defaultPosition};
        elList.forEach((el)=> {
          if(el.layerMeta.position.top === null) {
            el.layerMeta.position = {...defaultPosition};

            let newElPosition = findFreePosition(el.layerMeta.position, elList, elGap, widthEl, el.layerId);
            //console.log(newElPosition);
            //el.layerMeta.position.top = newElPosition.top;
            arrTop.push(newElPosition.top);
            //el.layerMeta.position.left = newElPosition.left;
            arrLeft.push(newElPosition.left);
          }

          if(el.connectionOut.length) {
            let outLength = el.connectionOut.length;
            el.connectionOut.forEach((elId, i)=> {
              if(list[elId].layerMeta.position.top === null) {
                const top = el.layerMeta.position.top + (elGap - ((outLength / 2) * (elGap + widthEl)) + ((elGap + widthEl) * i));
                const left = el.layerMeta.position.left + elGap + widthEl;

                let newPosition = findFreePosition({top, left}, elList, elGap, widthEl, list[elId].layerId);

                list[elId].layerMeta.position.top = newPosition.top;
                arrTop.push(newPosition.top);
                list[elId].layerMeta.position.left = newPosition.left;
                arrLeft.push(newPosition.left);
              }
            })
          };
        });

        const netHeight = (Math.max(...arrTop) - Math.min(...arrTop));
        const netWidth = (Math.max(...arrLeft) - Math.min(...arrLeft));
        const corrTop = (document.body.clientHeight /2) - (netHeight/2);
        const corrLeft = (document.body.clientWidth /2) - (netWidth/2) - 300;
        const correctionTop = corrTop > 0 ? corrTop : elGap;
        const correctionLeft = corrLeft > 0 ? corrLeft : elGap;

        elList.forEach((el)=> {
          el.layerMeta.position.top = el.layerMeta.position.top + correctionTop;
          el.layerMeta.position.left = el.layerMeta.position.left + correctionLeft;
        })
      }
    };
    function findFreePosition(currentPos, checkingList, indent, widthEl, currentId) {
      let checkPosition = currentPos;
      checkingPosition();

      return checkPosition;

      function checkingPosition() {
        return checkingList.forEach((el)=> {
          if(currentId === el.layerId ) return;
          if(
              checkPosition.top > (el.layerMeta.position.top - indent/2)
              && checkPosition.top < (el.layerMeta.position.top + indent/2 + widthEl)
              && checkPosition.left > (el.layerMeta.position.left - indent/2)
              && checkPosition.left < (el.layerMeta.position.left + indent/2 + widthEl)
            ) {
                checkPosition.top = checkPosition.top + indent;
                checkingPosition();
                return
              }
          else return checkPosition
        })
      }
    }
  },
  DELETE_network(state, index) {
    if(state.currentNetwork >= index) {
      const index = state.currentNetwork - 1;
      state.currentNetwork = index < 0 ? 0 : index
    }
    state.workspaceContent.splice(index, 1);
  },
  //---------------
  //  NETWORK SETTINGS
  //---------------
  set_networkSettings(state, {getters, value}) {
    getters.GET_currentNetwork.networkSettings = value
  },
  //---------------
  //  LOADER FOR TRAINING
  //---------------
  SET_showStartTrainingSpinner(state, value) {
    state.showStartTrainingSpinner = value;
  },
  //---------------
  //  NETWORK META
  //---------------
  set_netMode(state, {getters, value}) {
    getters.GET_currentNetwork.networkMeta.netMode = value;
  },
  set_openStatistics(state, {dispatch, getters, value}) {
    getters.GET_currentNetwork.networkMeta.openStatistics = value;
    let isTraining = getters.GET_networkIsTraining;
    if(isTraining) {
      value
        ? dispatch('mod_api/API_setHeadless', false, {root: true})
        : dispatch('mod_api/API_setHeadless', true, {root: true})
    }
    if(value && getters.GET_testIsOpen !== null) {
      getters.GET_currentNetwork.networkMeta.openTest = false;
    }
    if(value) {
      dispatch('mod_statistics/STAT_defaultSelect', null, {root: true});
      //dispatch('mod_events/EVENT_chartResize', null, {root: true});
    }
  },
  set_openTest(state, {dispatch, getters, value}) {
    getters.GET_currentNetwork.networkMeta.openTest = value;
    if(value && getters.GET_statisticsIsOpen !== null) {
      getters.GET_currentNetwork.networkMeta.openStatistics = false;
    }
    if(value) {
      dispatch('mod_statistics/STAT_defaultSelect', null, {root: true});
      //dispatch('mod_events/EVENT_chartResize', null, {root: true});
    }
  },
  set_statusNetworkCore(state, {getters, value}) {
    getters.GET_currentNetwork.networkMeta.coreStatus = value;
  },
  set_statusNetworkCoreStatus(state, {getters, value}) {
    getters.GET_currentNetwork.networkMeta.coreStatus.Status = value;
  },
  set_statusNetworkCoreStatusProgressClear(state, {getters}) {
    if(getters.GET_currentNetwork.networkMeta.coreStatus.Status.Progress) {
      getters.GET_currentNetwork.networkMeta.coreStatus.Status.Progress = 0;
    }
  },
  set_statusNetworkZoom(state, {getters, value}) {
    getters.GET_currentNetwork.networkMeta.zoom = value;
  },
  set_charts_doRequest(state, {getters, networkIndex}) {
    networkIndex
      ? state.workspaceContent[networkIndex].networkMeta.chartsRequest.doRequest++ //TODO проверить что счетчики идут паралельно в нескольких networks
      : getters.GET_currentNetwork.networkMeta.chartsRequest.doRequest++
  },
  set_charts_showCharts(state, {getters, networkIndex}) {
    networkIndex
      ? state.workspaceContent[networkIndex].networkMeta.chartsRequest.showCharts++
      : getters.GET_currentNetwork.networkMeta.chartsRequest.showCharts++
  },
  set_charts_timerID(state, {getters, timerId}) {
    getters.GET_currentNetwork.networkMeta.chartsRequest.timerID = timerId;
  },
  set_statusNetworkWaitGlobalEvent(state, {getters, value}) {
    getters.GET_currentNetwork.networkMeta.chartsRequest.waitGlobalEvent = value;
  },
  //---------------
  //  NETWORK ELEMENTS
  //---------------
  SET_elementName(state, value) {
    currentElement(value.id).layerName = value.setValue
  },
  add_element(state, {getters, event}) {
    let duplicatePositionIndent = 30;
    let newEl = state.dragElement
      ? state.dragElement
      : createNetElement(event);
    
    let top = newEl.layerMeta.position.top;
    let left = newEl.layerMeta.position.left;
    let zoom = getters.GET_currentNetwork.networkMeta.zoom;
    let elementList = getters.GET_currentNetworkElementList;

    newEl.layerMeta.tutorialId = getters.GET_tutorialActiveId;
    newEl.layerMeta.position.top = (event.offsetY - top)/zoom;
    newEl.layerMeta.position.left = (event.offsetX - left)/zoom;
    let depth = checkPosition(newEl, elementList);
    if(depth > 0) {
      newEl.layerMeta.position.top = newEl.layerMeta.position.top + (duplicatePositionIndent * depth);
      newEl.layerMeta.position.left = newEl.layerMeta.position.left + (duplicatePositionIndent * depth);
    }
    depth = 0;

    updateLayerName(newEl, elementList, 1);

    if(!elementList) state.workspaceContent[state.currentNetwork].networkElementList = {};
    Vue.set(state.workspaceContent[state.currentNetwork].networkElementList, newEl.layerId, newEl);
    state.dragElement = null;

    function checkPosition(el, list) {
      let depth = 0;

      runChecking(el, list);
      return depth;

      function runChecking(el, list) {
        let top = el.layerMeta.position.top + (duplicatePositionIndent * depth);
        let left = el.layerMeta.position.left + (duplicatePositionIndent * depth);
        for(let existID in list) {
          let existEl = list[existID];
          let elTop = existEl.layerMeta.position.top;
          let elLeft = existEl.layerMeta.position.left;
          if(top === elTop && left === elLeft) {
            ++depth;
            runChecking(el, list);
            return
          }
        }
      }
    }
  },
  delete_element(state, {getters, dispatch}) {
    let arrSelect = getters.GET_currentSelectedEl;
    if(!arrSelect.length) return;
    let arrSelectID = [];
    let net = {...getters.GET_currentNetworkElementList};
    deleteElement(arrSelect);

    for(let el in net) {
      net[el].connectionOut = net[el].connectionOut.filter((connect)=>{
        return !arrSelectID.includes(connect)
      });
      net[el].connectionArrow = net[el].connectionArrow.filter((connect)=>{
        return !arrSelectID.includes(connect)
      });
      net[el].connectionIn  = net[el].connectionIn.filter((connect)=>{
        return !arrSelectID.includes(connect)
      });
    }
    state.workspaceContent[state.currentNetwork].networkElementList = net;
    dispatch('mod_events/EVENT_calcArray', null, {root: true});
    dispatch('mod_api/API_getOutputDim', null, {root: true});

    function deleteElement(list) {
      list.forEach((el)=> {
        if(el.componentName === 'LayerContainer') {
          deleteElement(Object.values(el.containerLayersList))
        }
        delete net[el.layerId];
        arrSelectID.push(el.layerId);
      });
    }
  },
  add_arrow(state, {dispatch, stopID}) {
    let startID = state.startArrowID;
    if(stopID === startID) return;

    let findArrow = currentElement(startID).connectionOut.findIndex((element)=> element === stopID );
    if(findArrow !== -1) {
      dispatch('globalView/GP_infoPopup', 'Connection already exists!', {root: true});
      return
    }
    if(currentElement(startID).componentName === 'LayerContainer' || currentElement(stopID).componentName === 'LayerContainer') {
      dispatch('globalView/GP_infoPopup', 'Cannot create connection to Layer Container!', {root: true});
      return
    }

    currentElement(startID).connectionOut.push(stopID.toString()); //ID.toString need for the core
    currentElement(startID).connectionArrow.push(stopID.toString());
    currentElement(stopID).connectionIn.push(startID.toString());
    state.startArrowID = null;
    dispatch('mod_events/EVENT_calcArray', null, {root: true})
  },
  delete_arrow(state,{dispatch, arrow}) {
    let startID = arrow.startID;
    let stopID = arrow.stopID;
    let elStart = currentElement(startID);
    let elStop = currentElement(stopID);

    if(elStart.componentName === 'LayerContainer' || elStop.componentName === 'LayerContainer') {
      dispatch('globalView/GP_infoPopup', 'To remove the connection, please open the Layer Container', {root: true});
      return
    }

    let newConnectionOut = currentElement(startID).connectionOut.filter((item)=> item !== stopID);
    let newConnectionArrow = currentElement(startID).connectionArrow.filter((item)=> item !== stopID);
    let newConnectionIn = currentElement(stopID).connectionIn.filter((item)=> item !== startID);

    currentElement(startID).connectionOut = newConnectionOut;
    currentElement(startID).connectionArrow = newConnectionArrow;
    currentElement(stopID).connectionIn = newConnectionIn;
    dispatch('mod_events/EVENT_calcArray', null, {root: true})
  },

  /*-- NETWORK ELEMENTS SETTINGS --*/
  set_elementSettings(state, settings) {
    currentElement(settings.elId).layerSettings = settings.set;
    currentElement(settings.elId).layerCode = settings.code;
    currentElement(settings.elId).layerSettingsTabName = settings.tabName;
  },

  /*-- NETWORK ELEMENTS META --*/
  set_elementUnselect(state, {getters}) {
    for(let layer in getters.GET_currentNetworkElementList) {
      currentElement(layer).layerMeta.isSelected = false;
    }
  },
  set_elementSelect(state, value) {
    currentElement(value.id).layerMeta.isSelected = value.setValue;
  },
  set_elementSelectAll(state, {getters}) {
    for(let layer in getters.GET_currentNetworkElementList) {
      currentElement(layer).layerMeta.isSelected = true;
    }
  },
  set_elementMultiSelect(state, value) {
    currentElement(value.id).layerMeta.isSelected = value.setValue;
  },
  SET_elementLock(state, id) {
    let elMeta = currentElement(id).layerMeta;
    elMeta.isLock = !elMeta.isLock
  },
  SET_elementVisible(state, id) {
    let elMeta = currentElement(id).layerMeta;
    elMeta.isInvisible = !elMeta.isInvisible
  },
  SET_elementBgColor(state, value) {
    let elMeta = currentElement(value.id).layerMeta;
    elMeta.layerBgColor = value.color
  },
  SET_elementNone(state, {id, value}) {
    let el = currentElement(id);
    el.layerNone = value
  },
  change_elementPosition(state, value) {
    let elPosition = currentElement(value.id).layerMeta.position;
    elPosition.top = value.top;
    elPosition.left = value.left;
  },
  set_elementInputDim(state, {getters, value}) {
    for(let element in getters.GET_currentNetworkElementList) {
      currentElement(element).layerMeta.InputDim = value[element]
    }
  },
  set_elementOutputDim(state, {getters, value}) {
    for(let element in getters.GET_currentNetworkElementList) {
      currentElement(element).layerMeta.OutputDim = value[element].Dim;
      currentElement(element).layerCodeError = value[element].Error
    }
  },

  //---------------
  //  NETWORK CONTAINER
  //---------------
  add_container(state, {getters, commit, dispatch}) {
    let arrSelect = getters.GET_currentSelectedEl;
    let isValid = true;
    let elementList = getters.GET_currentNetworkElementList;
    /* validations */
    if(arrSelect.length === 0) isValid = false;
    if(arrSelect.length === 1) {
      dispatch('globalView/GP_infoPopup', 'At least 2 elements are needed to create a group', {root: true});
      isValid = false;
    }
    arrSelect.forEach((item)=> {
      if(item.componentName === 'LayerContainer') {
        dispatch('globalView/GP_infoPopup', 'You cannot create a Layer Container inside a Layer Container! Function in development', {root: true});
        isValid = false;
      }
    });
    if(!isValid) {
      dispatch('SET_elementUnselect');
      return;
    }
    /* END validations */
    //let net = getters.GET_currentNetworkElementList;
    let newContainer = createClearContainer(arrSelect);

    updateLayerName(newContainer, elementList, 1);

    Vue.set(state.workspaceContent[state.currentNetwork].networkElementList, newContainer.layerId, newContainer);
    commit('close_container', {container: newContainer, getters, dispatch});
    commit('set_elementUnselect', {getters});

    function createClearContainer(selectList) {
      let fakeEvent = {
        timeStamp: generateID(),
        target: {
          dataset: {
            layer: 'Layer Container',
            type: 'Сontainer',
            component: 'LayerContainer',
          },
          clientHeight: 0,
          clientWidth: 0
        }
      };
      let container = createNetElement(fakeEvent);
      container.containerLayersList = {};
      selectList.forEach((el)=>{
        container.containerLayersList[el.layerId] = el;
      });
      return container
    }
  },
  close_container(state, {container, getters, dispatch}) {
    let network = getters.GET_currentNetworkElementList;
    let layerCont = calcContainer(container, network);
    saveDifferentPosition(layerCont);

    for(let idEl in layerCont.containerLayersList) {
      network[idEl].layerNone = true;
    }
    network[container.layerId].layerNone = false;
    dispatch('mod_events/EVENT_calcArray', null, {root: true});

    function calcContainer(container, net) {
      let el = container;
      let listInside = el.containerLayersList;
      let allIdEl = [];
      let allIdOut = [];
      let allIdIn = [];
      let allTop = [];
      let allLeft = [];

      for(let elID in listInside) {
        let item = listInside[elID];
        allIdEl.push(elID);
        allIdOut = [...allIdOut, ...new Set(item.connectionOut)];
        allIdIn  = [...allIdIn,  ...new Set(item.connectionIn)];
        allTop.push(item.layerMeta.position.top);
        allLeft.push(item.layerMeta.position.left);
      }

      el.layerMeta.position.top = calcPosition(allTop);
      el.layerMeta.position.left = calcPosition(allLeft);
      el.connectionOut = calcConnection(allIdOut, allIdEl);
      el.connectionArrow = [...new Set(el.connectionOut)];
      el.connectionIn = calcConnection(allIdIn, allIdEl);

      el.connectionIn.forEach((elNextId)=>{
        if(!net[elNextId].connectionArrow.includes(el.layerId)) {
          net[elNextId].connectionArrow.push(el.layerId)
        }
        for(let elID in net) {
          let item = net[elID];
          if(item.componentName === 'LayerContainer') {
            let arrKeys = Object.keys(item.containerLayersList);
            if(arrKeys.includes(elNextId) && !item.connectionArrow.includes(el.layerId)){
              item.connectionArrow.push(el.layerId)
            }
          }
        }
      });
      el.connectionOut.forEach((elNextId)=>{
        for(let elID in net) {
          let item = net[elID];
          if(item.componentName === 'LayerContainer') {
            let arrKeys = Object.keys(item.containerLayersList);
            if(arrKeys.includes(elNextId) && !el.connectionArrow.includes(item.layerId)){
              el.connectionArrow.push(item.layerId)
            }
          }
        }
      });
      return el;


      function calcConnection(arrConnectionId, arrInsideId) {
        return arrConnectionId.filter((id)=> !arrInsideId.includes(id))
      }
      function calcPosition(arrIn) {
        const num = (Math.max(...arrIn) + Math.min(...arrIn))/2;
        return calcLayerPosition(num);
      }
    }
    function saveDifferentPosition(containerEl) {
      let listInside = containerEl.containerLayersList;
      let containerTop = containerEl.layerMeta.position.top;
      let containerLeft = containerEl.layerMeta.position.left;
      for(let elID in listInside) {
        let item = listInside[elID];
        let itemTop = item.layerMeta.position.top;
        let itemLeft = item.layerMeta.position.left;
        item.layerMeta.containerDiff.top = itemTop - containerTop;
        item.layerMeta.containerDiff.left = itemLeft - containerLeft;
      }
    }
  },
  open_container(state, {container, getters, dispatch}) {
    let net = getters.GET_currentNetworkElementList;
    calcLayerPosition(container);

    for(let idEl in container.containerLayersList) {
      net[idEl].layerNone = false;
    }
    net[container.layerId].layerNone = true;
    dispatch('mod_events/EVENT_calcArray', null, {root: true});

    function calcLayerPosition(containerEl) {
      let listInside = containerEl.containerLayersList;
      let containerTop = containerEl.layerMeta.position.top;
      let containerLeft = containerEl.layerMeta.position.left;
      for(let elID in listInside) {
        let item = listInside[elID];
        let diffTop = item.layerMeta.containerDiff.top;
        let diffLeft = item.layerMeta.containerDiff.left;
        item.layerMeta.position.top = diffTop + containerTop;
        item.layerMeta.position.left = diffLeft + containerLeft;
      }
    }
  },
  toggle_container(state, {val, container, dispatch, getters}) {
    val
      ? dispatch('CLOSE_container', container)
      : dispatch('OPEN_container', container);
    if(getters.GET_networkIsOpen) dispatch('SET_elementUnselect');
  },
  ungroup_container(state, {dispatch, getters}) {
    let net = {...getters.GET_currentNetworkElementList};
    let container = getters.GET_currentSelectedEl[0];
    dispatch('OPEN_container', container);
    for(let idEl in net) {
      let el = net[idEl];
      el.connectionArrow = el.connectionArrow.filter((arrow)=> arrow !== container.layerId)
    }
    delete net[container.layerId];
    state.workspaceContent[state.currentNetwork].networkElementList = net;
  },
  //---------------
  //  OTHER
  //---------------
  SET_currentNetwork(state, value) {
    state.currentNetwork = value
  },
  ADD_dragElement(state, event) {
    state.dragElement = createNetElement(event);
  },
  SET_startArrowID (state, value) {
    state.startArrowID = value
  },
  SET_preArrowStart (state, value) {
    state.preArrow.start = value;
    state.preArrow.stop = value;
    state.preArrow.show = true;
  },
  SET_preArrowStop (state, value) {
    state.preArrow.stop = value
  },
  CLEAR_preArrow (state) {
    state.preArrow = {
      show: false,
      start: {x: 0, y: 0},
      stop: {x: 0, y: 0},
    }
  },
};

const actions = {
  //---------------
  //  NETWORK
  //---------------
  ADD_network({commit, dispatch}, network) {
    commit('add_network', network)
  },
  SET_networkName({commit, getters}, value) {
    commit('set_networkName', {getters, value})
  },
  SET_networkSettings({commit, getters}, value) {
    commit('set_networkSettings', {getters, value})
  },
  SET_networkElementList({commit, getters}, value) {
    commit('set_networkElementList', {getters, value})
  },
  SET_netMode({commit, getters}, value) {
    commit('set_netMode', {getters, value})
  },
  SET_openStatistics({commit, getters, dispatch}, value) {
    commit('set_openStatistics', {dispatch, getters, value})
  },
  SET_openTest({commit, getters, dispatch}, value) {
    commit('set_openTest', {dispatch, getters, value})
  },
  SET_statusNetworkCore({commit, getters}, value) {
    commit('set_statusNetworkCore', {getters, value})
  },
  SET_statusNetworkCoreStatus({commit, getters}, value) {
    commit('set_statusNetworkCoreStatus', {getters, value})
  },
  SET_statusNetworkCoreStatusProgressClear({commit, getters}) {
    commit('set_statusNetworkCoreStatusProgressClear', {getters})
  },
  SET_statusNetworkZoom({commit, getters}, value) {
    commit('set_statusNetworkZoom', {getters, value})
  },
  SET_statusNetworkWaitGlobalEvent({commit, getters}, value) {
    commit('set_statusNetworkWaitGlobalEvent', {getters, value})
  },
  RESET_network({commit}) {
    commit('reset_network')
  },
  CHECK_requestInterval({dispatch, commit, rootState, getters, state}, time) {
    //console.log(`request -> can show`, `${time}ms`);
    const timeRequest = time + 500;
    const isLongRequest = timeRequest > rootState.globalView.timeIntervalDoRequest;
    if(isLongRequest) {
      const currentMeta = getters.GET_currentNetwork.networkMeta.chartsRequest;
      clearInterval(currentMeta.timerID);
      console.log('new time', timeRequest);
      dispatch('globalView/SET_timeIntervalDoRequest', timeRequest, {root: true});
      dispatch('EVENT_startDoRequest', true);
    }
  },
  EVENT_startDoRequest({dispatch, commit, rootState, getters, state}, isStart) {
    //console.log('EVENT_startDoRequest', isStart);
    const currentMeta = getters.GET_currentNetwork.networkMeta.chartsRequest;
    if(currentMeta === undefined) return;
    const timeInterval = rootState.globalView.timeIntervalDoRequest;

    dispatch('SET_statusNetworkWaitGlobalEvent', isStart);
    if(isStart) {
      let timerId = setInterval(()=> {
        dispatch('EVENT_chartsRequest')
      }, timeInterval);
      commit('set_charts_timerID', {getters, timerId});
    }
    else {
      clearInterval(currentMeta.timerID);
    }
  },
  EVENT_chartsRequest({dispatch, commit, rootState, getters, state}) {
    var networkIndex = state.currentNetwork;
    commit('set_charts_showCharts', {getters, networkIndex});
    dispatch('mod_api/API_updateResults', null, {root: true})
      .then(()=> {
        commit('set_charts_doRequest', {getters, networkIndex});
        dispatch('mod_api/API_getStatus', null, {root: true});
      });
  },
  EVENT_onceDoRequest({dispatch, commit, rootState, getters}, isStart) {
    dispatch('mod_api/API_updateResults', null, {root: true})
      .then(()=> {
        commit('set_charts_doRequest', {getters});
        dispatch('mod_api/API_getStatus', null, {root: true});
      });
  },
  //---------------
  //  NETWORK ELEMENTS
  //---------------
  SET_elementSettings({commit}, settings) {
    commit('set_elementSettings', settings)
  },
  ADD_element({commit, getters}, event) {
    commit('add_element', {getters, event})
  },
  DELETE_element({commit, getters, dispatch}) {
    commit('delete_element', {getters, dispatch, commit})
  },
  ADD_arrow({commit, getters, dispatch}, stopID) {
    commit('add_arrow', {dispatch, stopID})
  },
  DELETE_arrow({commit, getters, dispatch}, arrow) {
    commit('delete_arrow', {dispatch, arrow})
  },
  SET_elementUnselect({commit, getters}) {
    commit('set_elementUnselect', {getters})
  },
  SET_elementSelect({commit}, value) {
    commit('set_elementSelect', value)
  },
  SET_elementSelectAll({commit, getters}) {
    commit('set_elementSelectAll', {getters})
  },
  SET_elementMultiSelect({commit}, value) {
    commit('set_elementMultiSelect', value)
  },
  SET_elementInputDim({commit, getters}, value) {
    commit('set_elementInputDim', {getters, value})
  },
  SET_elementOutputDim({commit, getters}, value) {
    commit('set_elementOutputDim', {getters, value})
  },
  CHANGE_elementPosition({commit, getters}, value) {
    commit('change_elementPosition', value)
  },
  //---------------
  //  NETWORK CONTAINER
  //---------------
  ADD_container({commit, getters, dispatch}, event) {
    if(getters.GET_networkIsOpen) commit('add_container', {getters, commit, dispatch});
  },
  OPEN_container({commit, getters, dispatch}, container) {
    commit('open_container', {container, getters, dispatch})
  },
  CLOSE_container({commit, getters, dispatch}, container) {
    commit('close_container', {container, getters, dispatch})
  },
  TOGGLE_container({commit, getters, dispatch}, {val, container}) {
    commit('toggle_container', {val, container, dispatch, getters})
  },
  UNGROUP_container({commit, getters, dispatch}, container) {
    if(getters.GET_networkIsOpen) commit('ungroup_container', {container, dispatch, getters})
  },
};

export default {
  namespaced,
  getters,
  state,
  mutations,
  actions,
}

function updateLayerName(el, net, n){
  const layerName = el.layerName;
  if (net !== null) {
    let netArr = Object.values(net);    
    if (findValue(netArr, layerName+'_'+n).length) {
      n++;
      updateLayerName(el, net, n);
    } else {
      el.layerName = layerName+'_'+n;
    }
    function findValue(arr, value) {
      return arr.filter(object => object.layerName.toLowerCase() === value.toLowerCase());
    }   
  }else{
    el.layerName = layerName+'_'+n;
  } 
}

function currentElement(id) {
  return state.workspaceContent[state.currentNetwork].networkElementList[id];
}
const createNetElement = function (event) {
  return {
    layerId: generateID(),
    layerName: event.target.dataset.layer,
    layerType: event.target.dataset.type,
    layerSettings: event.layerSettings ? event.layerSettings : null,
    layerSettingsTabName: undefined,
    layerCode: '',
    layerCodeError: null,
    layerNone: false,
    layerMeta: {
      isInvisible: false,
      isLock: false,
      isSelected: false,
      position: {
        top: event.target.clientHeight/2,
        left: event.target.clientWidth/2,
      },
      tutorialId: '',
      OutputDim: '',
      InputDim: '',
      layerContainerName: '',
      layerBgColor: '',
      containerDiff: {
        top: 0,
        left: 0,
      }
    },
    checkpoint: [],
    endPoints: [],
    componentName: event.target.dataset.component,
    connectionOut: [],
    connectionIn: [],
    connectionArrow: [],
    //calcAnchor: { top: [], right: [], bottom: [], left: []}
  };
}