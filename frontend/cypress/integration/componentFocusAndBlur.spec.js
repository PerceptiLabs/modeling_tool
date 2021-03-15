it('Should focus on component and lose when click outside', () => {
  cy.get('.net-element').first().click('center');
  cy.get('.net-element').first().should('have.class', 'net-element--active');
  cy.get('.network-field').click();
  cy.get('.net-element').first().should('not.have.class', 'net-element--active');
});