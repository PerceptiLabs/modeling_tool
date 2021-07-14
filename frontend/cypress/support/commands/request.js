Cypress.Commands.add('ryggRequest', (url, method = 'GET', qs = {}, data = {}) => {
    const request = {
        url: `${Cypress.env('RYGG_URL')}${url}`,
        method,
        qs: {
            ...(qs || {}),
            token: Cypress.env('PL_FILE_SERVING_TOKEN')
        },
        body: data
    };

    return cy.request(request);
});
