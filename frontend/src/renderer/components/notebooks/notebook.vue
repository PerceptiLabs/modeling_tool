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
            this.fetchNotebookJson()
            .then(notebookJson => {
                const newNotebookJson = this.createNotebookDataToInject(notebookJson, this.networkCode);
                this.injectNotebookJson(newNotebookJson);
                this.fetchNotebookUrl();
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
                    source: codeSnippet.Output,
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
            if (!this.currentNetwork || !this.currentNetwork.networkElementList) {
                return [];
            }

            for(let networkElement of Object.entries(this.currentNetwork.networkElementList)) {
                // networkElement[0] is just the layerId
                const networkInformation = networkElement[1];
                const payload = {
                    layerId: networkInformation.layerId,
                    settings: networkInformation.layerSettings,
                };

                this.$store.dispatch('mod_api/API_getCode', payload)
                    .then(code => {
                        // console.log('get code answer', networkElement.layerId, code);
                        this.networkCode.push(code);
                    })
                    .catch(error => {
                        console.log('error', error);
                    });
            }
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
            currentNetwork: 'mod_workspace/GET_currentNetwork'
        })
        // currentNetwork() {
        //     console.log('currentNetwork', this.$store.getters['mod_workspace/GET_currentNetwork']);
        //     return this.$store.getters['mod_workspace/GET_currentNetwork'];
        // },
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
        // this.fetchNetworkCode();

        // console.log('notebook mounted');
        // this.$store.dispatch('mod_api/API_getGraphOrder', {layerId: this.currentNetwork.networkID})
        // .then(response => {
        //     console.log('API_getGraphOrder', response);
        // });
    }
}
</script>


<style lang="scss" scoped>
#notebook {
    background-color: #22242a;
}
</style>