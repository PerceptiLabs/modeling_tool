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

export {
    addHubSpotAnalytics,
    addGoogleAnalytics
}