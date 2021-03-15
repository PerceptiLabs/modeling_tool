it('Should add components to network', () => {
  cy.get('.layer-list-header-label').eq(0).click();
  cy.contains('Local').click();
  cy.get('.network-field').trigger('mousemove', {
    clientX: 670,
    clientY: 441,
    screenX: 670,
    screenY: 545,
    pageX: 670,
    pageY: 441,
  })
  cy.get('.network-field').click(50, 50);

  cy.get('.layer-list-header-label').eq(1).click();
  cy.contains('Reshape').click();
  cy.get('.network-field').trigger('mousemove', {
    clientX: 670,
    clientY: 441,
    screenX: 670,
    screenY: 545,
    pageX: 670,
    pageY: 441,
  })
  cy.get('.network-field').click(250, 50);

  cy.get('.el-type-Data').should('be.visible')
  cy.get('.net-element-process').should('be.visible');
});