import { generateID, calcLayerPosition, deepCopy, deepCloneNetwork, isLocalStorageAvailable, stringifyNetworkObjects }  from "@/core/helpers.js";
import { widthElement } from '@/core/constants.js'
import Vue    from 'vue'
import router from '@/router'
import {isElectron} from "@/core/helpers";

const namespaced = true;

const state = {
  workspaceContent: [],
  currentNetwork: 0,
  dragElement: null,
  startArrowID: null,
  webLoadingDataFlag: false,
  preArrow: {
    show: false,
    start: {x: 0, y: 0},
    stop: {x: 0, y: 0},
  },
  positionForCopyElement: {
    cursor: {x: 0, y: 0},
    elementsPosition: [],
    cursorInsideWorkspace: true
  },
  showStartTrainingSpinner: false,
  isOpenElement: false,
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
  GET_currentNetworkId(state, getters) {
    return getters.GET_networkIsNotEmpty
      ? state.workspaceContent[state.currentNetwork].networkID
      : 0
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
    return !!statusList.includes(coreStatus)
  },
  GET_tutorialActiveId(state, getters, rootState, rootGetters) {
    if( rootGetters['mod_tutorials/getIstutorialMode'] && rootGetters['mod_tutorials/getActiveAction']) {
      return rootGetters['mod_tutorials/getActiveAction'].dynamic_id
    }
  },
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
      return !(openStatistics || openTest);
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
  GET_enableHotKeyElement(state, getters, rootState) {
    return !state.isOpenElement && getters.GET_networkIsOpen && rootState.mod_events.isEnableCustomHotKey
  },
  GET_positionForCopyElement(state) {
    return state.positionForCopyElement;
  },
  GET_cursorInsideWorkspace(state) {
    return state.positionForCopyElement.cursorInsideWorkspace;
  }
};

const mutations = {
  reset_network(state) {
    state.workspaceContent = []
  },
  RESTORE_network(state, val) {
    state.workspaceContent = val.workspaceContent;
    state.currentNetwork = val.currentNetwork;
  },
  //---------------
  //  LOCALSTORAGE
  //---------------
  set_workspacesInLocalStorage(state) {
    if (!isLocalStorageAvailable()) { return; }

    try {
      const networkIDs = [];

      state.workspaceContent.forEach(network => {
        networkIDs.push(network.networkID);

        localStorage.setItem(`_network.${network.networkID}`, stringifyNetworkObjects(network));
      });

      localStorage.setItem('_network.ids', JSON.stringify(networkIDs.sort()));
    } catch (error) {
      // console.error('Error persisting networks to localStorage', error);
    }
  },
  get_workspacesFromLocalStorage(state) {
    // this function is invoked when the pageQuantum (workspace) component is created
    // the networks that were saved in the localStorage are hydrated

    const activeNetworkIDs = localStorage.getItem('_network.ids') || [];
    const keys = Object.keys(localStorage)
      .filter(key =>
        key.startsWith('_network.') &&
        key !== '_network.ids'&&
        key !== '_network.meta')
        .sort();

    for(const key of keys) {
      const networkID = key.replace('_network.', '');

      // _network.<networkID> entries in localStorage are only cleared on load
      if (!activeNetworkIDs.includes(networkID)) {
        localStorage.removeItem(key);
        continue;
      }

      const networkIsLoaded = state.workspaceContent
        .some(networkInWorkspace => networkInWorkspace.networkID === networkID)

      if (!networkIsLoaded) {
        const network = JSON.parse(localStorage.getItem(key));

        // remove focus from previous focused network elements
        if (network.networkElementList) {
          Object.keys(network.networkElementList).map(elKey => {
            network.networkElementList[elKey].layerMeta.isSelected = false;
          });
        }

        // clears the handle of the setInterval function
        // this value is used to determine if a new setInterval call should be made
        network.networkMeta.chartsRequest.timerID = null;



        state.workspaceContent.push(network);
      }
    }
  },
  set_lastActiveTabInLocalStorage(state, networkID) {
    if (!isLocalStorageAvailable()) { return; }

    localStorage.setItem('_network.meta', JSON.stringify({ 'lastActiveNetworkID': networkID }));

  },
  get_lastActiveTabFromLocalStorage(state) {
    // function for remembering the last active tab
    const activeNetworkIDs = JSON.parse(localStorage.getItem('_network.ids')) || [];
    const networkMeta = JSON.parse(localStorage.getItem('_network.meta')) || {};

    const currentNetworkID = networkMeta.lastActiveNetworkID;
    const index = activeNetworkIDs.findIndex((el) => el === currentNetworkID);

    if (index > 0) {
      state.currentNetwork = index;
    }
  },
  //---------------
  //  NETWORK
  //---------------
  set_networkName(state, {getters, value}) {
    getters.GET_currentNetwork.networkName = value
  },
  set_networkRootFolder(state, {getters, value}) {
    getters.GET_currentNetwork.networkRootFolder = value
  },
  add_network (state, network) {
    let workspace = state.workspaceContent;
    let newNetwork = {};
    //-- DEFAULT DATA
    const defaultNetwork = {
      networkName: 'New_Model',
      networkID: '',
      networkMeta: {},
      networkElementList: [],
      networkRootFolder: ''
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
    //-- Check and create the position
    createPositionElements(newNetwork.networkElementList);
    //-- Add to workspace
    workspace.push(deepCopy(newNetwork));
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
      if(!list || list.length === 0 || Object.values(list)[0].layerMeta.position.top !== null) {
        return;
      }
      else {
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
            arrTop.push(newElPosition.top);
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
  delete_network(state, index) {
    if(state.currentNetwork >= index) {
      const index = state.currentNetwork - 1;
      state.currentNetwork = index < 0 ? 0 : index
    }
    state.workspaceContent.splice(index, 1);
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
    if(value && getters.GET_statisticsIsOpen !== null) {
      getters.GET_currentNetwork.networkMeta.openStatistics = false;
    }
    if(value) {
      getters.GET_currentNetwork.networkMeta.openTest = false;
      dispatch('mod_statistics/STAT_defaultSelect', null, {root: true});
      setTimeout(()=> {
        getters.GET_currentNetwork.networkMeta.openTest = true
      }, 0)
      //dispatch('mod_events/EVENT_chartResize', null, {root: true});
    }
    else getters.GET_currentNetwork.networkMeta.openTest = value;
  },
  set_statusNetworkCore(state, {getters, value}) {
    if(getters.GET_currentNetwork.networkMeta) {
      getters.GET_currentNetwork.networkMeta.coreStatus = value;
    }
  },
  set_statusNetworkCoreStatus(state, {getters, value}) {
    if(getters.GET_currentNetwork.networkMeta) {
      getters.GET_currentNetwork.networkMeta.coreStatus.Status = value;
    }
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
  SET_CopyCursorPosition(state, position) {
    state.positionForCopyElement.cursor.x = position.x;
    state.positionForCopyElement.cursor.y = position.y;
  },
  SET_CopyElementsPosition(state, position) {
    state.positionForCopyElement.elementsPosition.push({left: position.left, top: position.top});
  },
  SET_cursorInsideWorkspace(state, value) {
    state.positionForCopyElement.cursorInsideWorkspace = value
  },
  CLEAR_CopyElementsPosition(state) {
    state.positionForCopyElement.elementsPosition = [];
  },
  SET_elementName(state, value) {
    currentElement(value.id).layerName = value.setValue
  },
  add_element(state, {getters, dispatch, event}) {
    let duplicatePositionIndent = 60;
    let cursorPosition = getters.GET_positionForCopyElement.cursor;
    let firstCopyPositionElement = getters.GET_positionForCopyElement.elementsPosition[0];
    let isCursorInsideWorkspace = getters.GET_cursorInsideWorkspace;
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

    if(isCursorInsideWorkspace && depth > 0) {
      newEl.layerMeta.position.top =  (cursorPosition.y + newEl.layerMeta.position.top) - firstCopyPositionElement.top - duplicatePositionIndent;
      newEl.layerMeta.position.left =  (cursorPosition.x + newEl.layerMeta.position.left) - firstCopyPositionElement.left - duplicatePositionIndent;
    }
    else {
      newEl.layerMeta.position.top = newEl.layerMeta.position.top + (duplicatePositionIndent * depth);
      newEl.layerMeta.position.left = newEl.layerMeta.position.left + (duplicatePositionIndent * depth);
    }
    depth = 0;

    updateLayerName(newEl, elementList, 1);

    if(!elementList || elementList.length === 0) state.workspaceContent[state.currentNetwork].networkElementList = {};
    Vue.set(state.workspaceContent[state.currentNetwork].networkElementList, newEl.layerId, newEl);
    state.dragElement = null;
    dispatch('mod_workspace-history/PUSH_newSnapshot', null, {root: true});

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
  async delete_element(state, {getters, dispatch}) {
    let arrSelect = getters.GET_currentSelectedEl;
    if(!arrSelect.length) return;
    let arrSelectID = [];
    let linkedNet = getters.GET_currentNetworkElementList;
    removeIsSelectedAfterDeleteItems(arrSelect);
    // make new history with unselected item
    await dispatch('mod_events/EVENT_calcArray', null, {root: true});

    let net = {...linkedNet};
    deleteElement(arrSelect);
    for(let el in net) {
      let element = net[el];
      element.connectionOut = element.connectionOut.filter((connect)=>{
        return !arrSelectID.includes(connect)
      });
      element.connectionArrow = element.connectionArrow.filter((connect)=>{
        return !arrSelectID.includes(connect)
      });
      element.connectionIn  = element.connectionIn.filter((connect)=>{
        return !arrSelectID.includes(connect)
      });

      if(element.layerNone && element.containerLayersList) {
        arrSelect.forEach(select => {
          element.layerNone = false;  // (close layersContainer) for remove elements from Layers
          delete element.containerLayersList[select.layerId];
          element.layerNone = true;
          let isLastContainerElement = Object.keys(element.containerLayersList).length <= 1;
          if (isLastContainerElement) delete net[el];
        });
      }
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
    function removeIsSelectedAfterDeleteItems(arrSelect){
      arrSelect.forEach((el)=> {
        linkedNet[el.layerId].layerMeta.isSelected = false;
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
    if(currentElement(startID).componentName === 'LayerContainer'
      || currentElement(stopID).componentName === 'LayerContainer'
    ) {
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

    if(elStart.componentName === 'LayerContainer'
      || elStop.componentName === 'LayerContainer'
    ) {
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
  DELETE_copyProperty(state, id) {
    state.workspaceContent[state.currentNetwork].networkElementList[id].copyId = null;
    state.workspaceContent[state.currentNetwork].networkElementList[id].copyContainerElement = null;
  },

  /*-- NETWORK ELEMENTS SETTINGS --*/
  set_elementSettings(state, {dispatch, settings}) {
    //console.log('set_elementSettings', settings);
    currentElement(settings.elId).layerSettings = settings.set;
    currentElement(settings.elId).layerCode = settings.code;
    currentElement(settings.elId).layerSettingsTabName = settings.tabName;
    dispatch('mod_workspace-history/PUSH_newSnapshot', null, {root: true});
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
  set_elementInputDim(state, value) {
    for(let element in value) {
      currentElement(element).layerMeta.InputDim = value[element].inShape;
      currentElement(element).layerCodeError = value[element].Error
    }
  },
  set_elementOutputDim(state, {value}) {
    for(let element in value) {
      currentElement(element).layerMeta.OutputDim = value[element].Dim;
      currentElement(element).layerCodeError = value[element].Error
    }
  },
  SET_webLoadingDataFlag(state, value) {
    state.webLoadingDataFlag = value
  },

  //---------------
  //  NETWORK CONTAINER
  //---------------
  add_container(state, {getters, commit, dispatch}) {
    let arrSelect = getters.GET_currentSelectedEl;
    let isValid = true;
    let elementList = getters.GET_currentNetworkElementList;
    let containersArray = [];
    let parentContainerID = arrSelect.length ? arrSelect[0].parentContainerID : null;
    /* validations */
    if(arrSelect.length === 0) isValid = false;
    if(arrSelect.length === 1) {
      dispatch('globalView/GP_infoPopup', 'At least 2 elements are needed to create a group', {root: true});
      isValid = false;
    }
    if(!isValid) {
      dispatch('SET_elementUnselect');
      return;
    }
    /* END validations */
    let newContainer = createClearContainer(arrSelect);

    updateLayerName(newContainer, elementList, 1);
    if(parentContainerID) {
      Vue.set(state.workspaceContent[state.currentNetwork].networkElementList[parentContainerID].containerLayersList, newContainer.layerId, newContainer);
      Vue.set(state.workspaceContent[state.currentNetwork].networkElementList, newContainer.layerId, newContainer);
    }
    else {
      Vue.set(state.workspaceContent[state.currentNetwork].networkElementList, newContainer.layerId, newContainer);
    }
    commit('close_container', {container: newContainer,  getters, dispatch});
    commit('set_elementUnselect', {getters});

    function createClearContainer(selectList) {
      arrSelect.forEach(element => {
        if(selectList[0].parentContainerID) {
          const parentContainerLayerList = state.workspaceContent[state.currentNetwork].networkElementList[selectList[0].parentContainerID].containerLayersList;
          for(const id in parentContainerLayerList) {
            delete parentContainerLayerList[element.layerId]
          }
        }
      });
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
      container.isShow = true;
      if(selectList[0].parentContainerID) {
        const last = selectList.length - 1;
        if(selectList[last].componentName === 'LayerContainer') selectList.splice(last, 1);
        container.parentContainerID = selectList[0].parentContainerID;
      }
      selectList.forEach((el)=>{
        el.parentContainerID = container.layerId;
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

    closeChildContainer(layerCont);

    dispatch('mod_events/EVENT_calcArray', null, {root: true});


    function closeChildContainer(container) {
      const layerListKeys = Object.keys(container.containerLayersList);
      layerListKeys.forEach(id => {
        const element = container.containerLayersList[id];
        if (element.componentName === 'LayerContainer') {
          element.isShow = false;
          for(let idEl in element.containerLayersList) {
            const childElement = element.containerLayersList[idEl];
            childElement.layerNone = true;
            if(childElement.componentName === 'LayerContainer') {
              childElement.isShow = false;
            }
          }
          closeChildContainer(element)
        }
      });
    }

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

    showChildContainer(container);

    dispatch('mod_events/EVENT_calcArray', null, {root: true});

    function showChildContainer(container) {
      const layerListKeys = Object.keys(container.containerLayersList);
      layerListKeys.forEach(id => {
        const element = container.containerLayersList[id];
        if (element.componentName === 'LayerContainer') {
          element.isShow = true;
        }
      });
    }

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
      delete el.layerContainerID;
    }
    delete net[container.layerId];
    state.workspaceContent[state.currentNetwork].networkElementList = net;
  },
  //---------------
  //  OTHER
  //---------------
  set_currentNetwork(state, tabIndex) {
    state.currentNetwork = tabIndex;
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
  set_isOpenElement (state, value) {
    state.isOpenElement = value
  },
  set_historyStep (state, {value, dispatch}) {
    state.workspaceContent[state.currentNetwork].networkName = value.networkName;
    state.workspaceContent[state.currentNetwork].networkElementList = value.networkElementList;
  },
};

const actions = {
  //---------------
  //  NETWORK
  //---------------
  ADD_network({commit, dispatch}, network) {
    if(isElectron()) {
      commit('add_network', network);
    } else {
      commit('add_network', network);
      const lastNetworkID = state.workspaceContent[state.currentNetwork].networkID;
      commit('set_lastActiveTabInLocalStorage', lastNetworkID);
      commit('set_workspacesInLocalStorage'); 
    }
  },
  DELETE_network({commit, dispatch}, index) {
    if(isElectron()) {
      const networkID = state.workspaceContent[index].networkID;
      commit('delete_network', index);
      dispatch('mod_api/API_closeSession', networkID, { root: true });
    } else {
      // API_closeSession stops the process in the core
      const network = state.workspaceContent[index];
      dispatch('mod_api/API_closeSession', network.networkID, { root: true });
  
      if (index === state.currentNetwork) {
  
        if (state.workspaceContent.length === 1) {
          commit('set_lastActiveTabInLocalStorage', '');
        } else if (index === 0) {
          commit('set_lastActiveTabInLocalStorage', state.workspaceContent[index + 1].networkID);
        } else {
          commit('set_lastActiveTabInLocalStorage', state.workspaceContent[index - 1].networkID);
        }
      }
  
      commit('delete_network', index);
      commit('set_workspacesInLocalStorage');
    }
  },
  GET_workspacesFromLocalStorage({commit, dispatch}) {
    return new Promise(resolve => {
      if (!isLocalStorageAvailable()) { resolve(); }

      commit('get_workspacesFromLocalStorage');
      commit('get_lastActiveTabFromLocalStorage');

      processNonActiveWorkspaces();
      processActiveWorkspaces();

      function processNonActiveWorkspaces() {
        // removing stats and test tabs if there aren't any trained models
        // this happens when the core is restarted
        const networks = state.workspaceContent.filter(network =>
          network.networkElementList !== null &&
          network.networkID !== state.workspaceContent[state.currentNetwork].networkID);

        for(let network of networks) {
          const isRunningPromise = dispatch('mod_api/API_checkNetworkRunning', network.networkID, { root: true });
          const isTrainedPromise = dispatch('mod_api/API_checkTrainedNetwork', network.networkID, { root: true });
          Promise.all([isRunningPromise, isTrainedPromise])
            .then(([isRunning, isTrained]) => {
              // console.log('Promise all values', isRunning, isTrained);
              if (isRunning && isTrained) {
                network.networkMeta.openStatistics = false;
                network.networkMeta.openTest = null;
              } else if (!isRunning && isTrained) {
                network.networkMeta.openStatistics = false;
                network.networkMeta.openTest = false;
              } else {
                network.networkMeta.openStatistics = null;
                network.networkMeta.openTest = null;
              }
            });
        }
      }

      function processActiveWorkspaces() {
        const network = state.workspaceContent.find(network =>
          network.networkID === state.workspaceContent[state.currentNetwork].networkID);

          const isRunningPromise = dispatch('mod_api/API_checkNetworkRunning', network.networkID, { root: true });
          const isTrainedPromise = dispatch('mod_api/API_checkTrainedNetwork', network.networkID, { root: true });
          Promise.all([isRunningPromise, isTrainedPromise])
            .then(([isRunning, isTrained]) => {

            if (isRunning && !isTrained) {
              // when the spinner is loading
              commit('SET_showStartTrainingSpinner', true);
              dispatch('SET_openStatistics', network.networkMeta.openStatistics);
              dispatch('SET_openTest', null);
              dispatch('SET_chartsRequestsIfNeeded', network.networkID);
            } else if (isRunning && isTrained) {
              // after spinner is done loading, and the first charts are shown
              dispatch('SET_openStatistics', network.networkMeta.openStatistics);
              dispatch('SET_openTest', null);
              dispatch('SET_chartsRequestsIfNeeded', network.networkID);
            } else if (!isRunning && isTrained) {
              // after training is done
              dispatch('SET_openStatistics', network.networkMeta.openStatistics);
              dispatch('SET_openTest', network.networkMeta.openTest);
              dispatch('SET_chartsRequestsIfNeeded', network.networkID);
            } else {
              dispatch('SET_openStatistics', null);
              dispatch('SET_openTest', null);
            }
        });
      }

      resolve();
    });
  },
  SET_chartsRequestsIfNeeded({state, dispatch}, networkID) {
    // This function is used to determine if the page has been refreshed after the training
    // has started, but before it is completed.

    const network = state.workspaceContent.find(network => network.networkID === networkID);

    // console.group('SET_chartsRequestsIfNeeded');
    // console.log('stats tab', network.networkMeta.openStatistics);
    // console.log('test tab', network.networkMeta.openTest);
    // console.log('networkWaitGlobalEvent', network.networkMeta.chartsRequest.waitGlobalEvent);
    // console.groupEnd();

    // skip if:
    // network never trained before
    // if there's already a valid timerID
    if (!network ||
      network.networkMeta.openStatistics == null ||
      network.networkMeta.chartsRequest.timerID) { return; }

    // this check is only for the statistics tab
    dispatch('mod_api/API_checkNetworkRunning', networkID, {root: true})
      .then((isRunning) => {

      if (network.networkMeta.coreStatus.Status === 'Paused') {
        //statistics still being computed and paused
        dispatch('EVENT_onceDoRequest', true);
      } else if (isRunning) {
        //statistics still being computed and NOT paused
        dispatch('EVENT_startDoRequest', true);
      } else if (network.networkMeta.coreStatus.Status === 'Finished' &&
        network.networkMeta.coreStatus.Progress < 1 &&
        network.networkMeta.chartsRequest.waitGlobalEvent) {
        // statistics done, tests have started
        dispatch('EVENT_startDoRequest', true);
      } else if (network.networkMeta.coreStatus.Status === 'Finished' &&
        network.networkMeta.coreStatus.Progress >= 1) {
        // statistics done, tests done
        dispatch('mod_api/API_postTestMove', 'nextStep', {root: true});
      } else {
        dispatch('EVENT_onceDoRequest', true);
      }
    });
  },
  SET_currentNetwork({commit}, index){
    commit('set_currentNetwork', index);
    commit('set_lastActiveTabInLocalStorage', state.workspaceContent[index].networkID);
  },
  SET_networkName({commit, getters}, value) {
    commit('set_networkName', {getters, value})
  },
  SET_networkRootFolder({commit, getters}, value) {
    commit('set_networkRootFolder', {getters, value})
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
    const timeRequest = time + 500;
    const isLongRequest = timeRequest > rootState.globalView.timeIntervalDoRequest;
    if(isLongRequest) {
      const currentMeta = getters.GET_currentNetwork.networkMeta.chartsRequest;
      clearInterval(currentMeta.timerID);
      dispatch('globalView/SET_timeIntervalDoRequest', timeRequest, {root: true});
      dispatch('EVENT_startDoRequest', true);
    }
  },
  EVENT_startDoRequest({dispatch, commit, rootState, getters, state}, isStart) {
    const currentMeta = getters.GET_currentNetwork.networkMeta;
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
      clearInterval(currentMeta.chartsRequest.timerID);
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
  SET_elementSettings({commit, dispatch}, settings) {
    commit('set_elementSettings', {dispatch, settings})
  },
  ADD_element({commit, getters, dispatch}, event) {
    commit('add_element', {getters, dispatch, event})
  },
  DELETE_element({commit, getters, dispatch}) {
    if(getters.GET_networkIsOpen) {
      commit('delete_element', {getters, dispatch, commit});
      dispatch('mod_api/API_getOutputDim', null, {root: true});
    }
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
    if(getters.GET_enableHotKeyElement) commit('set_elementSelectAll', {getters})
  },
  SET_elementMultiSelect({commit}, value) {
    commit('set_elementMultiSelect', value)
  },
  SET_elementInputDim({commit}, value) {
    commit('set_elementInputDim', value)
  },
  SET_elementOutputDim({commit, getters}, value) {
    commit('set_elementOutputDim', {getters, value})
  },
  CHANGE_elementPosition({commit}, value) {
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
  //---------------
  //  OTHER
  //---------------
  SET_isOpenElement({commit}, value) {
    commit('set_isOpenElement', value)
  },
  SET_historyStep({commit, dispatch}, value) {
    commit('set_historyStep', {value, dispatch});
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
    copyId: event.target.dataset.copyId || null,
    copyContainerElement: event.target.dataset.copyContainerElement || null,
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
  };
};
