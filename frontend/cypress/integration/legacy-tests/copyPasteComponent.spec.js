it('Should copy and paste component', () => {
  cy.get('.net-element').first().click();
  cy.get('.workspace-scale_input input').type('{ctrl}c');
  cy.get('.workspace-scale_input input').type('{meta}c');
  cy.get('.network-field').click(200, 50);
  cy.get('.workspace-scale_input input').click().clear().type('100 {enter}');


  cy.get('.network-field').click(200, 50);
  cy.get('.network-field').first().trigger('mousemove', { clientX: 200, clientY: 300 });

  cy.get('.workspace-scale_input input').type('{ctrl}v');
  cy.get('.workspace-scale_input input').type('{cmd}v');
  cy.get('.network-field').click(200, 50);
  cy.get('.workspace-scale_input input').clear().type('100{enter}');

  cy.get('.net-element')
    .should(($netEle) => {
      expect($netEle).to.have.length(3);
    })
  
  // remove pasted item
  cy.get('.btn.btn--toolbar.tooltip-wrap').first().click();
  cy.get('.net-element')
    .should(($netEle) => {
      expect($netEle).to.have.length(2);
    })
});