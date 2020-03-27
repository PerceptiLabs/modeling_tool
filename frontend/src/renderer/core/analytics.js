import { isDevelopMode } from '@/core/constants';
import axios from 'axios';

export const hubSpot = (function() {
    let publicMethods = {};

    const addTag = function(input) {
        if (!input) { return; }

        window._hsq = window._hsq || [];
        window._hsq.push(input);
    }

    const getCookieValue = function() {
      return document.cookie.replace(/(?:(?:^|.*;\s*)hubspotutk\s*\=\s*([^;]*).*$)|^.*$/, "$1");
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

    publicMethods.trackUserRegistration = function({email, firstName, lastName, communicationsConsent}) {
        
      let hubspotutkValue = getCookieValue();

      const payload = {
        "submittedAt": (new Date()).getTime(),
        "fields": [
          {
            "name": "email",
            "value": email
          },
          {
            "name": "firstname",
            "value": firstName
          },
          {
            "name": "lastname",
            "value": lastName
          },
        ],
        "context": {
          "hutk": hubspotutkValue, // include this parameter and set it to the hubspotutk cookie value to enable cookie tracking on your submission
          "pageUri": "perceptilabs.com/register",
          "pageName": "User registration"
        },
        "legalConsentOptions": {
          "consent": {
            "consentToProcess": true,
            "text": "By clicking Sign up below, you consent to allow PerceptiLabs to store and process the personal information submitted above to provide you the content requested.",
            "communications": [
              {
                "value": communicationsConsent,
                "subscriptionTypeId": 8790776,
                "text": "I agree to receive other communications from PerceptiLabs."
              }
            ]
          }
        },
        "skipValidation": true
      }
      
      const url = 'https://api.hsforms.com/submissions/v3/integration/submit/7122301/d3fd6e39-4be1-4316-b93b-af60978f2337';
      return axios.post(url, payload)
        .then(response => {
            
        })
        .catch(error => {
          console.error('Error tracking user registration', error);
        });
    }

    return publicMethods;
})();

export const googleAnalytics = (function() {

    let publicMethods = {};

    const addTag = function() {
        window.dataLayer = window.dataLayer || [];
        window.dataLayer.push(arguments);
    }

    publicMethods.setup = function() {
        const gaId = process.env.GOOGLE_ANALYTICS_ID;
        // if (!gaId || isDevelopMode) { return; }
    
        
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

        addTag('set', {'user_id' : userId});
    }

    publicMethods.trackCustomEvent = function(eventName, eventParameters = {}) {
        if (!eventName) { return; }

        addTag('event', eventName, eventParameters);
    }

    return publicMethods;
})();

export default {
    hubSpot,
    googleAnalytics,
}