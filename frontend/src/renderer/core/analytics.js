const addHubSpotAnalytics = function() {

    const hubSpotId = process.env.HUBSPOT_ID;
    if (!hubSpotId) { return; }
    
    let hubSpotElement = document.createElement('script');
    hubSpotElement.type = 'text/javascript';
    hubSpotElement.id = 'hs-script-loader';
    hubSpotElement.async = true;
    hubSpotElement.defer = true;
    hubSpotElement.src = `//js.hs-scripts.com/${hubSpotId}`;
    document.head.appendChild(hubSpotElement);
}

const addGoogleAnalytics = function() {

    const gaId = process.env.GOOGLE_ANALYTICS_ID;
    if (!gaId) { return; }

    if (!window['gtag']) {
      window.dataLayer = window.dataLayer || [];
      window['gtag'] = function () { window.dataLayer.push(arguments); }
    }

    window['gtag']('js', new Date());
    window['gtag']('config', gaId);
    
    let gaElement = document.createElement('script');
    gaElement.async = true;
    gaElement.src = `https://www.googletagmanager.com/gtag/js?id=${gaId}`;
    document.head.appendChild(gaElement);
}

const googleAnalytics = (function() {

    let publicMethods = {};

    const addTag = function () {
        window.dataLayer = window.dataLayer || [];
        window.dataLayer.push(arguments);
    }

    publicMethods.setup = function() {
        const gaId = process.env.GOOGLE_ANALYTICS_ID;
        if (!gaId) { return; }
        
        addTag('js', new Date());
        addTag('config', gaId);

        let gaElement = document.createElement('script');
        gaElement.async = true;
        gaElement.src = `https://www.googletagmanager.com/gtag/js?id=${gaId}`;
        document.head.appendChild(gaElement);
    }

    publicMethods.trackRouteChange = function(to) {

        // console.log('trackRouteChange', to);

        if (!to) { return; }

        const argPayload = {
            page_title: to.name,
            page_path: to.path,
            page_location: window.location.host + to.path
        };
        addTag('event', 'page_view', argPayload);
    }

    publicMethods.trackUserId = function(userId) {
        if (!userId || userId === 'Guest') { return; }

        console.log(window.dataLayer);

        addTag('set', {'user_id' : userId});
    }

    return publicMethods;
})();

export default {
    addHubSpotAnalytics,
    addGoogleAnalytics,
    googleAnalytics,
}