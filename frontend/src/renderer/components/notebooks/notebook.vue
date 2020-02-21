<template lang="pug">
    iframe#notebook(
        ref='notebook-iframe'
        @load="onIFrameLoad"
        :src="iframeSource",
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
            notebookUrl: '',
            jupyterNotebookManager: 'http://localhost:9000',
            networkCode: []
        };
    },
    methods: {
        onIFrameLoad(){

            this.fetchNotebookJson()
            .then(notebookJson => {

                
                // console.log('onIframeLoad - b', notebookJson);
                notebookJson.content.cells = [];

                for (let codeSnippet of this.networkCode) {
                    let notebookCellJson = {
                        cell_type: 'code',
                        execution_count: null,
                        metadata: {trusted: true},
                        outputs: [],
                        source: codeSnippet.Output,
                    }

                    notebookJson.content.cells.push(notebookCellJson);
                }

                // console.log('onIframeLoad - a', notebookJson);
                this.injectNotebookJson(notebookJson);
            });
            
            // let iframe = this.$refs['notebook-iframe'];
            // console.log('iframe loaded', iframe);
            // let innerDoc = iframe.contentDocument.document;
            // console.log('iframe.contentDocument', innerDoc);
            // let app = innerDoc.querySelector('.notebook_app');
            // console.log('iframe.contentWindow', iframe.contentWindow);
            // console.log('innerDoc.querySelector', app);
            // console.groupEnd();
        },
        fetchNotebookJson(){

            // http://192.168.180.133:8000/user/test/api/contents/Documents/Untitled.ipynb
            // const url = this.jupyterHubBaseUrl + '/user/test/api/contents/Documents/Untitled.ipynb';
            console.log('fetchNotebookJson');

            const url = this.jupyterNotebookManager + '/notebook';
            return fetch(url)
            .then(response => response.json())
            .then(notebookJson => {
                return notebookJson;
            });
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
            .then(notebookResponse => console.log('injectNotebookJson', notebookResponse));
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
        }
    },
    computed: {
        currentNetwork() {
            console.log('currentNetwork', this.$store.getters['mod_workspace/GET_currentNetwork']);
            return this.$store.getters['mod_workspace/GET_currentNetwork'];
        },
        iframeSource() {
            return this.jupyterHubBaseUrl + '/user/test/notebooks/Documents/Untitled.ipynb';
        },
    },
    mounted(){
        this.fetchNetworkCode();

        this.$store.dispatch('mod_api/API_getGraphOrder', {layerId: this.currentNetwork.networkID})
        .then(response => {
            console.log('API_getGraphOrder', response);
        });

    }
}
</script>


<style lang="scss" scoped>
#notebook {
    background-color: #22242a;
}
</style>