import { isDevelopMode } from '@/core/constants';

const hubSpot = (function() {
    let publicMethods = {};

    const addTag = function(input) {
        if (!input) { return; }

        window._hsq = window._hsq || [];
        window._hsq.push(input);
    }

    publicMethods.setup = function() {
        const hubSpotId = process.env.HUBSPOT_ID;
        if (!hubSpotId || isDevelopMode) { return; }
        
        let hubSpotElement = document.createElement('script');
        hubSpotElement.type = 'text/javascript';
        hubSpotElement.id = 'hs-script-loader';
        hubSpotElement.async = true;
        hubSpotElement.defer = true;
        hubSpotElement.src = `//js.hs-scripts.com/${hubSpotId}`;
        document.head.appendChild(hubSpotElement);
    }

    publicMethods.trackRouteChange = function(to) { 
        if (!to) { return; }
      
        if (to.path === '/') {
          addTag(['setPath', '/']);
        } else {
          addTag(['setPath', to.path]);
          addTag(['trackPageView']);
        }
    }

    publicMethods.trackRunButtonPress = function(userEmail) {
        addTag(['trackEvent"', {
            id: "Run button clicked",
            value: userEmail
        }]);
    }

    return publicMethods;
})();

const googleAnalytics = (function() {

    let publicMethods = {};

    const addTag = function() {
        window.dataLayer = window.dataLayer || [];
        window.dataLayer.push(arguments);
    }

    publicMethods.setup = function() {
        const gaId = process.env.GOOGLE_ANALYTICS_ID;
        if (!gaId || isDevelopMode) { return; }
        
        addTag('js', new Date());
        addTag('config', gaId);

        let gaElement = document.createElement('script');
        gaElement.async = true;
        gaElement.src = `https://www.googletagmanager.com/gtag/js?id=${gaId}`;
        document.head.appendChild(gaElement);
    }

    publicMethods.trackRouteChange = function(to) {
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
    hubSpot,
    googleAnalytics,
}