it('Should history navigate forward and backward', () => {
  cy.get('.btn.btn--toolbar.tooltip-wrap').first().click();
  cy.get('.net-element')
    .should(($netEle) => {
      expect($netEle).to.have.length(2);
    })
});