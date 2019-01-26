<template lang="pug">
      main.page
        div.page__sidebar
          ul.switcher.d-flex
            li
              input(type="radio" id="computer" value="computer" v-model="source")
              label(for="computer") Computer
            li
              input(type="radio" id="cloud" value="cloud" v-model="source")
              label(for="cloud") Cloud
          h3 Import as:
          ul.icons-group-button.d-flex
            li 
              input(type="radio" id="cloud-service" value="cloud-service" v-model="service")
              label(for="cloud-service")
                i.icon.icon-cloud
            li
              input(type="radio" id="dropbox-service" value="dropbox-service" v-model="service")
              label(for="dropbox-service") 
                i.icon.icon-dropbox-logo
            li
              input(type="radio" id="g-drive-service" value="g-drive-service" v-model="service")
              label(for="g-drive-service")
                i.icon.icon-g-drive
            li
              input(type="radio" id="onedrive-service" value="onedrive-service" v-model="service")
              label(for="onedrive-service") 
                i.icon.icon-onedrive
            li
              input(type="radio" id="cloud-add-service" value="cloud-add-service" v-model="service")
              label(for="cloud-add-service") 
                i.icon.icon-cloud-add

          ul.account-info
              li.d-flex
                span
                  i.icon.icon-dropbox-logo 
                  label Account: Quantum.net
                span.logout Logout
              li.d-flex.disabled
                span
                  i.icon.icon-dropbox-logo 
                  label Account: Quantum.net
                span.logout Logout
              li
                a(href="#")
                  i.icon.icon-dropbox-logo 
                  label Add account
                
              

        div.page__workspace
            router-link.btn.btn--link(:to="{name: 'login'}") back

</template>
<script>
export default {
     name: 'Projects',
    data() {
        return {
            source: '',
            service: ''
        }
    }
}
</script>
<style lang="scss" scoped>
    @import '../../scss/base';
    .page{
        grid-template-columns: 1fr 4fr;
        grid-template-rows: inherit;
        grid-template-areas: 
            "sidebar workspace";
        &__sidebar{
            grid-area: sidebar;
            padding: 40px 10px 0 10px;
            h3{
                margin: 20px 0;
            }
        }
        &__workspace{
            grid-area: workspace;
            background: $bg-workspace;
        }
    }
    .switcher{
        border: 1px solid $color-5;
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 4px 4px rgba(0, 0, 0, 0.25);

        li{
            flex: 1 1 0;
            text-align: center;
            overflow: hidden;
        
            label{
                display: block;
                width: 100%;
                padding: 8px 2px;
                font-size: 14px;
            }

            input[type="radio"]:checked, 
            input[type="radio"]:not(:checked) {
                position: absolute;
                left: -9999px;
            }
            input[type="radio"] + label {
                color: #868697;
            }
            input[type="radio"]:checked + label {
                background: $bg-grad-blue;
                color: #dadce2;
            }
        }
    }
    .icons-group-button{
        justify-content: space-between;
        margin-bottom: 20px;

        li{
            width: 45px;
            height: 45px;
            
            label{
                display: block;
                width: 100%;
                height: 100%;
                background: #495163;
                display: flex;
                justify-content: center;
                align-items: center;
                font-size: 22px;
                color: #5c6680;
                border-radius: 5px;
                border: 2px solid #5c6680;
                box-sizing: border-box;
            }

            input[type="radio"]:checked, 
            input[type="radio"]:not(:checked) {
                position: absolute;
                left: -9999px;
            }
            input[type="radio"] + label {
                color: #868697;
            }
            input[type="radio"]:checked + label {
                background: $bg-grad-blue;
                color: #dadce2;
                box-shadow: 0 4px 4px rgba(0, 0, 0, 0.25);
                border: none;
            }
        }
    }
    .account-info{
        border-top: 1px solid #4d556a;
        border-bottom: 1px solid #4d556a;
        padding: 10px 0;
        li {
            justify-content: space-between;
            margin-bottom: 10px;
            margin-left: 10px;
            .icon{
                margin-right: 5px;
            }
            &.disabled {
                color: #6b6e7f;
            }
            &:last-child {
                margin-bottom: 0
            }
            a{
                color: #e2b96b;
                label {
                    text-decoration: underline;
                }
            }
        }
        
    }


</style>


