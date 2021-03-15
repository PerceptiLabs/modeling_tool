it('Should open and close the code window', () => {
  cy.get('.net-element:eq(0)').click();
  cy.get('.sidebar-setting-head > .btn-menu-bar').contains('Open code').click();
  cy.get('.code-window-header').should('be.visible');
  cy.get('[data-testing-target="code-window-close"]').click();
});