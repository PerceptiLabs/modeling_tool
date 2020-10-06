const DB_NAME = 'perceptilabs-idb';
const DB_VERSION = 1;
let _DB;

const _getDb = async () => {
  return new Promise((resolve, reject) => {

    if(_DB) { return resolve(_DB); }
    
    let request = window.indexedDB.open(DB_NAME, DB_VERSION);
    
    request.onerror = e => {
      reject(e);
    };

    request.onsuccess = e => {
      _DB = e.target.result;
      resolve(_DB);
    };
    
    request.onupgradeneeded = e => {
      let db = e.target.result;
      db.createObjectStore('models');
      db.createObjectStore('ids');    
    };
  });
}

export default {
  /**
   * Fetches the current ids in for the project.
   * @return {void}
   */
  async getIds() {

    let db = await _getDb();

    return new Promise(resolve => {

      let trans = db.transaction(['ids'],'readonly');
      trans.oncomplete = () => {
        resolve(ids);
      };
      
      let store = trans.objectStore('ids');
      let ids = [];
      
      store.openCursor().onsuccess = e => {
        let cursor = e.target.result;
        if (cursor) {
          ids.push(cursor.value)
          cursor.continue();
        }
      };

    });
  },
  
  /**
   * Clears then set the networksIDs. 
   * @param {Array.<number>} ids
   * @return {void}
  */
  async setIds(ids) {

    let db = await _getDb();

    return new Promise(resolve => {

      let trans = db.transaction(['ids'],'readwrite');
      trans.oncomplete = () => {
        resolve();
      };

      let store = trans.objectStore('ids');
      
      store.clear();
      for (const id of ids) {
        store.put(id, id);
      }
    });
  },


  async deleteId(id) {

    let db = await _getDb();

    return new Promise(resolve => {

      let trans = db.transaction(['ids'],'readwrite');
      trans.oncomplete = () => {
        resolve();
      };

      let store = trans.objectStore('ids');
      store.delete(id);
    }); 
  }, 


  async deleteAllIds() {

    let db = await _getDb();

    return new Promise(resolve => {

      let trans = db.transaction(['ids'],'readwrite');
      trans.oncomplete = () => {
        resolve();
      };

      let store = trans.objectStore('ids');
      store.clear();
    });
  
  },

  async getModel(modelId) {

    let db = await _getDb();

    return new Promise(resolve => {

      let trans = db.transaction(['models'],'readonly');
      
      let store = trans.objectStore('models');
      
      let request = store.get(modelId.toString());

      request.onsuccess = e => {
        resolve(request.result);
      };
    });
  },

  async getModels(ids = []) {

    let db = await _getDb();

    return new Promise(resolve => {

      let trans = db.transaction(['models'],'readonly');
      trans.oncomplete = () => {
        resolve(models);
      };
      
      let store = trans.objectStore('models');
      let models = [];
      
      store.openCursor().onsuccess = e => {
        let cursor = e.target.result;
        if (!cursor) { return; }

        if (ids.includes(cursor.value.networkID)) {
          models.push(cursor.value)
        }
        
        cursor.continue();
      };

    });
  },

  async saveModel(model) {

    let db = await _getDb();

    return new Promise(resolve => {

      let trans = db.transaction(['models'],'readwrite');
      trans.oncomplete = () => {
        resolve();
      };

      let store = trans.objectStore('models');
      store.put(model, model.networkID.toString());

    });
  
  },

  async deleteModel(networkId) {

    let db = await _getDb();

    return new Promise(resolve => {

      let trans = db.transaction(['models'],'readwrite');
      trans.oncomplete = () => {
        resolve();
      };

      let store = trans.objectStore('models');
      store.delete(networkId);
    }); 
  }, 

  async deleteAllModels() {

    let db = await _getDb();

    return new Promise(resolve => {

      let trans = db.transaction(['models'],'readwrite');
      trans.oncomplete = () => {
        resolve();
      };

      let store = trans.objectStore('models');
      store.clear();
    }); 
  }, 

}
