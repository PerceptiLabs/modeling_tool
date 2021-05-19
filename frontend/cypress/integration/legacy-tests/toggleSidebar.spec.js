it('Should toggle sidebar', () => {
  cy.get('.page_sidebar').should('be.visible');
  cy.get('[data-testing-target="sidebar-tootle-btn"]').click();
  cy.get('.page_sidebar').should('not.be.visible');
  cy.get('[data-testing-target="sidebar-tootle-btn"]').click();
  cy.get('.page_sidebar').should('be.visible');
});