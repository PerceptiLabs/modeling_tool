
document.addEventListener("DOMContentLoaded", function() {
  let currentPathName = window.location.pathname;
  currentPathName = currentPathName.substring(currentPathName.lastIndexOf('/')+1);
  // auth | authenticate | registration | reset-credentials | first-broker-login

  window.mixpanel.opt_in_tracking();

  switch(currentPathName) {
    case 'auth': {
      // Creating users in HubSpot
      // handleAuthActions();

      // Tracking in MixPanel
      handleAuthStatistics();
      break;
    }
    case 'authenticate': {
      break;
    }
    case 'registration': {
      handleRegistrationActions();
      handleRegistrationStatistics();
      break;
    }
    case 'first-broker-login': {
      handleRegistrationActions();
      break;
    }
    case 'reset-credentials': {
      break;
    }
  }

});

const handleRegistrationActions = function() {
  const termsAndConditionLink = document.getElementById('terms-and-condition-link');
  const termsAndConditionsModalWrapper =  document.getElementById('terms-and-coditions-modal-wrapper');
  const termsAndConditionBackButton = document.getElementById('terms-and-condition-back-button');
  const termsAndConditionCheckbox = document.getElementById('termsAndConditions');
  const registerSubmitBtn = document.getElementById('register-submit-btn');
  const emailInputField = document.getElementById('email');

  termsAndConditionLink.addEventListener('click', function () {
    setTermsAndConditionsModalState(true);
  });
  

  termsAndConditionsModalWrapper.addEventListener('click', function(event) {
    const isRootModalWrapper = event.target.id && event.target.id === 'terms-and-coditions-modal-wrapper';
    if(isRootModalWrapper) {
      setTermsAndConditionsModalState(false);
    }
  })

  termsAndConditionBackButton.addEventListener('click', function() {
    setTermsAndConditionsModalState(false)
  })

  const setTermsAndConditionsModalState = function(modalState) {
    const statValue = modalState ? 'block' : 'none';
    termsAndConditionsModalWrapper.style.display =  statValue;
  }

  termsAndConditionCheckbox.addEventListener('change', function(event) {
    if(event.target.checked) {
      registerSubmitBtn.removeAttribute('disabled');
    } else {
      registerSubmitBtn.setAttribute('disabled', true);
    }
  });


  // DISABLE FORM SUBMISSION TO HUBSPOT
  // registerSubmitBtn.addEventListener('click', function() {
  //   const url = 'https://api.hsforms.com/submissions/v3/integration/submit/7122301/928396cb-6243-44c2-8e46-8394f13c75bf';

  //   const payload = {
  //     "submittedAt": (new Date()).getTime(),
  //     "fields": [
  //       {
  //         "name": "email",
  //         "value": emailInputField.value
  //       }
  //     ],
  //     "context": {
  //       "pageUri": "perceptilabs.com/register",
  //       "pageName": "User registration"
  //     },
  //     "legalConsentOptions": {
  //       "consent": {
  //         "consentToProcess": true,
  //         "text": "By clicking Sign up below, you consent to allow PerceptiLabs to store and process the personal information submitted above to provide you the content requested.",
  //         "communications": [
  //           {
  //             "value": true,
  //             "subscriptionTypeId": 10574130,
  //             "text": "I agree to receive other communications from PerceptiLabs."
  //           }
  //         ]
  //       }
  //     },
  //     "skipValidation": true
  //   }

  //   const xhr = new XMLHttpRequest();
  //   xhr.open('POST', url, true);

  //   xhr.setRequestHeader('Content-Type', 'application/json');

  //   xhr.onreadystatechange = function() {
  //     if(xhr.readyState == 4 && xhr.status == 200) {
  //       console.log(xhr.responseText);
  //     }
  //   }
  //   xhr.send(JSON.stringify(payload));
  // });
}

const handleAuthStatistics = function() {
  const githubLoginButton = document.getElementById('zocial-github');
  const keyCloakLoginButton = document.getElementById('kc-login');

  if (githubLoginButton) {
    githubLoginButton.addEventListener('click', () => {
      window.mixpanel.track('User login', { 'Provider': 'GitHub' });
    });
  }

  if (keyCloakLoginButton) {
    keyCloakLoginButton.addEventListener('click', () => {
      window.mixpanel.track('User login', { 'Provider': 'KeyCloak' });
    });
  }
}

const handleRegistrationStatistics = function() {
  const registrFormEl = document.getElementById('kc-register-form');
  const firstName = document.getElementById('firstName');
  const lastName = document.getElementById('lastName');
  const email = document.getElementById('email');
  const password = document.getElementById('password');
  const passwordConfirm = document.getElementById('password-confirm');
   

  const inputTrackEventList = ['focus', 'blur', 'change'];
  const inputsRegistrationForm = [firstName, lastName, email, password, passwordConfirm];

  inputsRegistrationForm.forEach(element => {
    inputTrackEventList.forEach(eventName => {
      element.addEventListener(eventName, () => {
        window.mixpanel.track('Registration step', {[eventName]: "Input "+ element.name});
      })
    })
  })

  registrFormEl.addEventListener('submit', _ => {
    window.mixpanel.track('User registration', {'Email': email.value});

    // Google Ads conversion tracking
    if (gtag) {
      gtag('event', 'conversion', {'send_to': 'AW-694987597/O4fbCLnJpOcBEM3WsssC'});
    }
  })
}