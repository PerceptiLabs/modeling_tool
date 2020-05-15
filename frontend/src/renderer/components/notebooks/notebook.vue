<template lang="pug">
    iframe#notebook(
        ref='notebook-iframe'
        :src="notebookUrl",
        width='100%',
        height='100%',
        frameBorder="0")
</template>

<script>

// import Vue from 'vue';
import { mapGetters } from 'vuex';
import { stringifyNetworkObjects, promiseWithTimeout } from '@/core/helpers';

export default {
    name: 'Notebook',
    data() {
        return {
            notebookUrl: 'http://192.168.180.136:8000/user/test/notebooks/Documents/Untitled.ipynb?token=f8c7dac1af8643ffb68f1d7e2869cf7a',
            jupyterNotebookManager: 'http://localhost:9000',
            networkCode: []
        };
    },
    methods: {
        updateNotebook(){

            Promise.all([
                    this.fetchNotebookJson(),
                    this.fetchNetworkCode(),
                    this.fetchNetworkCodeOrder()
                ])
                .then(([notebookJson, networkCodes, networkCodeOrder]) => {

                    // console.log('notebookJson', notebookJson);
                    // console.log('networkCode', networkCodes);
                    // console.log('networkCodeOrder', networkCodeOrder);


                    const validNetworkCodes = networkCodes.filter(nc => nc);
                    const sortedCode = this.sortNetworkCode(validNetworkCodes, networkCodeOrder);
                    const newNotebookJson = this.createNotebookDataToInject(notebookJson, sortedCode);
                    this.injectNotebookJson(newNotebookJson);
                    this.fetchNotebookUrl();
                });
        },
        fetchNotebookJson(){
            const url = this.jupyterNotebookManager + '/notebook';
            return fetch(url)
                .then(response => response.json())
                .then(notebookJson => {
                    return notebookJson;
                })
                .catch(error => console.error('fetchNotebookJson - error', error));
        },
        sortNetworkCode(array, sortOrder = null) {
            if (!array || !sortOrder) { return; }

            // current sort is O(n^2), will use Map if most networks have many elements

            const sortedArray = [];
            for (let sortKey of sortOrder) {

                let targetCode = array.find(element => element.layerId === sortKey);
                if (targetCode) {
                    sortedArray.push(targetCode.Output);
                }
            }
            return sortedArray;
        },
        createNotebookDataToInject(notebookJson, networkCode) {
            const newNotebookJson = JSON.parse(JSON.stringify(notebookJson));
            newNotebookJson.content.cells = [];

            for (let codeSnippet of networkCode) {
                let notebookCellJson = {
                    cell_type: 'code',
                    execution_count: null,
                    metadata: {trusted: true},
                    outputs: [],
                    source: codeSnippet,
                }

                newNotebookJson.content.cells.push(notebookCellJson);
            }
            return newNotebookJson;
        },
        injectNotebookJson(notebookJson) {
            // console.log('injectNotebookJson', notebookJson);
            if (!notebookJson) { return; }

            // const url = this.jupyterHubBaseUrl + '/user/test/api/contents/Documents/Untitled.ipynb';

            const url = this.jupyterNotebookManager + '/notebook';
            fetch(url, {
                method: 'PUT',
                body: JSON.stringify(notebookJson),
                headers: new Headers({
                    'Content-Type': 'application/json',
                })
            })
            .then(response => response.json())
            .then(notebookResponse => {
                // console.log('injectNotebookJson', notebookResponse);
                // this.fetchNotebookUrl
            })
            .catch(error => console.error('injectNotebookJson - error', error));

        },
        fetchNetworkCode() {
            if (!this.currentNetwork || !this.currentNetwork.networkElementList) { return []; }

            const fetchCodePromises = [];

            for(let networkElement of Object.entries(this.currentNetwork.networkElementList)) {

                const promise = addIdToLayerCode.call(this, networkElement);
                fetchCodePromises.push(promiseWithTimeout(200, promise));
            }

            return Promise.all(fetchCodePromises)
                .then(code => {
                    return code.filter(c => c).map(c => c);
                });

            function addIdToLayerCode(networkElement) {
                // wrote this litte function because we want a layerId key with the code
                // this is to help with the sorting in the next step

                // networkElement[0] is just the layerId
                const networkInformation = networkElement[1];
                const payload = {
                    layerId: networkInformation.layerId,
                    settings: networkInformation.layerSettings,
                };

                return this.$store.dispatch('mod_api/API_getCode', payload)
                    .then(result => {
                        result.layerId = networkInformation.layerId;
                        return result;
                    })
            }
        },
        fetchNetworkCodeOrder() {
            return this.$store.dispatch('mod_api/API_getGraphOrder', this.coreNetwork)
                .then(codeOrder => codeOrder)
                .catch(error => []);
        },
        fetchNotebookUrl() {

            this.notebookUrl = '';

            const url = this.jupyterNotebookManager + '/notebookurl';
            fetch(url)
                .then(response => response.text())
                .then(url => this.notebookUrl = url)
                .catch(error => console.error('notebookurl - error', error));
        }
    },
    computed: {
        ...mapGetters({
            currentNetwork: 'mod_workspace/GET_currentNetwork',
            coreNetwork: 'mod_api/GET_coreNetwork'

        })
    },
    watch: {
        currentNetwork: {
            immediate: true,
            handler(newValue) {
                this.updateNotebook();
            }
        }
    },

}
</script>


<style lang="scss" scoped>
#notebook {
    background-color: #22242a;
}
</style>