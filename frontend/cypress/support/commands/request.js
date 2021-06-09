Cypress.Commands.add('ryggRequest', (url, method = 'GET', data = {}) => {
    const request = {
        url: `${Cypress.env('RYGG_URL')}${url}`,
        method,
        body: data
    }
    return cy.request(request);
});

Cypress.Commands.add('fileServerRequest', (url, method = 'GET', qs = {}, data = {}) => {
    const request = {
        url: `${Cypress.env('FILE_SERVER_URL')}${url}`,
        method,
        qs: {
            ...qs,
            token: Cypress.env('PL_FILE_SERVING_TOKEN')
        },
        body: data
    };

    return cy.request(request);
});
