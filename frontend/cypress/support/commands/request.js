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

Cypress.Commands.add('kernelRequest', (url, method = 'GET', qs = {}, data = {}) => {
    const request = {
        url: `${Cypress.env('KERNEL_URL')}${url}`,
        method,
        qs,
        body: data
    };

    return cy.request(request);
});
