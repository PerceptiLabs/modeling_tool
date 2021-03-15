it('Should create a classification model ', () => {
  cy.get('.left-header-btn-text').contains('Create').click();
  cy.get('.template-item').first().click();
  cy.get('#create-model-btn').click();
  cy.location().should((loc) => {
    expect(loc.pathname).to.eq('/app');
  })
});