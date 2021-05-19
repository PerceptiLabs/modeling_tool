it('Should create connection between components', () => {
  cy.get('.output-dot:eq(0)')
    .trigger('mousedown', 3, 3);
  cy.get('.input-dot:eq(0)')
    .trigger('mouseup', 3, 3);
  cy.get('.svg-arrow_line').should('be.visible');

});