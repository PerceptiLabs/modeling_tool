const kcRoot = Cypress.env('KEYCLOAK_BASE_URL');
const kcRealm = Cypress.env('KEYCLOAK_REALM');
const kcClient = Cypress.env('KEYCLOAK_CLIENT_ID');
const kcRedirectUri = Cypress.env('APP_URL');

Cypress.Commands.add('kcLogin', (username, password) => {
  const loginPageRequest = {
    url: `${kcRoot}/auth/realms/${kcRealm}/protocol/openid-connect/auth`,
    qs: {
      client_id: kcClient,
      redirect_uri: kcRedirectUri,
      state: createUUID(),
      nonce: createUUID(),
      response_mode: 'fragment',
      response_type: 'code',
      scope: 'openid'
    }
  };
  // Open the KC login page, fill in the form with username and password and submit.
  return cy.request(loginPageRequest)
    .then(submitLoginForm);
  ////////////
  function submitLoginForm(response) {
    const _el = document.createElement('html');
    _el.innerHTML = response.body;
    // This should be more strict depending on your login page template.
    const loginForm = _el.getElementsByTagName('form');
    const isAlreadyLoggedIn = !loginForm.length;
    if (isAlreadyLoggedIn) {
      return;
    }
    return cy.request({
      form: true,
      method: 'POST',
      url: loginForm[0].action,
      followRedirect: false,
      body: {
        username: username,
        password: password
      }
    });
  }
  // Copy-pasted code from KC javascript client. It probably doesn't need to be 
  // this complicated but I refused to spend time on figuring that out.
  function createUUID() {
    var s = [];
    var hexDigits = '0123456789abcdef';
    for (var i = 0; i < 36; i++) {
      s[i] = hexDigits.substr(Math.floor(Math.random() * 0x10), 1);
    }
    s[14] = '4';
    s[19] = hexDigits.substr((s[19] & 0x3) | 0x8, 1);
    s[8] = s[13] = s[18] = s[23] = '-';
    var uuid = s.join('');
    return uuid;
  }
});

Cypress.Commands.add('kcLogout', () => {
  return cy.request({
    url: `${kcRoot}/auth/realms/${kcRealm}/protocol/openid-connect/logout`,
    qs: {
      redirect_uri: kcRedirectUri
    }
  });
});