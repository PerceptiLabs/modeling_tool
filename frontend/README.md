# PerceptiLabs

> PerceptiLabs is a cross-platform software that will make it easier to use Machine Learning, especially Deep Learning.

#### Build Setup

``` bash
# install dependencies
npm install

# serve with hot reload at localhost:9080
npm run dev

# build electron application for production
windows
    npm run build
linux
    npm run build
mac
    xattr -cr .
    sudo npm run build
    node notarize.js

# lint all JS/Vue component files in `src/`
npm run lint

# clone project
git clone --depth=1 https://PerceptiLabs@dev.azure.com/PerceptiLabs/PerceptiLabs/_git/PerceptiLabs
git remote set-branches origin '*'
git fetch -v
git checkout BRACH //dev, stage, master, web-dev, web-master

```

---

This project was generated with [electron-vue](https://github.com/SimulatedGREG/electron-vue)@[16fb2b9](https://github.com/SimulatedGREG/electron-vue/tree/16fb2b963f17318cd9ff17d2adfd1945bd7107a0) using [vue-cli](https://github.com/vuejs/vue-cli). Documentation about the original structure can be found [here](https://simulatedgreg.gitbooks.io/electron-vue/content/index.html).
