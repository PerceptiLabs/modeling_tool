<template lang="pug">
    iframe#notebook(
        ref='notebook-iframe'
        @load="onIFrameLoad"
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
        onIFrameLoad(){

            // this.updateNotebook();

            // let iframe = this.$refs['notebook-iframe'];
            // console.log('iframe loaded', iframe);
            // let innerDoc = iframe.contentDocument.document;
            // console.log('iframe.contentDocument', innerDoc);
            // let app = innerDoc.querySelector('.notebook_app');
            // console.log('iframe.contentWindow', iframe.contentWindow);
            // console.log('innerDoc.querySelector', app);
            // console.groupEnd();
        },
        updateNotebook(){

            // console.log('this.fetchNotebookJson()', this.fetchNotebookJson());
            // console.log('this.fetchNetworkCode()', this.fetchNetworkCode());

            Promise.all([
                    this.fetchNotebookJson(),
                    this.fetchNetworkCode(),
                    this.fetchNetworkCodeOrder()
                ])
                .then(([notebookJson, networkCodes, networkCodeOrder]) => {

                    // console.log('notebookJson', notebookJson);
                    // console.log('networkCode', networkCodes);
                    // console.log('networkCodeOrder', networkCodeOrder);

                    // const validNetworkCodes = networkCodes.filter(nc => nc);
                    // const newNotebookJson = this.createNotebookDataToInject(notebookJson, validNetworkCodes);
                    // this.injectNotebookJson(newNotebookJson);
                    // this.fetchNotebookUrl();
                });
        },
        fetchNotebookJson(){

            // http://192.168.180.133:8000/user/test/api/contents/Documents/Untitled.ipynb
            // const url = this.jupyterHubBaseUrl + '/user/test/api/contents/Documents/Untitled.ipynb';
            // console.log('fetchNotebookJson');

            const url = this.jupyterNotebookManager + '/notebook';
            return fetch(url)
                .then(response => response.json())
                .then(notebookJson => {
                    return notebookJson;
                })
                .catch(error => console.error('fetchNotebookJson - error', error));
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
        injectNotebookJson(notebookJson){
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
                // networkElement[0] is just the layerId
                const networkInformation = networkElement[1];
                const payload = {
                    layerId: networkInformation.layerId,
                    settings: networkInformation.layerSettings,
                };

                const promise = this.$store.dispatch('mod_api/API_getCode', payload);

                fetchCodePromises.push(promiseWithTimeout(200, promise));
            }

            return Promise.all(fetchCodePromises)
                .then(code => {

                    console.log('code', code);
                    return code.filter(c => c).map(c => c.Output);
                });
        },
        fetchNetworkCodeOrder() {
            return this.$store.dispatch('mod_api/API_getGraphOrder', this.coreNetwork)
                .then(codeOrder => {
                    return codeOrder;
                });
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
                console.log('New currentNetwork', newValue);
                this.updateNotebook();

            }
        }
    },
    mounted(){
        // const a = this.fetchNetworkCode();
        // a.then(val => console.log('------------', val));

        // console.log('json network ', this.currentNetwork.networkElementList);
        // console.log('coreNetwork', this.coreNetwork);

        // console.log('notebook mounted');

    }
}
</script>


<style lang="scss" scoped>
#notebook {
    background-color: #22242a;
}
</style>