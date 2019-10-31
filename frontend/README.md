# PerceptiLabs

> PerceptiLabs is a cross-platform software that will make it easier to use Machine Learning, especially Deep Learning.

#### Build Setup

``` bash
# install dependencies
npm install

# serve with hot reload at localhost:9080
npm run dev

mac
    sudo chmod -R 777 core // all access 'core' folder 
    sudo spctl --master-disable //disable checking sign
    sudo npm run dev

# build electron application for production
windows
    npm run build
linux
    start core
        chmod +x appServer
        ./appServer

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

